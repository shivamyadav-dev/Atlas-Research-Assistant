import os
import sys
import warnings
from dotenv import load_dotenv
from graph import graph  # type: ignore

# Suppress Pydantic V1 deprecation warning for Python 3.14+
warnings.filterwarnings("ignore", message=".*Pydantic V1.*", category=UserWarning)


def run(question: str) -> str:
    result = graph.invoke({"question": question})
    return result.get("final_report", "")


if __name__ == "__main__":
    load_dotenv()
    if len(sys.argv) >= 2:
        q = " ".join(sys.argv[1:])
    else:
        q = input("Enter your research question: ").strip()
    if not os.getenv("GOOGLE_API_KEY"):
        print("ERROR: Missing GOOGLE_API_KEY in .env")
        print("Please set GOOGLE_API_KEY in your .env file or environment variables.")
        sys.exit(1)
    # Search keys are optional - project works with just GOOGLE_API_KEY
    if not os.getenv("GOOGLE_SEARCH_API_KEY") or not os.getenv("GOOGLE_CSE_ID"):
        print("INFO: Running in LLM-only mode (search keys not provided).")
        print("To enable web search, set GOOGLE_SEARCH_API_KEY and GOOGLE_CSE_ID in .env")
    out = run(q)
    print("\n===== Final Report =====\n")
    print(out)
