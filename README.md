# Aura Document Intelligence

A premium, open-source Retrieval-Augmented Generation (RAG) system with a stunning Next.js frontend and a powerful FastAPI backend. 

Aura allows you to drop any document (PDF, DOCX, TXT, etc.) into a folder, and it will instantly process, chunk, and embed the content. You can then use the breathtaking web interface to perform hybrid searches or generate flashcards to study your own documents.

## Features

- **Next.js Interface**: Premium UI featuring glassmorphism, dynamic video backgrounds, and 3D flipping flashcards powered by Tailwind CSS.
- **Hybrid Search Engine**: Combines semantic similarity (Qdrant), BM25 keyword search, and exact matching with Reciprocal Rank Fusion (RRF) for unparalleled accuracy.
- **Context Enriched Chunking**: Intelligent NLP document splitting that respects sentence boundaries and extracts named entities using `spaCy` and `NLTK`.
- **Real-Time Folder Monitoring**: Automatically watches your local directories and instantly ingests new, modified, or deleted files.
- **Study Mode**: Automatically generates random 3D flashcards from your ingested documents to help you learn and memorize your own data.
- **Embedded Vector Database**: Uses Qdrant in local file-path mode. No Docker or external servers required!

## Project Architecture

```
Aura/
├── app/                    # FastAPI Backend
│   ├── api/               # API routes
│   ├── core/              # Query Service & orchestration
│   ├── models/            # Pydantic schemas
│   └── config.py          # Configuration settings
├── frontend/               # Next.js Frontend
│   ├── app/               # App Router pages (Dashboard, Landing)
│   ├── components/        # React components (Navbar, Flashcards)
│   └── globals.css        # Premium Tailwind styling
├── storage/                # ML Pipeline
│   ├── vector_storage.py  # Qdrant integration
│   ├── embedding_manager.py # SentenceTransformers integration
│   ├── document_chunker.py  # Context-enriched chunking
│   ├── hybrid_searcher.py  # BM25 + Exact + Semantic Fusion
│   └── pipeline.py        # Master ingestion pipeline
└── watchservice/           # Folder Watchdog Service
```

## Quickstart Guide

Aura requires Python 3.10+ and Node.js 18+.

### 1. Start the Backend (FastAPI + Qdrant)

Open your terminal, navigate to the project root, and run:

```bash
# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install heavy ML dependencies
pip install -r requirements.txt

# Download required NLP models (first run only)
python -m spacy download en_core_web_sm

# Start the API server
uvicorn app.app:app --host 0.0.0.0 --port 8000 --reload
```
*Note: The first time you run the server, it will download the BAAI embedding model (~150MB).*

### 2. Start the Frontend (Next.js)

Open a **second terminal window**, navigate to the `frontend` directory:

```bash
cd frontend

# Install Node dependencies
npm install

# Start the beautiful development server
npm run dev
```

### 3. Open the Dashboard!
Visit **[http://localhost:3000](http://localhost:3000)** in your browser to experience Aura.

---

## Configuration & API Reference

Aura is highly configurable via environment variables or the `app/config.py` file.

- **FastAPI Swagger Docs**: Available at `http://localhost:8000/docs` when the backend is running.
- **Vector Storage**: Qdrant data is persisted locally in the `./qdrant_storage/` folder.
- **Embedding Model**: Defaults to `BAAI/bge-small-en-v1.5` (dimension 384).

### Key API Endpoints
- `POST /ingest` - Ingest a folder of documents
- `POST /hybrid-search` - Search with Semantic + BM25 + RRF
- `GET /flashcards` - Retrieve random document chunks for studying
- `POST /watcher/start` - Begin watching local folders for changes

## License
This project is open-source and free to use for personal or educational purposes.
