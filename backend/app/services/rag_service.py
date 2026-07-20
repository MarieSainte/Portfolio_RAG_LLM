import logging
import os

import chromadb
import pandas as pd
from langchain.retrievers.document_compressors import CrossEncoderReranker
from langchain_chroma import Chroma
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import settings
from app.services.lexical_index import LexicalIndex

logger = logging.getLogger(__name__)

COLLECTION_NAME = "experience_jordan"


class RAGService:
    """Pipeline de retrieval hybride : dense (Chroma) + lexical (SQLite FTS5) -> reranking cross-encoder.

    Deux sources de candidats complémentaires :
    - dense (embeddings) : proximité sémantique, robuste aux reformulations ;
    - lexical (BM25/FTS5) : correspondance exacte de mots-clés (technos, acronymes).
    Leurs candidats sont fusionnés (dédupliqués), puis reclassés par un cross-encoder
    multilingue (CPU) qui ne garde que les meilleurs contextes.

    Initialisation paresseuse : les modèles ML et la connexion ChromaDB ne sont
    chargés qu'au premier usage réel (pas à l'import), ce qui garde le démarrage
    et les tests rapides.
    """

    def __init__(self):
        self._embeddings = None
        self._client = None
        self._vectorstore = None
        self._dense_retriever = None
        self._reranker = None
        self.lexical_index = LexicalIndex()

    @property
    def embeddings(self):
        # Embeddings locaux gratuits (CPU-friendly), identiques à l'index existant
        if self._embeddings is None:
            self._embeddings = HuggingFaceEmbeddings(
                model_name=settings.EMBEDDING_MODEL,
                model_kwargs={"device": "cpu"},
            )
        return self._embeddings

    @property
    def vectorstore(self):
        if self._vectorstore is None:
            try:
                self._client = chromadb.HttpClient(
                    host=settings.CHROMA_HOST,
                    port=settings.CHROMA_PORT,
                )
                self._vectorstore = Chroma(
                    client=self._client,
                    collection_name=COLLECTION_NAME,
                    embedding_function=self.embeddings,
                )
            except Exception:
                logger.exception("ChromaDB connection error (HTTP)")
                self._client = None
                self._vectorstore = None
        return self._vectorstore

    @property
    def retriever(self):
        """Retriever dense (k candidats). None si ChromaDB est inaccessible."""
        if self._dense_retriever is None:
            vs = self.vectorstore
            if vs is None:
                return None
            self._dense_retriever = vs.as_retriever(search_kwargs={"k": settings.RETRIEVER_K})
        return self._dense_retriever

    @property
    def reranker(self):
        """Reranker cross-encoder multilingue (CPU), partagé dense + lexical."""
        if self._reranker is None:
            cross_encoder = HuggingFaceCrossEncoder(
                model_name=settings.RERANKER_MODEL,
                model_kwargs={"device": "cpu"},
            )
            self._reranker = CrossEncoderReranker(model=cross_encoder, top_n=settings.RERANK_TOP_N)
        return self._reranker

    def _build_chunks(self, csv_path: str) -> tuple[list[Document], list[str]]:
        """Découpe le CSV en chunks -> (documents, ids). Liste vide si le fichier manque."""
        if not os.path.exists(csv_path):
            logger.warning("CSV file not found", extra={"context": {"path": csv_path}})
            return [], []

        df = pd.read_csv(csv_path)
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
        )

        documents: list[Document] = []
        ids: list[str] = []
        for idx, row in df.iterrows():
            project_id = str(row.get("id", idx))
            description = "" if pd.isna(row.get("description")) else str(row["description"])
            link = "" if pd.isna(row.get("link")) else str(row["link"])
            doc_type = "" if pd.isna(row.get("type")) else str(row["type"])

            for i, chunk in enumerate(splitter.split_text(description)):
                documents.append(
                    Document(
                        page_content=chunk,
                        metadata={
                            "project_id": project_id,
                            "link": link,
                            "chunk_index": i,
                            "type": doc_type,
                        },
                    )
                )
                ids.append(f"{project_id}_chunk_{i}")
        return documents, ids

    def index_csv(self, csv_path: str):
        documents, ids = self._build_chunks(csv_path)
        if not documents:
            logger.warning("no documents to index")
            return

        # Index lexical FTS5 : reconstruit à chaque appel (léger), indépendamment de
        # l'état de ChromaDB, pour rester cohérent avec le dense index.
        self.lexical_index.build(
            [
                {
                    "doc_id": doc_id,
                    "content": doc.page_content,
                    "project_id": doc.metadata["project_id"],
                    "link": doc.metadata["link"],
                    "type": doc.metadata["type"],
                    "chunk_index": doc.metadata["chunk_index"],
                }
                for doc, doc_id in zip(documents, ids, strict=True)
            ]
        )

        # Index dense (Chroma) : indexé une seule fois (skip si la collection est déjà peuplée).
        if self.vectorstore is None:
            logger.warning("ChromaDB client not initialized, skipping dense indexing")
            return
        collection = self._client.get_or_create_collection(name=COLLECTION_NAME)
        if collection.count() > 0:
            logger.info(
                "collection already populated, skipping dense indexing",
                extra={"context": {"count": collection.count()}},
            )
            return

        self._vectorstore.add_documents(documents, ids=ids)
        logger.info(
            "indexing complete",
            extra={
                "context": {
                    "chunks": len(documents),
                    "chunk_size": settings.CHUNK_SIZE,
                    "chunk_overlap": settings.CHUNK_OVERLAP,
                }
            },
        )

    def _dense_candidates(self, query_text: str) -> list[Document]:
        retriever = self.retriever
        if retriever is None:
            return []
        try:
            return retriever.invoke(query_text)
        except Exception:
            logger.exception("dense retrieval error")
            return []

    def retrieve(self, query_text: str) -> list:
        """Retrieval hybride : fusion dense + lexical, puis reranking cross-encoder."""
        dense_docs = self._dense_candidates(query_text)
        lexical_docs = self.lexical_index.search(query_text, settings.LEXICAL_K)

        # Fusion + déduplication par contenu (un chunk peut sortir des deux sources).
        merged: dict[str, Document] = {}
        for doc in [*dense_docs, *lexical_docs]:
            merged.setdefault(doc.page_content, doc)
        candidates = list(merged.values())
        if not candidates:
            return []

        try:
            return list(self.reranker.compress_documents(candidates, query_text))
        except Exception:
            logger.exception("reranking error")
            # Repli : renvoyer les candidats fusionnés bornés à top_n, sans reranking.
            return candidates[: settings.RERANK_TOP_N]


# Singleton instance
rag_service = RAGService()
