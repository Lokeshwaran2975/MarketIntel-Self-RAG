# 📊 MarketIntel-Self-RAG

> **AI-powered Financial RAG Assistant using LangGraph, Hybrid Retrieval (Vector + BM25), CrossEncoder Re-ranking, ChromaDB, and Ollama LLM for accurate financial question answering.**

---

## 🚀 Overview

MarketIntel-Self-RAG is an intelligent financial question-answering system that combines **Retrieval-Augmented Generation (RAG)** with **Hybrid Search**, **CrossEncoder Re-ranking**, and **LangGraph workflows** to deliver accurate answers from financial documents such as:

- 📑 Annual Reports
- 📑 10-K Filings
- 📑 10-Q Filings
- 📑 8-K Reports
- 📑 Earnings Reports

Instead of relying solely on an LLM, the system retrieves the most relevant financial evidence before generating responses, significantly reducing hallucinations and improving factual accuracy.

---

# ✨ Features

- ✅ Hybrid Retrieval (Vector Search + BM25)
- ✅ ChromaDB Vector Database
- ✅ Ollama LLM Integration
- ✅ LangGraph Workflow
- ✅ CrossEncoder Re-ranking
- ✅ Metadata-aware Retrieval
- ✅ Query Understanding
- ✅ Financial Metric Extraction
- ✅ Self-RAG Inspired Retrieval Validation
- ✅ Automatic Context Building
- ✅ Source Attribution
- ✅ Financial Report QA

---

# 🏗 Architecture

```text
                 User Question
                       │
                       ▼
             Query Processing
                       │
                       ▼
          Metadata Extraction
                       │
                       ▼
             Hybrid Retriever
         ┌────────────┴────────────┐
         │                         │
         ▼                         ▼
   Vector Search              BM25 Search
         │                         │
         └────────────┬────────────┘
                      ▼
          Reciprocal Rank Fusion
                      ▼
           Duplicate Removal
                      ▼
         CrossEncoder Re-ranking
                      ▼
           Metadata Ranking
                      ▼
            Context Builder
                      ▼
              LangGraph Agent
         ┌──────────┴──────────┐
         ▼                     ▼
   Retrieval Grader       Query Rewrite
         │                     │
         └──────────┬──────────┘
                    ▼
              Answer Generator
                    ▼
             Final Response
```

---

# 📂 Project Structure

```text
MarketIntel-Self-RAG
│
├── app.py
├── requirements.txt
├── README.md
├── LICENSE
│
├── src
│   ├── agents
│   ├── graph
│   ├── ingestion
│   ├── loaders
│   ├── processing
│   ├── prompts
│   ├── reranker
│   ├── retriever
│   ├── utils
│   └── vectorstore
│
└── data
    ├── annual_reports
    ├── earnings_reports
    ├── sec_filings
    └── news
```

---

# ⚙️ Tech Stack

| Category | Technologies |
|-----------|--------------|
| Language | Python |
| Framework | LangGraph |
| LLM | Ollama (Llama 3.2) |
| Embeddings | Nomic Embed Text |
| Vector DB | ChromaDB |
| Search | BM25 |
| Re-ranking | CrossEncoder (MS MARCO MiniLM) |
| Workflow | LangGraph |
| Document Processing | LangChain |
| Logging | Python Logging |

---

# 🔍 Retrieval Pipeline

1. Query Processing
2. Metadata Extraction
3. Hybrid Search
4. MMR Vector Retrieval
5. BM25 Retrieval
6. Reciprocal Rank Fusion
7. Duplicate Removal
8. CrossEncoder Re-ranking
9. Metadata Ranking
10. Context Building
11. Retrieval Grading
12. Answer Generation

---

# 📊 Example Query

```
What was NVIDIA's net income in 2025?
```

### Example Output

```
Company:
NVIDIA

Fiscal Period:
Year Ended Jan 26, 2025

Metric:
Net Income

Value:
$72,880 million
```

---

# 🚀 Installation

Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/MarketIntel-Self-RAG.git

cd MarketIntel-Self-RAG
```

Create virtual environment

```bash
python -m venv marketintel-env
```

Activate

### Windows

```bash
marketintel-env\Scripts\activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

# 🤖 Install Ollama

Download Ollama

https://ollama.com/download

Pull the required models

```bash
ollama pull llama3.2:3b

ollama pull nomic-embed-text
```

---

# ▶️ Run

```bash
python app.py
```

---

# 📸 Demo

> Add screenshots or GIFs here.

Example:

```
assets/demo.gif
assets/workflow.png
assets/output.png
```

---

# 📈 Future Improvements

- Multi-Agent Financial Analysis
- Self-RAG Feedback Loop
- Multi-Document Reasoning
- Streaming Responses
- Financial Charts
- Web Interface
- Docker Deployment
- Cloud Deployment
- API Support

---

# 👨‍💻 Author

**Lokeshwaran**

Artificial Intelligence & Data Science Engineer

- Python
- Machine Learning
- Deep Learning
- Generative AI
- Retrieval-Augmented Generation (RAG)

---

# ⭐ If you found this project useful

Please consider giving this repository a ⭐ on GitHub.
