import warnings
import os

# Suppress Pydantic V1 deprecation warning for Python 3.14+ BEFORE any other imports
warnings.filterwarnings("ignore", message=".*Pydantic V1.*", category=UserWarning)
warnings.filterwarnings("ignore", category=UserWarning)

from typing import Any, Dict, List, cast
from langchain_core.messages import HumanMessage, SystemMessage  # type: ignore
from langchain_google_genai import ChatGoogleGenerativeAI  # type: ignore
from tools import google_search, fetch_url  # type: ignore

# LLM via Google Generative AI (Gemini)
# Default to gemini-2.0-flash which is available and fast
# Other available models: gemini-2.5-flash, gemini-flash-latest, gemini-pro-latest
MODEL_NAME = os.getenv("GOOGLE_MODEL_NAME", "gemini-2.0-flash")


def get_llm() -> ChatGoogleGenerativeAI:
    """Initialize ChatGoogleGenerativeAI with explicit API key."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is required")
    
    # Ensure model name has "models/" prefix for v1beta API
    model_name = MODEL_NAME
    if not model_name.startswith("models/"):
        model_name = f"models/{model_name}"
    
    # Use convert_system_message_to_human=True for better compatibility
    return ChatGoogleGenerativeAI(
        model=model_name, 
        google_api_key=api_key,
        convert_system_message_to_human=True
    )


def _extract_lines(text: str) -> List[str]:
    lines = [l.strip("- ") for l in text.splitlines() if l.strip()]
    # Filter short noise lines
    return [l for l in lines if len(l) > 2]


def planner_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Decompose the user's question into focused sub-questions."""
    question = state.get("question", "").strip()
    if not question:
        return {"subquestions": []}
    llm = get_llm()
    prompt = (
        "You are a research planner. Break the following question into 3-6 focused,\n"
        "non-overlapping sub-questions that would help a search agent retrieve\n"
        "the most relevant information.\n\nQuestion:\n" + question + "\n\n"
        "Return each sub-question as a separate line without numbering."
    )
    resp = get_llm().invoke(prompt)
    text = resp.content if isinstance(resp.content, str) else str(resp.content)
    subqs = _extract_lines(text)
    return {"subquestions": subqs}


def search_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Perform Google search for each sub-question and collect results."""
    subqs: List[str] = state.get("subquestions", [])
    aggregated: List[Dict[str, Any]] = []
    for sq in subqs:
        try:
            hits = cast(Any, google_search).invoke({"query": sq, "num_results": 5})  # langchain tool call
        except Exception as e:
            hits = [{"title": "Error", "link": "", "snippet": str(e)}]
        aggregated.append({"subquestion": sq, "results": hits})
    return {"search_results": aggregated}


def synthesizer_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Synthesize a coherent report from search results."""
    question: str = state.get("question", "")
    search_results: List[Dict[str, Any]] = state.get("search_results", [])
    
    # Check if we have any actual search results
    has_results = False
    if search_results:
        for block in search_results:
            results = block.get("results", [])
            if results and len(results) > 0:
                has_results = True
                break
    
    if not has_results:
        # No search results available - use LLM-only mode
        llm = get_llm()
        sys = SystemMessage(content=(
            "You are a senior research analyst. Answer the question using your internal knowledge. If sources are unavailable, don't fabricate citations."
        ))
        human = HumanMessage(content=(
            f"Main Question:\n{question}\n\nWrite the final report."
        ))
        out = llm.invoke([sys, human])
        final_report = out.content if isinstance(out.content, str) else str(out.content)
        return {"final_report": final_report}

    # Build context text from results
    context_chunks: List[str] = []
    for block in search_results:
        sq = block.get("subquestion", "")
        results = block.get("results", [])
        if results:  # Only include non-empty results
            lines = [f"- {r.get('title', '')}: {r.get('snippet', '')}" for r in results[:5] if r.get('title') or r.get('snippet')]
            if lines:  # Only add chunk if there are actual lines
                chunk = f"Sub-question: {sq}\n" + "\n".join(lines)
                context_chunks.append(chunk)
    
    if not context_chunks:
        # Fallback to LLM-only if no valid context was built
        llm = get_llm()
        sys = SystemMessage(content=(
            "You are a senior research analyst. Answer the question using your internal knowledge. If sources are unavailable, don't fabricate citations."
        ))
        human = HumanMessage(content=(
            f"Main Question:\n{question}\n\nWrite the final report."
        ))
        out = llm.invoke([sys, human])
        final_report = out.content if isinstance(out.content, str) else str(out.content)
        return {"final_report": final_report}
    
    context = "\n\n".join(context_chunks)

    llm = get_llm()
    sys = SystemMessage(content=(
        "You are a senior research analyst. Synthesize a clear, structured report\n"
        "answering the main question using the provided context. Cite URLs where useful.\n"
        "Use concise sections and bullet points when appropriate."
    ))
    human = HumanMessage(content=(
        f"Main Question:\n{question}\n\nContext from searches:\n{context}\n\n"
        "Write the final report."
    ))
    out = llm.invoke([sys, human])
    final_report = out.content if isinstance(out.content, str) else str(out.content)
    return {"final_report": final_report}
