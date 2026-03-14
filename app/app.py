from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
from typing import List

from app.config import settings
from app.models.requests import (
    QueryRequest, IngestRequest, HybridSearchRequest,
    WatchFolderRequest, WatcherBatchRequest
)
from app.models.responses import (
    QueryResponse, IngestResponse, HybridSearchResponse,
    CreateCollectionResponse, DeleteCollectionResponse
)
from app.core.query_service import QueryService
from storage.vector_storage import VectorStorage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Aura API",
    description="API for managing and querying Aura embeddings and vectors.",
    version=settings.app_version
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the query service
query_service = QueryService()


# ── Health Endpoints ──

@app.get("/", tags=["Health"])
async def root():
    return {"message": "Document Query API is running", "status": "healthy"}


@app.get("/health", tags=["Health"])
async def health_check():
    try:
        collections = query_service.vector_storage.client.get_collections()
        collection_exists = any(
            col.name == query_service.vector_storage.collection_name
            for col in collections.collections
        )
        return {
            "status": "healthy",
            "qdrant_connected": True,
            "collection_exists": collection_exists,
            "collection_name": query_service.vector_storage.collection_name,
            "embedding_model": query_service.embedding_manager.embedding_model
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


# ── Search Endpoints ──

@app.post("/search", response_model=QueryResponse, tags=["Search"])
async def search_documents(request: QueryRequest):
    """Perform semantic vector search across ingested documents."""
    return query_service.search(request)


@app.post("/hybrid-search", response_model=HybridSearchResponse, tags=["Search"])
async def hybrid_search(request: HybridSearchRequest):
    """Perform hybrid search combining semantic, keyword (BM25), and exact match with RRF fusion."""
    return query_service.hybrid_search(request)


@app.post("/search/rebuild-index", tags=["Search"])
async def rebuild_keyword_index():
    """Force rebuild of the BM25 keyword index."""
    return query_service.rebuild_keyword_index()


@app.get("/flashcards", response_model=QueryResponse, tags=["Search"])
async def get_flashcards(limit: int = 20):
    """Get random document chunks for flashcard review."""
    import time
    start = time.monotonic()
    results = query_service.get_random_chunks(limit=limit)
    end = time.monotonic()
    return QueryResponse(
        query="flashcards",
        results=results,
        total_results=len(results),
        processing_time_ms=round((end - start) * 1000, 2)
    )

# ── Ingestion Endpoints ──

@app.post("/ingest", response_model=IngestResponse, tags=["Ingestion"])
async def ingest_documents(request: IngestRequest):
    """Ingest documents from a directory with context-enriched chunking."""
    return query_service.ingest(request)


# ── Collection Management Endpoints ──

@app.get("/collections/info", tags=["Collections"])
async def get_collection_info():
    try:
        return query_service.vector_storage.get_collection_info()
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Collection not found: {str(e)}")


@app.post("/collections/{collection_name}/create", response_model=CreateCollectionResponse, tags=["Collections"])
async def create_collection(collection_name: str):
    try:
        temp_storage = VectorStorage(
            host=query_service.vector_storage.host,
            port=query_service.vector_storage.port,
            path=query_service.vector_storage.path,
            collection_name=collection_name,
            vector_size=settings.vector_size
        )
        return CreateCollectionResponse(
            message=f"Collection '{collection_name}' created successfully",
            collection_name=collection_name,
            created=True,
            status="success"
        )
    except Exception as e:
        logger.error(f"Error creating collection {collection_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create collection: {str(e)}")


@app.get("/collections/{collection_name}/info", tags=["Collections"])
async def get_collection_details(collection_name: str):
    try:
        temp_storage = VectorStorage(
            host=query_service.vector_storage.host,
            port=query_service.vector_storage.port,
            path=query_service.vector_storage.path,
            collection_name=collection_name
        )
        return temp_storage.get_collection_info()
    except Exception as e:
        logger.error(f"Error getting collection info for {collection_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get collection info: {str(e)}")


@app.delete("/collections/{collection_name}", response_model=DeleteCollectionResponse, tags=["Collections"])
async def delete_collection(collection_name: str):
    try:
        temp_storage = VectorStorage(
            host=query_service.vector_storage.host,
            port=query_service.vector_storage.port,
            path=query_service.vector_storage.path,
            collection_name=collection_name
        )
        deleted = temp_storage.delete_collection()
        return DeleteCollectionResponse(
            message=f"Collection '{collection_name}' deleted successfully." if deleted
                    else f"Collection '{collection_name}' does not exist.",
            collection_name=collection_name,
            deleted=deleted,
            status="success" if deleted else "not_found"
        )
    except Exception as e:
        logger.error(f"Error deleting collection: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting collection: {str(e)}")


# ── Folder Watcher Endpoints ──

@app.post("/watcher/start", tags=["Watcher"])
async def start_watcher():
    """Start the folder monitoring service."""
    return query_service.start_folder_watching()


@app.post("/watcher/stop", tags=["Watcher"])
async def stop_watcher():
    """Stop the folder monitoring service."""
    return query_service.stop_folder_watching()


@app.get("/watcher/status", tags=["Watcher"])
async def watcher_status():
    """Get the current status of the folder watcher."""
    return query_service.get_folder_watcher_status()


@app.post("/watcher/folders/add", tags=["Watcher"])
async def add_watch_folder(request: WatchFolderRequest):
    """Add a folder to the monitoring list."""
    return query_service.add_watch_folder(
        folder_path=request.folder_path,
        allowed_extensions=request.allowed_extensions,
        recursive=request.recursive,
        auto_ingest=request.auto_ingest
    )


@app.post("/watcher/folders/remove", tags=["Watcher"])
async def remove_watch_folder(request: WatchFolderRequest):
    """Remove a folder from the monitoring list."""
    return query_service.remove_watch_folder(folder_path=request.folder_path)


@app.get("/watcher/folders", tags=["Watcher"])
async def list_watched_folders():
    """List all currently monitored folders."""
    return query_service.get_watched_folders()


@app.post("/watcher/folders/batch", tags=["Watcher"])
async def batch_manage_folders(request: WatcherBatchRequest):
    """Batch add/remove folders from monitoring."""
    results = {"added": [], "removed": [], "errors": []}

    if request.add_folders:
        for folder in request.add_folders:
            try:
                query_service.add_watch_folder(folder_path=folder)
                results["added"].append(folder)
            except Exception as e:
                results["errors"].append({"folder": folder, "error": str(e)})

    if request.remove_folders:
        for folder in request.remove_folders:
            try:
                query_service.remove_watch_folder(folder_path=folder)
                results["removed"].append(folder)
            except Exception as e:
                results["errors"].append({"folder": folder, "error": str(e)})

    return results


@app.post("/watcher/scan", tags=["Watcher"])
async def force_scan():
    """Force scan all monitored folders for changes."""
    watched = query_service.get_watched_folders()
    scan_results = []

    for folder in watched:
        try:
            result = query_service.ingest(IngestRequest(
                directory_path=folder['path'],
                skip_existing=True,
                chunk_size=settings.default_chunk_size,
                overlap=settings.default_overlap,
            ))
            scan_results.append({
                "folder": folder['path'],
                "files_processed": result.files_processed,
                "total_chunks": result.total_chunks
            })
        except Exception as e:
            scan_results.append({
                "folder": folder['path'],
                "error": str(e)
            })

    return {"message": "Scan complete", "results": scan_results}


if __name__ == "__main__":
    uvicorn.run(
        "app.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
