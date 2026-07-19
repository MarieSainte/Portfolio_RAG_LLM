import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    PROJECT_NAME: str = "Chatbot Backend (Mistral AI + LangChain)"
    MISTRAL_API_KEY: str = os.getenv("MISTRAL_API_KEY")
    MISTRAL_MODEL: str = os.getenv("MISTRAL_MODEL", "mistral-medium-latest")
    CORS_ORIGINS: list = ["http://localhost:4200", "http://localhost:8080"]
    CHROMA_HOST: str = os.getenv("CHROMA_HOST", "chromadb")
    CHROMA_PORT: int = int(os.getenv("CHROMA_PORT", 8000))

    # Rate limiting de l'endpoint /chat (protège les crédits Mistral)
    CHAT_RATE_LIMIT: str = os.getenv("CHAT_RATE_LIMIT", "10/minute")

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # RAG
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    # Cross-encoder multilingue (corpus FR), léger et rapide sur CPU
    RERANKER_MODEL: str = os.getenv("RERANKER_MODEL", "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1")
    RETRIEVER_K: int = int(os.getenv("RETRIEVER_K", 10))  # candidats denses avant reranking
    RERANK_TOP_N: int = int(os.getenv("RERANK_TOP_N", 5))  # contextes gardés après reranking


settings = Settings()
