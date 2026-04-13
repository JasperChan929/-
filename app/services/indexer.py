import os
import uuid
from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import settings
from app.services.loaders import load_document
from app.services.registry import (
    add_document_record,
    delete_document_record,
    get_document_record,
    list_documents,
    reset_registry,
)
from app.services.vector_store import get_vector_store


def split_documents(documents: List[Document], doc_id: str) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
    )
    chunks = splitter.split_documents(documents)

    for idx, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = idx
        chunk.metadata["doc_id"] = doc_id

    return chunks


def ingest_file(file_path: str) -> dict:
    docs = load_document(file_path)
    doc_id = str(uuid.uuid4())
    chunks = split_documents(docs, doc_id=doc_id)

    vector_store = get_vector_store()
    ids = [str(uuid.uuid4()) for _ in chunks]
    vector_store.add_documents(documents=chunks, ids=ids)

    add_document_record(
        {
            "doc_id": doc_id,
            "file_name": os.path.basename(file_path),
            "file_path": file_path,
            "documents_loaded": len(docs),
            "chunks_indexed": len(chunks),
        }
    )

    return {
        "doc_id": doc_id,
        "file_name": os.path.basename(file_path),
        "documents_loaded": len(docs),
        "chunks_indexed": len(chunks),
    }


def delete_document_by_id(doc_id: str) -> dict:
    record = get_document_record(doc_id)
    if not record:
        return {"deleted": False, "doc_id": doc_id}

    vector_store = get_vector_store()

    # 删除 Chroma 中属于该 doc_id 的向量
    collection = vector_store._collection
    results = collection.get(where={"doc_id": doc_id})
    ids = results.get("ids", [])
    if ids:
        collection.delete(ids=ids)

    # 删除本地原文件
    file_path = record.get("file_path")
    if file_path and os.path.exists(file_path):
        os.remove(file_path)

    delete_document_record(doc_id)

    return {
        "deleted": True,
        "doc_id": doc_id,
        "file_name": record.get("file_name"),
    }


def reset_knowledge_base() -> dict:
    docs = list_documents()
    for item in docs:
        file_path = item.get("file_path")
        if file_path and os.path.exists(file_path):
            os.remove(file_path)

    vector_store = get_vector_store()
    collection = vector_store._collection
    all_items = collection.get()
    ids = all_items.get("ids", [])
    if ids:
        collection.delete(ids=ids)

    reset_registry()

    return {"reset": True, "deleted_documents": len(docs)}