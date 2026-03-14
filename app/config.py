from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App metadata
    app_name: str = "Aura"
    app_version: str = "1.0.0"
    app_description: str = "API for managing and querying Aura embeddings and vectors"

    # API settings
    host: str = "localhost"
    port: int = 8000
    reload: bool = True
    log_level: str = "info"

    # Qdrant settings
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_path: Optional[str] = "./qdrant_storage"
    collection_name: str = "documents"

    # Embedding settings
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    vector_size: int = 384

    # Chunking settings
    default_chunk_size: int = 450
    default_overlap: int = 100
    max_workers: int = 3

    # Search settings
    top_k: int = 5
    max_top_k: int = 100
    score_threshold: float = 0.0

    # Hybrid search weights
    semantic_weight: float = 0.7
    keyword_weight: float = 0.3
    rrf_k: int = 60

    # Folder watcher settings
    WATCHER_BATCH_SIZE: int = 5
    WATCHER_POLL_INTERVAL: float = 30000.0

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
