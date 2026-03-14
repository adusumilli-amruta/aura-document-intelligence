from typing import Optional, Dict, Any
from pydantic import BaseModel


class SearchResult(BaseModel):
    chunk_id: str = ""
    chunk_text: str = ""
    file_name: str = ""
    file_path: str = ""
    file_type: str = ""
    chunk_index: int = 0
    total_chunks: int = 0
    score: float = 0.0
    semantic_score: float = 0.0
    keyword_score: float = 0.0
    exact_match_score: float = 0.0
    rerank_score: float = 0.0
    final_score: float = 0.0
    metadata: Dict[str, Any] = {}
