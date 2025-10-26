from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # API Configuration
    openai_api_key: str
    openai_model: str = "gpt-4o"
    embedding_model: str = "text-embedding-ada-002"
    
    # Gemini API Configuration
    gemini_api_key: str
    gemini_model: str = "gemini-2.0-flash"
    gemini_temperature: float = 0.2
    gemini_max_tokens: int = 1200
    
    # Vector Database Configuration
    pinecone_api_key: str
    pinecone_environment: str = "us-west1-gcp-free"
    pinecone_index_name: str = "math-textbooks-free"
    vector_dimension: int = 384  # Free embedding dimension
    
    # Legacy ChromaDB (for fallback)
    chroma_db_path: str = "./chroma_db"
    collection_name: str = "math_textbooks"
    
    # Application Configuration
    app_name: str = "Pearson Math Tutor"
    debug: bool = False
    log_level: str = "INFO"
    
    # Security Configuration
    max_requests_per_minute: int = 60
    max_tokens_per_request: int = 2000
    
    # RAG Configuration
    chunk_size: int = 1000
    chunk_overlap: int = 100
    max_context_chunks: int = 5
    similarity_threshold: float = 0.7
    
    # CORS Configuration
    allowed_origins: list = [
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:3000",
        "http://localhost:3000",
        "http://127.0.0.1:8001",
        "http://localhost:8001",
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        "null",  # For file:// protocol
        "*"  # Allow all origins for development
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()
