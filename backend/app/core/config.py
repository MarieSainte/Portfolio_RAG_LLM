from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# Peuple os.environ depuis .env (utile aux modules qui lisent os.getenv directement,
# ex. variables LangSmith consommées par LangChain).
load_dotenv()


class Settings(BaseSettings):
    # Chaque champ est renseigné automatiquement depuis la variable d'environnement
    # du même nom (sinon la valeur par défaut ci-dessous s'applique).
    PROJECT_NAME: str = "Chatbot Backend (Mistral AI + LangChain)"
    MISTRAL_API_KEY: str | None = None
    MISTRAL_MODEL: str = "mistral-medium-latest"
    CORS_ORIGINS: list[str] = ["http://localhost:4200", "http://localhost:8080"]
    CHROMA_HOST: str = "chromadb"
    CHROMA_PORT: int = 8000

    # Rate limiting de l'endpoint /chat (protège les crédits Mistral)
    CHAT_RATE_LIMIT: str = "10/minute"

    # Logging
    LOG_LEVEL: str = "INFO"

    # RAG
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    # Cross-encoder multilingue (corpus FR), léger et rapide sur CPU
    RERANKER_MODEL: str = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"
    RETRIEVER_K: int = 4  # candidats denses (Chroma) avant reranking (mode non adaptatif)
    LEXICAL_K: int = (
        4  # candidats lexicaux (SQLite FTS5, BM25) avant reranking (mode non adaptatif)
    )
    RERANK_TOP_N: int = 2  # contextes gardés après reranking (mode non adaptatif)
    # Retrieval adaptatif : le nombre de contextes s'ajuste à la longueur de la question.
    # Question courte -> peu de contextes (précis) ; question longue -> plus (synthèse).
    ADAPTIVE_RETRIEVAL: bool = True
    RERANK_TOP_N_MIN: int = 3  # contextes gardés pour une question courte
    RERANK_TOP_N_MAX: int = 5  # contextes gardés pour une question longue
    QUERY_SHORT_WORDS: int = 6  # <= ce nombre de mots -> TOP_N_MIN
    QUERY_LONG_WORDS: int = 18  # >= ce nombre de mots -> TOP_N_MAX
    RETRIEVER_K_FACTOR: int = 3  # candidats (dense & lexical) = top_n * facteur avant reranking
    # Découpage des documents avant indexation. Configurable par variable d'env
    # (CHUNK_SIZE / CHUNK_OVERLAP) pour expérimenter différentes tailles de chunk.
    # NB : changer ces valeurs n'a d'effet que sur un index reconstruit (collection vide).
    CHUNK_SIZE: int = 3000
    CHUNK_OVERLAP: int = 200

    # Journalisation des interactions chat dans SQLite (table + index FTS5 recherchable).
    # Chemin relatif au WORKDIR (/app) ; monter un volume dessus en prod pour la persistance.
    INTERACTIONS_DB_PATH: str = "data/interactions.db"
    # Jeton protégeant l'endpoint d'administration /admin/interactions.
    # Laissé vide -> endpoint désactivé (404). Défini -> requiert l'en-tête X-Admin-Token.
    ADMIN_TOKEN: str | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
