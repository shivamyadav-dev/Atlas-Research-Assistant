# Atlas Research Assistant

An AI-powered multi-agent research system built using **LangGraph**, **Google Gemini**, and **Streamlit**.  
This project was developed as part of the **Google × Kaggle 5-Day AI Agents Intensive** Capstone Project.

---

## 🚀 Project Overview

The **Atlas Research Assistant** processes any user question through a structured multi-agent workflow:

1. **Planner Agent** – Breaks down the main question into smaller sub-questions.  
2. **Search Agent** – Runs Google Custom Search (optional) for each sub-question.  
3. **Synthesizer Agent** – Uses Google Gemini to generate a detailed, structured research report.

The system supports both:
- **Search-enabled mode** (Google CSE API keys)
- **LLM-only mode** (Gemini only)


---

## 🧠 Key Features

- Multi-agent workflow built using **LangGraph (StateGraph)**  
- High-quality reasoning and synthesis with **Google Gemini**  
- Optional **Google Search API** integration  
- Clean and interactive **Streamlit UI**  
- Command-line interface support  
- Modular and developer-friendly code structure  

---

## 📂 Project Structure

```
├── agents.py          # Planner, Search, Synthesizer nodes
├── graph.py           # LangGraph workflow definition
├── app.py             # Streamlit frontend
├── main.py            # CLI entry point
├── tools.py           # Search and URL fetch utilities
├── requirements.txt   # Project dependencies
```

---

## 🔧 Installation

```bash
git clone <your-repo-url>
cd <project-folder>
pip install -r requirements.txt
```

---

## 🔑 Environment Variables

Create a `.env` file with the following variables:

```
GOOGLE_API_KEY=your_gemini_api_key
GOOGLE_SEARCH_API_KEY=your_cse_search_key   # optional
GOOGLE_CSE_ID=your_cse_id                   # optional
GOOGLE_MODEL_NAME=gemini-2.0-flash
```

If search keys are missing, the project automatically runs in **LLM-only mode**.

---

## ▶️ Running the Application

### **Streamlit Interface**
```bash
python -m streamlit run app.py
```

### **Command Line**
```bash
python main.py "Your research question here"
```

---

## 🏅 About the Google × Kaggle AI Agents Intensive

This project was built during the **5-Day AI Agents Intensive**, where participants learned:
- Agent architectures  
- LangGraph workflows  
- Google Gemini LLM integrations  
- Real-world agent development  

Participants completing the Capstone Project are eligible for:
- **Kaggle certificate**  
- **Kaggle badge** (coming December 2025)

---

## 🙌 Author

**Shivam Kumar Yadav**  
AI/ML Developer | Generative AI | LLM Engineering | MLOps

---

## ⭐ Support

If you found this project useful:
- ⭐ Star the repository  
- 🔄 Fork it  
- 🛠️ Contribute improvements  
