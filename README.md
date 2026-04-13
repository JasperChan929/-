# IntelliDocs-RAG v2

A portfolio-ready hybrid document question-answering system built with **LangChain**, **Chroma**, **FastAPI**, and **Streamlit**.

## Overview

IntelliDocs-RAG is a document QA system that supports **PDF/DOCX upload**, **semantic indexing**, **hybrid retrieval**, and **grounded answer generation**.  
It is designed as a portfolio project for showcasing practical RAG engineering skills.

## Features

- Upload and index **PDF** / **DOCX** documents
- Chunk documents and store embeddings in **Chroma**
- Use **hybrid retrieval**:
  - **BM25 keyword matching**
  - **Vector similarity search**
- Grounded QA with retrieved document chunks
- Document registry and metadata tracking
- List indexed documents
- Delete a single document from the knowledge base
- Reset the entire knowledge base
- FastAPI backend
- Streamlit frontend
- Simple evaluation script
- Docker support

## Tech Stack

- **LangChain**
- **Chroma**
- **FastAPI**
- **Streamlit**
- **OpenAI API**
- **BM25 / rank_bm25**

## Project Structure

```bash
intellidocs-rag/
├─ app/
├─ frontend/
├─ scripts/
├─ tests/
├─ data/
├─ sample_eval/
├─ Dockerfile
├─ docker-compose.yml
├─ requirements.txt
└─ README.md