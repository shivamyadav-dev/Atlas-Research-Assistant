"""Streamlit frontend for Atlas Research Project."""
import os
import sys
import warnings

# Add current directory to path to ensure imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
# Remove 'app.py' if it was incorrectly added to path
if 'app.py' in sys.path:
    sys.path.remove('app.py')
# Add the project directory to Python path
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
# Also add parent directory in case we're in a subdirectory
parent_dir = os.path.dirname(current_dir)
if parent_dir and parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Suppress Pydantic V1 deprecation warning BEFORE any other imports
warnings.filterwarnings("ignore", message=".*Pydantic V1.*", category=UserWarning)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore")  # Suppress all warnings during import

import streamlit as st
from dotenv import load_dotenv

# Import graph after warnings are suppressed
try:
    # Try importing langchain_google_genai first to check if it's available
    try:
        import langchain_google_genai
    except ImportError:
        st.error("❌ **Missing Dependency**")
        st.error("The `langchain-google-genai` package is not installed.")
        st.error("**Solution:** Run the following command in your terminal:")
        st.code(f"{sys.executable} -m pip install langchain-google-genai", language="bash")
        st.error("Or install all dependencies:")
        st.code(f"{sys.executable} -m pip install -r requirements.txt", language="bash")
        st.error(f"**Current Python:** {sys.executable}")
        st.error("**Important:** Make sure Streamlit uses the same Python.")
        st.error("Run: `python -m streamlit run app.py` (not just `streamlit run app.py`)")
        st.stop()
    
    # Now try importing graph
    from graph import graph
except ImportError as e:
    st.error(f"❌ **Failed to import graph module**")
    st.error(f"Error: {e}")
    st.error(f"Python executable: {sys.executable}")
    st.error(f"Current directory: {current_dir}")
    st.error(f"Python path (first 5): {sys.path[:5]}")
    st.error("**Troubleshooting:**")
    st.error("1. Make sure all dependencies are installed: `pip install -r requirements.txt`")
    st.error("2. Check that you're using the correct Python environment")
    st.error("3. Try restarting Streamlit")
    st.stop()
except Exception as e:
    st.error(f"❌ **Error importing graph**")
    st.error(f"Error: {e}")
    import traceback
    with st.expander("Full Error Details"):
        st.code(traceback.format_exc())
    st.stop()

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Atlas Research Assistant",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
    }
    .stButton>button:hover {
        background-color: #1565c0;
    }
    .result-box {
        padding: 1.5rem;
        border-radius: 0.5rem;
        background-color: #f0f2f6;
        border-left: 4px solid #1f77b4;
        margin-top: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🔍 Atlas Research Assistant</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">AI-powered research tool that breaks down complex questions and synthesizes comprehensive reports</p>', unsafe_allow_html=True)

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Check API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        st.success("✅ Google API Key configured")
        st.caption(f"Key: {api_key[:15]}...")
    else:
        st.error("❌ Google API Key not found")
        st.caption("Please set GOOGLE_API_KEY in your .env file")
        st.stop()
    
    # Check search keys
    search_key = os.getenv("GOOGLE_SEARCH_API_KEY")
    cse_id = os.getenv("GOOGLE_CSE_ID")
    
    if search_key and cse_id:
        st.success("✅ Web search enabled")
    else:
        st.info("ℹ️ Running in LLM-only mode")
        st.caption("Web search keys not configured")
    
    st.divider()
    
    # Model selection
    model_name = os.getenv("GOOGLE_MODEL_NAME", "gemini-2.0-flash")
    st.caption(f"Model: {model_name}")
    
    st.divider()
    
    st.markdown("### 📖 How to Use")
    st.markdown("""
    1. Enter your research question in the text area
    2. Click the "Research" button
    3. Wait for the AI to analyze and generate a report
    4. Review the comprehensive report below
    """)
    
    st.divider()
    
    st.markdown("### 💡 Tips")
    st.markdown("""
    - Ask specific, focused questions
    - Break down complex topics into sub-questions
    - The AI will automatically decompose your question
    """)

# Main content area
st.markdown("### 📝 Enter Your Research Question")

# Text input for research question
question = st.text_area(
    "What would you like to research?",
    height=100,
    placeholder="Example: Explain the fan-out/fan-in agent workflow and when to use it",
    help="Enter a detailed research question. The AI will break it down into sub-questions and provide a comprehensive answer."
)

# Research button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    research_button = st.button("🔍 Start Research", type="primary", use_container_width=True)

# Initialize session state
if "research_results" not in st.session_state:
    st.session_state.research_results = None
if "research_question" not in st.session_state:
    st.session_state.research_question = None

# Process research question
if research_button and question:
    if not question.strip():
        st.warning("⚠️ Please enter a research question.")
    else:
        with st.spinner("🔍 Analyzing your question and generating research report..."):
            try:
                # Run the research
                result = graph.invoke({"question": question.strip()})
                final_report = result.get("final_report", "")
                
                # Store in session state
                st.session_state.research_results = final_report
                st.session_state.research_question = question.strip()
                
                st.success("✅ Research completed successfully!")
                
            except Exception as e:
                st.error(f"❌ Error occurred: {str(e)}")
                st.exception(e)

# Display results
if st.session_state.research_results:
    st.markdown("---")
    st.markdown("### 📊 Research Report")
    
    # Display the question
    st.markdown(f"**Research Question:** {st.session_state.research_question}")
    
    st.divider()
    
    # Display the report
    st.markdown(st.session_state.research_results)
    
    # Download button
    st.download_button(
        label="📥 Download Report",
        data=st.session_state.research_results,
        file_name="research_report.txt",
        mime="text/plain"
    )

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; padding: 1rem;'>"
    "Powered by Google Gemini AI | Built with Streamlit"
    "</div>",
    unsafe_allow_html=True
)

# Developer credit — styled and subtle
st.markdown(
    "<div style='text-align: center; margin-top: 0.5rem;'>"
    "<span style='display:inline-block; padding:0.35rem 0.7rem; background:linear-gradient(90deg,#ffffffcc,#f7f9fc);"
    " box-shadow: 0 1px 3px rgba(0,0,0,0.08); border-radius: 999px; color:#444; font-size:0.9rem;'>"
    "Developed by <strong>Shivam Kumar Yadav</strong>"
    "</span>"
    "</div>",
    unsafe_allow_html=True
)

