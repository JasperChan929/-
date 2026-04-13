from collections import defaultdict
from typing import List, Tuple

from langchain_core.documents import Document
from langchain_community.retrievers import BM25Retriever

from app.core.config import settings
from app.services.vector_store import get_vector_store


class HybridRetriever:
    def __init__(self):
        self.vector_store = get_vector_store()

    def _get_all_docs_for_bm25(self) -> List[Document]:
        data = self.vector_store.get()
        documents = data.get("documents", [])
        metadatas = data.get("metadatas", [])

        docs = []
        for content, metadata in zip(documents, metadatas):
            docs.append(Document(page_content=content, metadata=metadata or {}))
        return docs

    def _vector_search(self, query: str) -> List[Tuple[Document, float]]:
        return self.vector_store.similarity_search_with_relevance_scores(
            query=query,
            k=settings.TOP_K_VECTOR,
        )

    def _bm25_search(self, query: str) -> List[Document]:
        all_docs = self._get_all_docs_for_bm25()
        if not all_docs:
            return []

        bm25 = BM25Retriever.from_documents(all_docs)
        bm25.k = settings.TOP_K_BM25
        return bm25.invoke(query)

    def retrieve(self, query: str) -> List[Document]:
        score_map = defaultdict(float)
        doc_map = {}

        vector_results = self._vector_search(query)
        for rank, (doc, score) in enumerate(vector_results, start=1):
            key = self._doc_key(doc)
            doc_map[key] = doc
            score_map[key] += settings.VECTOR_WEIGHT * float(score) + (1.0 / rank)

        bm25_results = self._bm25_search(query)
        for rank, doc in enumerate(bm25_results, start=1):
            key = self._doc_key(doc)
            doc_map[key] = doc
            score_map[key] += settings.BM25_WEIGHT * (1.0 / rank)

        ranked = sorted(score_map.items(), key=lambda x: x[1], reverse=True)
        final_docs = [doc_map[key] for key, _ in ranked[: settings.TOP_K_FINAL]]
        return final_docs

    @staticmethod
    def _doc_key(doc: Document) -> str:
        source = doc.metadata.get("source", "unknown")
        chunk_id = doc.metadata.get("chunk_id", "none")
        doc_id = doc.metadata.get("doc_id", "none")
        return f"{doc_id}::{source}::{chunk_id}"