# Voice of Customer AI (VOC AI)

An AI-powered customer feedback intelligence platform built with Streamlit, SQLite, and Groq LLMs. This application ingests raw customer reviews, support logs, or survey responses, runs parallelized batch analysis to classify sentiment, category, pain points, and business impact, and outputs actionable insights, buyer personas, and a professional executive PDF report.

---

## 🚀 Key Features

- **📂 Multi-Format File Ingest**: Supports CSV, Excel (`.xlsx`, `.xls`), and plain text (`.txt`) files, with intelligent column mapping for custom datasets.
- **⚡ Parallelized LLM Pipeline**: Uses `ThreadPoolExecutor` to run concurrent analysis batches via the Groq API (`llama-3.3-70b-versatile` or `mixtral-8x7b-32768`), maximizing throughput.
- **📊 Interactive Analytics Dashboard**:
  - **Net Sentiment Index (NSI)** and distribution charts.
  - **Thematic Classification**: Automatically groups feedback into Product Quality, Pricing, User Experience, Support, Performance, and Feature Requests.
  - **Opportunity Discovery Engine**: A scatter plot quadrant analysis that maps **Opportunity Score** against **Business Impact** to highlight quick-wins and high-priority fixes.
- **👥 AI Customer Personas**: Generates 2-3 data-driven target user personas summarizing their common demographics, motivations, recurring complaints, and core needs.
- **🔍 Feedback Explorer**: Search, filter, and drill down into individual reviews by sentiment, category, or search keywords.
- **📄 Customizable Executive PDF Reports**: Edit AI-generated summaries and recommendations on-screen, then export them to a professional PDF document with page-decorations, summary tables, and branding using ReportLab.
- **💾 Local SQLite Caching**: All runs, classifications, and report records are stored locally for fast retrieval.

---

## 🛠️ Project Structure

The project code is organized as follows:

- **[app.py](file:///Users/siddharth/Downloads/Voice%20of%20Customer%20AI/app.py)**: The main Streamlit web interface and page router.
- **[database.py](file:///Users/siddharth/Downloads/Voice%20of%20Customer%20AI/database.py)**: SQLite database schema initialization, insertion, and query functions.
- **[llm.py](file:///Users/siddharth/Downloads/Voice%20of%20Customer%20AI/llm.py)**: Groq API client interface, structured prompts, batching mechanisms, and concurrent processing.
- **[models.py](file:///Users/siddharth/Downloads/Voice%20of%20Customer%20AI/models.py)**: Pydantic schemas validating structured JSON outputs from LLMs.
- **[report_generator.py](file:///Users/siddharth/Downloads/Voice%20of%20Customer%20AI/report_generator.py)**: Dynamic PDF compiler using ReportLab with custom headers, tables, and pagination.
- **[utils.py](file:///Users/siddharth/Downloads/Voice%20of%20Customer%20AI/utils.py)**: Helper functions for cleaning texts, parsing files, and calculating statistics.
- **[requirements.txt](file:///Users/siddharth/Downloads/Voice%20of%20Customer%20AI/requirements.txt)**: List of Python packages required for the project.

---

## 📦 Installation & Setup

### Prerequisites

Ensure you have Python 3.10 or higher installed.

### 1. Clone & Navigate
```bash
git clone https://github.com/Siddharth-Dangi/Voice-of-Customer-AI.git
cd Voice-of-Customer-AI
```

### 2. Configure Virtual Environment & Install Dependencies
Create a Python virtual environment and install the required libraries:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Add Environment Variables (Optional)
Create a `.env` file in the root directory to store your Groq API key:
```env
GROQ_API_KEY=gsk_your_actual_groq_api_key_here
```
*Note: You can also input your Groq API Key directly in the sidebar of the Streamlit application.*

---

## 🏃 Running the Application

Always run the app using the virtual environment python/streamlit:

```bash
# If virtual environment is activated:
streamlit run app.py

# Alternatively, run directly:
.venv/bin/streamlit run app.py
```

Open your browser and navigate to the local address displayed in the terminal (usually `http://localhost:8501`).

---

## 🛠️ Technology Stack

- **Frontend Framework**: Streamlit
- **Data Wrangling**: Pandas, OpenPyXL (Excel import)
- **Charts & Visuals**: Plotly Express
- **AI/LLM Engine**: Groq API
- **JSON Validation**: Pydantic v2
- **Database**: SQLite3
- **Document Generation**: ReportLab
