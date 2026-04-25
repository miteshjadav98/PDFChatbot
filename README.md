# PDF RAG Chatbot

A full-stack Retrieval-Augmented Generation (RAG) chatbot application that allows users to upload PDF documents and ask questions about their content.

## Features

- Upload PDF documents
- Ask questions about the uploaded content
- AI-powered answers using Azure OpenAI GPT-4.1
- Local vector storage with FAISS
- Support for multiple PDFs
- Page number tracking in sources
- Clean web interface with Streamlit

## Tech Stack

- **Backend**: FastAPI
- **Frontend**: Streamlit
- **LLM**: Azure OpenAI GPT-4.1 via LangChain
- **Embeddings**: HuggingFace sentence-transformers (all-MiniLM-L6-v2)
- **Vector Store**: FAISS (local, persisted)
- **Document Loader**: PyPDFLoader

## Setup

1. Clone or download the project files.

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your Azure OpenAI credentials in `.env`:
   ```
   AZURE_OPENAI_API_KEY=your_key
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_DEPLOYMENT=gpt-4.1
   AZURE_OPENAI_API_VERSION=2024-02-15-preview
   ```

## Running the Application

1. Start the FastAPI backend:
   ```bash
   cd backend
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. In a new terminal, start the Streamlit frontend:
   ```bash
   cd frontend
   streamlit run app.py
   ```

3. Open your browser to `http://localhost:8501` for the chat interface.

## API Endpoints

- `POST /upload`: Upload a PDF file
- `GET /ask?q=question`: Ask a question
- `GET /health`: Health check

## Example API Calls

Upload a PDF:
```bash
curl -X POST "http://localhost:8000/upload" -F "file=@document.pdf"
```

Ask a question:
```bash
curl "http://localhost:8000/ask?q=What is the main topic of the document?"
```

## Project Structure

```
rag-chatbot/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── rag/
│   │   ├── pipeline.py      # RAG pipeline using LCEL
│   │   ├── embeddings.py    # HuggingFace embeddings
│   │   ├── vectorstore.py   # FAISS vector store management
│   │   ├── llm.py           # Azure OpenAI setup
│   │   └── config.py        # Configuration
│   ├── models/
│   │   └── schemas.py       # Pydantic models
│   └── services/
│       └── rag_service.py   # RAG service layer
├── frontend/
│   └── app.py               # Streamlit application
├── faiss_index/             # Persisted FAISS index
├── .env                     # Environment variables
├── requirements.txt         # Python dependencies
└── README.md                # This file
```