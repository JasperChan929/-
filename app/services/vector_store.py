from langchain_chroma import Chroma

from app.core.config import settings
from app.services.embeddings import get_embeddings


def get_vector_store() -> Chroma:
    return Chroma(
        collection_name="intellidocs",
        embedding_function=get_embeddings(),
        persist_directory=settings.CHROMA_PERSIST_DIR,
    )