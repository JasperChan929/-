import os
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.core.config import settings
from app.schemas.request import QuestionRequest
from app.services.indexer import ingest_file, delete_document_by_id, reset_knowledge_base
from app.services.qa_chain import ask_question
from app.services.registry import list_documents

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok", "version": "2.0.0"}


@router.get("/documents")
def get_documents():
    return {"documents": list_documents()}


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    suffix = Path(file.filename).suffix.lower()
    if suffix not in {".pdf", ".docx"}:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX are supported.")

    os.makedirs(settings.RAW_FILE_DIR, exist_ok=True)
    save_path = os.path.join(settings.RAW_FILE_DIR, file.filename)

    with open(save_path, "wb") as f:
        content = await file.read()
        f.write(content)

    try:
        result = ingest_file(save_path)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to ingest file: {e}")


@router.post("/ask")
def ask_doc_question(request: QuestionRequest):
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        return ask_question(question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to answer question: {e}")


@router.delete("/documents/{doc_id}")
def delete_document(doc_id: str):
    try:
        result = delete_document_by_id(doc_id)
        if not result["deleted"]:
            raise HTTPException(status_code=404, detail="Document not found.")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {e}")


@router.delete("/reset")
def reset_all_documents():
    try:
        return reset_knowledge_base()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reset knowledge base: {e}")