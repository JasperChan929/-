from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    OPENAI_API_KEY: str
    OPENAI_CHAT_MODEL: str = "gpt-4o-mini"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"

    CHROMA_PERSIST_DIR: str = "./data/chroma"
    RAW_FILE_DIR: str = "./data/raw"
    REGISTRY_DIR: str = "./data/registry"
    REGISTRY_FILE: str = "./data/registry/documents.json"

    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200

    TOP_K_VECTOR: int = 4
    TOP_K_BM25: int = 4
    TOP_K_FINAL: int = 6

    VECTOR_WEIGHT: float = 0.7
    BM25_WEIGHT: float = 0.3

    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()