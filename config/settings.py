from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # FAISS
    faiss_index_path: str = "./data/faiss_index.bin"
    
    # MySQL
    mysql_host: str = "localhost"
    mysql_user: str = "root"
    mysql_password: str = "password"
    mysql_database: str = "rag_db"
    mysql_port: int = 3306
    
    # LLM
    llm_model_name: str = "qwen2:3b"  # TODO: Update based on actual local LLM setup
    llm_temperature: float = 0.7
    llm_max_tokens: int = 512
    llm_base_url: Optional[str] = None  # e.g., "http://localhost:8000/v1" for local LLM API
    
    # Embedding
    embedding_model_name: str = "all-MiniLM-L6-v2"
    embedding_dim: int = 384
    
    # Retrieval
    default_top_k: int = 5

    class Config:
        env_file = ".env"


settings = Settings()
