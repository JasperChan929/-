import requests
import streamlit as st

API_BASE = "http://127.0.0.1:8000/api"

st.set_page_config(page_title="IntelliDocs-RAG", layout="wide")
st.title("📄 IntelliDocs-RAG v2")
st.caption("Hybrid RAG system with PDF/DOCX upload, Chroma, BM25, FastAPI, and Streamlit.")

if "messages" not in st.session_state:
    st.session_state.messages = []


def fetch_documents():
    try:
        resp = requests.get(f"{API_BASE}/documents", timeout=30)
        if resp.ok:
            return resp.json().get("documents", [])
    except Exception:
        pass
    return []


with st.sidebar:
    st.header("Document Management")

    uploaded_files = st.file_uploader(
        "Upload PDF or DOCX files",
        type=["pdf", "docx"],
        accept_multiple_files=True,
    )

    if st.button("Index Uploaded Files"):
        if not uploaded_files:
            st.warning("Please upload at least one file.")
        else:
            for uploaded_file in uploaded_files:
                files = {
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        uploaded_file.type or "application/octet-stream",
                    )
                }
                try:
                    resp = requests.post(f"{API_BASE}/upload", files=files, timeout=120)
                    if resp.ok:
                        data = resp.json()
                        st.success(
                            f"Indexed: {data['file_name']} | doc_id={data['doc_id']} | chunks={data['chunks_indexed']}"
                        )
                    else:
                        st.error(f"Upload failed: {resp.text}")
                except Exception as e:
                    st.error(f"Upload error: {e}")

    st.markdown("---")
    st.subheader("Indexed Documents")

    docs = fetch_documents()
    if docs:
        for doc in docs:
            st.write(f"**{doc['file_name']}**")
            st.caption(f"doc_id: {doc['doc_id']} | chunks: {doc['chunks_indexed']}")
            if st.button(f"Delete {doc['doc_id']}", key=f"delete_{doc['doc_id']}"):
                try:
                    resp = requests.delete(f"{API_BASE}/documents/{doc['doc_id']}", timeout=60)
                    if resp.ok:
                        st.success(f"Deleted: {doc['file_name']}")
                        st.rerun()
                    else:
                        st.error(resp.text)
                except Exception as e:
                    st.error(f"Delete error: {e}")
    else:
        st.info("No documents indexed yet.")

    st.markdown("---")
    if st.button("Reset Knowledge Base"):
        try:
            resp = requests.delete(f"{API_BASE}/reset", timeout=60)
            if resp.ok:
                st.success("Knowledge base reset successfully.")
                st.rerun()
            else:
                st.error(resp.text)
        except Exception as e:
            st.error(f"Reset error: {e}")

    st.markdown("---")
    st.info("Hybrid retrieval = BM25 keyword search + vector similarity search")


for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("citations"):
            st.caption(f"Sources: {msg['citations']}")


user_question = st.chat_input("Ask a question about your uploaded documents...")

if user_question:
    st.session_state.messages.append({"role": "user", "content": user_question})

    with st.chat_message("user"):
        st.markdown(user_question)

    with st.chat_message("assistant"):
        with st.spinner("Retrieving and generating answer..."):
            try:
                resp = requests.post(
                    f"{API_BASE}/ask",
                    json={"question": user_question},
                    timeout=120,
                )
                if resp.ok:
                    data = resp.json()
                    st.markdown(data["answer"])
                    st.caption(f"Sources: {data['citations']}")
                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": data["answer"],
                            "citations": data["citations"],
                        }
                    )
                else:
                    error_text = f"Request failed: {resp.text}"
                    st.error(error_text)
                    st.session_state.messages.append({"role": "assistant", "content": error_text})
            except Exception as e:
                error_text = f"Request error: {e}"
                st.error(error_text)
                st.session_state.messages.append({"role": "assistant", "content": error_text})