from typing import Any, Dict, List
from pydantic import BaseModel


class UploadResponse(BaseModel):
    doc_id: str
    file_name: str
    documents_loaded: int
    chunks_indexed: int


class QAResponse(BaseModel):
    answer: str
    citations: List[Dict[str, Any]]
    retrieved_count: int