from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.logging import configure_logging

configure_logging()

app = FastAPI(
    title="IntelliDocs-RAG API",
    version="2.0.0",
    description="Hybrid document QA system with LangChain + Chroma + FastAPI + Streamlit",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")