# Desktop Assistant

An intelligent document management system with Retrieval-Augmented Generation (RAG) capabilities, featuring hybrid search, Context Enriched Chunking, and real-time folder monitoring. Upload documents, perform semantic search with keyword fusion, and get relevant answers from your document corpus with automatic updates.

## Features
- **Hybrid Search**: Combines semantic similarity, BM25 keyword search, and exact matching with Reciprocal Rank Fusion (RRF)
- **Context Enriched Chunking**: Semantic-aware chunking that respects sentence boundaries and enriches metadata
- **Real-time Folder Monitoring**: Automatic document ingestion with background file system watching
- **Document Ingestion**: Supports PDF, DOC/DOCX, PPT/PPTX, TXT, MD, RTF, and ODT files
- **Semantic Search**: Vector-based search using Qdrant vector database
- **Text Extraction**: Powered by the `unstructured` library
- **Smart Chunking**: Token-aware chunking with semantic boundaries and metadata enrichment
- **Embeddings**: Uses SentenceTransformers for high-quality embeddings
- **FastAPI**: REST API with automatic documentation and comprehensive endpoints
- **Flexible Storage**: Supports both local file storage and Qdrant server modes

## Project Structure
```
DesktopAssistant/
├── app/                    # FastAPI application
│   ├── api/               # API endpoints
│   ├── core/              # Core business logic
│   │   ├── query_service.py # Central orchestration service
│   │   └── exceptions.py   # Custom exceptions
│   ├── models/            # Pydantic models
│   │   ├── entities.py    # SearchResult model
│   │   ├── requests.py    # API request models
│   │   └── responses.py   # API response models
│   ├── config.py          # Configuration settings
│   └── app.py             # FastAPI application entry point
├── storage/               # Storage and retrieval components
│   ├── vector_storage.py  # Qdrant integration
│   ├── embedding_manager.py # Embedding generation
│   ├── document_chunker.py  # Context enriched chunking
│   ├── file_handler.py     # File processing
│   ├── hybrid_searcher.py  # Hybrid search implementation
│   └── pipeline.py        # Ingestion pipeline
├── watchservice/          # Folder monitoring service
│   ├── watcher.py         # File system watcher
│   └── watcherservice.py  # Watcher service management
├── qdrant_storage/        # Local Qdrant data (if using path mode)
└── requirements.txt       # Dependencies
```

## Requirements
- Python 3.10+
- Qdrant (either running as a service on `localhost:6333` or local file-path mode)

## Installation
```bash
# Clone the project
cd DesktopAssistant

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model (optional, for NER)
python -m spacy download en_core_web_sm
```

## Configuration
Settings are defined in `app/config.py` using `pydantic-settings`. You can override via environment variables or a `.env` file in the project root.

Key settings (defaults shown):
- **APP**: `APP_NAME=Desktop Assistant`, `APP_VERSION=1.0.0`
- **API**: `HOST=localhost`, `PORT=8000`, `RELOAD=true`, `LOG_LEVEL=info`
- **Qdrant**: `QDRANT_HOST=localhost`, `QDRANT_PORT=6333`, `QDRANT_PATH=./qdrant_storage`, `COLLECTION_NAME=documents`
- **Embeddings**: `EMBEDDING_MODEL=BAAI/bge-small-en-v1.5`, `VECTOR_SIZE=384`
- **Chunking**: `DEFAULT_CHUNK_SIZE=450`, `DEFAULT_OVERLAP=100`
- **Search**: `TOP_K=5`, `MAX_TOP_K=100`, `SCORE_THRESHOLD=0.0`
- **Hybrid Search**: `SEMANTIC_WEIGHT=0.7`, `KEYWORD_WEIGHT=0.3`, `RRF_K=60`
- **Folder Watcher**: `WATCHER_BATCH_SIZE=5`, `WATCHER_POLL_INTERVAL=30000.0`

## Running the API
Start the FastAPI server:

```bash
# Option 1: Using uvicorn
uvicorn app.app:app --host 0.0.0.0 --port 8000 --reload

# Option 2: Using the module directly
python -m app.app
```

Open the interactive docs:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Core Endpoints
- **GET** `/` – Health message
- **GET** `/health` – Verifies Qdrant connection and collection

### Search & Ingestion
- **POST** `/search` – Semantic vector search
- **POST** `/hybrid-search` – Hybrid search (semantic + BM25 + exact match with RRF)
- **POST** `/search/rebuild-index` – Force rebuild BM25 keyword index
- **POST** `/ingest` – Ingest a directory of files with Context Enriched Chunking

### Collections Management
- **GET** `/collections/info` – Info about current collection
- **POST** `/collections/{collection_name}/create` – Create a collection
- **GET** `/collections/{collection_name}/info` – Info for a specific collection
- **DELETE** `/collections/{collection_name}` – Delete a collection

### Folder Watcher (Real-time Monitoring)
- **POST** `/watcher/start` – Start folder monitoring service
- **POST** `/watcher/stop` – Stop folder monitoring service
- **GET** `/watcher/status` – Get watcher service status
- **POST** `/watcher/folders/add` – Add folder to monitoring
- **POST** `/watcher/folders/remove` – Remove folder from monitoring
- **GET** `/watcher/folders` – List monitored folders
- **POST** `/watcher/folders/batch` – Batch add/remove folders
- **POST** `/watcher/scan` – Force scan of all monitored folders

## Usage Examples

### Ingest Documents
```bash
curl -X POST "http://localhost:8000/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "directory_path": "/path/to/your/documents",
    "skip_existing": true,
    "chunk_size": 400,
    "overlap": 100
  }'
```

### Semantic Search
```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "what is machine learning?",
    "top_k": 5,
    "score_threshold": 0.0
  }'
```

### Hybrid Search
```bash
curl -X POST "http://localhost:8000/hybrid-search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "what is machine learning?",
    "top_k": 5,
    "semantic_weight": 1.0,
    "keyword_weight": 1.0,
    "exact_weight": 2.0
  }'
```

### Folder Monitoring
```bash
# Start the watcher service
curl -X POST "http://localhost:8000/watcher/start"

# Add a folder to monitor
curl -X POST "http://localhost:8000/watcher/folders/add" \
  -H "Content-Type: application/json" \
  -d '{"folder_path": "/path/to/documents"}'

# Check watcher status
curl -X GET "http://localhost:8000/watcher/status"
```

## System Architecture

### Core Components
- **QueryService**: Central orchestration service with lazy loading pattern
- **HybridSearch**: Multi-modal retrieval with RRF fusion
- **VectorStorage**: Qdrant integration with collection management
- **EmbeddingManager**: SentenceTransformers-based embedding generation
- **FolderWatcher**: Real-time file system monitoring service
- **DocumentChunker**: Context-aware chunking with semantic boundaries

### Design Patterns
- **Dependency Injection**: Clean separation of concerns
- **Lazy Loading**: Circular dependency resolution
- **Event-Driven**: Asynchronous file processing
- **Microservice-Ready**: Modular API structure

### Performance Features
- **Embedded Qdrant**: Local storage mode for zero-setup deployment
- **Batch Processing**: Efficient handling of multiple file operations
- **Background Services**: Non-blocking folder monitoring
- **Configurable Weights**: Tunable hybrid search parameters
