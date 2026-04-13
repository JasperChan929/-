from pathlib import Path
from typing import List

from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_core.documents import Document

SUPPORTED_EXTENSIONS = {".pdf", ".docx"}


def load_document(file_path: str) -> List[Document]:
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {suffix}")

    if suffix == ".pdf":
        loader = PyPDFLoader(str(path))
        docs = loader.load()
    elif suffix == ".docx":
        loader = Docx2txtLoader(str(path))
        docs = loader.load()
    else:
        raise ValueError(f"Unsupported file type: {suffix}")

    for i, doc in enumerate(docs):
        doc.metadata["source"] = path.name
        doc.metadata["file_path"] = str(path)
        doc.metadata["page_or_chunk"] = i

    return docs