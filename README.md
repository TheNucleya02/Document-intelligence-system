# 📚 PDF Q&A Application  

A powerful **Document Question-Answering System** built with **FastAPI (Backend)** and **Streamlit (Frontend)**.  
Upload your PDFs or DOCX files and interact with them using **Mistral AI** with **AstraDB vector storage**.  

---

## 🚀 Features  

- 📂 **Upload Documents** – Supports **PDF & DOCX** formats  
- 🤖 **AI-Powered Q&A** – Ask questions and get context-aware answers using **Mistral AI**  
- 💾 **Vector Database** – Store and query document embeddings with **AstraDB**  
- 💬 **Conversational Memory** – Keep track of chat history while querying  
- 🎨 **Modern UI** – Clean, simple, and interactive interface with **Streamlit**  
- 🔗 **FastAPI Backend** – Provides REST API endpoints for document operations  
- 🛠 **Extensible** – Easy to add new LLMs or vector stores in the future  

---

## 🛠 Tech Stack  

- **Frontend:** [Streamlit](https://streamlit.io/)  
- **Backend:** [FastAPI](https://fastapi.tiangolo.com/)  
- **Vector DB:** [AstraDB](https://www.datastax.com/astra-db)  
- **Embeddings & LLM:** [Mistral AI](https://mistral.ai/)  
- **Deployment:** Render / Local  

---

## ⚡ Quick Start  

### 1️⃣ Install dependencies
```bash
pip install -r requirements.txt

ASTRA_DB_API_ENDPOINT=your_astra_db_endpoint
ASTRA_DB_APPLICATION_TOKEN=your_astra_db_token
MISTRAL_API_KEY=your_mistral_api_key

python run.py

# Terminal 1 - Backend
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 - Frontend
streamlit run frontend/app.py --server.port 8501

## PROJECT STRUCTURE
.
├── backend/
│   ├── main.py          # FastAPI app
│   ├── routes/          # API routes
│   ├── services/        # Document & QA logic
│
├── frontend/
│   └── app.py           # Streamlit UI
│
├── run.py               # Helper to run backend & frontend
├── requirements.txt     # Dependencies
├── .env                 # Environment variables
└── README.md            # Documentation
