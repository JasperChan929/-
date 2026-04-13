from typing import List

from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage

from app.services.embeddings import get_chat_model
from app.services.retriever import HybridRetriever

SYSTEM_PROMPT = """你是一个严谨的文档问答助手。

规则：
1. 你必须只根据给定上下文回答问题。
2. 如果上下文不足，请明确说：“我无法从已上传文档中确认这个问题的答案”。
3. 不要编造事实，不要扩展未在文档中出现的信息。
4. 回答应清晰、简洁、结构化。
5. 回答最后附上简短引用来源说明。"""


def format_context(docs: List[Document]) -> str:
    blocks = []
    for idx, doc in enumerate(docs, start=1):
        source = doc.metadata.get("source", "unknown")
        chunk_id = doc.metadata.get("chunk_id", "n/a")
        page_or_chunk = doc.metadata.get("page_or_chunk", "n/a")
        text = doc.page_content.strip()
        blocks.append(
            f"[Context {idx}] source={source}, page_or_chunk={page_or_chunk}, chunk_id={chunk_id}\n{text}"
        )
    return "\n\n".join(blocks)


def ask_question(query: str) -> dict:
    retriever = HybridRetriever()
    docs = retriever.retrieve(query)

    if not docs:
        return {
            "answer": "当前知识库为空，或没有检索到相关文档内容。请先上传 PDF/DOCX 文档。",
            "citations": [],
            "retrieved_count": 0,
        }

    context = format_context(docs)
    llm = get_chat_model()

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(
            content=(
                f"问题：{query}\n\n"
                f"上下文如下：\n{context}\n\n"
                f"请严格根据上下文回答，并给出简短的引用说明。"
            )
        ),
    ]
    response = llm.invoke(messages)

    citations = []
    for doc in docs:
        citations.append(
            {
                "doc_id": doc.metadata.get("doc_id"),
                "source": doc.metadata.get("source"),
                "chunk_id": doc.metadata.get("chunk_id"),
                "page_or_chunk": doc.metadata.get("page_or_chunk"),
            }
        )

    return {
        "answer": response.content,
        "citations": citations,
        "retrieved_count": len(docs),
    }