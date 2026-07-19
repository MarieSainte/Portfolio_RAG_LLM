import os

import chromadb
import pandas as pd
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CrossEncoderReranker
from langchain_chroma import Chroma
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import settings

COLLECTION_NAME = "experience_jordan"


class RAGService:
    """Pipeline de retrieval LangChain : Chroma (dense, top-k) -> reranking cross-encoder (CPU).

    Initialisation paresseuse : les modèles ML et la connexion ChromaDB ne sont
    chargés qu'au premier usage réel (pas à l'import), ce qui garde le démarrage
    et les tests rapides.
    """

    def __init__(self):
        self._embeddings = None
        self._client = None
        self._vectorstore = None
        self._retriever = None

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
            except Exception as e:
                print(f"ChromaDB connection error (HTTP): {e}")
                self._client = None
                self._vectorstore = None
        return self._vectorstore

    @property
    def retriever(self):
        """Retriever dense large (k candidats) + reranker cross-encoder multilingue (CPU)."""
        if self._retriever is None:
            vs = self.vectorstore
            if vs is None:
                return None
            base_retriever = vs.as_retriever(search_kwargs={"k": settings.RETRIEVER_K})
            cross_encoder = HuggingFaceCrossEncoder(
                model_name=settings.RERANKER_MODEL,
                model_kwargs={"device": "cpu"},
            )
            reranker = CrossEncoderReranker(model=cross_encoder, top_n=settings.RERANK_TOP_N)
            self._retriever = ContextualCompressionRetriever(
                base_compressor=reranker,
                base_retriever=base_retriever,
            )
        return self._retriever

    def index_csv(self, csv_path: str):
        if self.vectorstore is None:
            print("ChromaDB client not initialized. Skipping indexing.")
            return

        if not os.path.exists(csv_path):
            print(f"CSV file not found: {csv_path}")
            return

        # Only index if collection is empty
        collection = self._client.get_or_create_collection(name=COLLECTION_NAME)
        if collection.count() > 0:
            print(f"ChromaDB collection already contains {collection.count()} entries. Skipping initial indexing.")
            return

        print(f"Starting indexing from {csv_path}...")
        df = pd.read_csv(csv_path)

        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

        documents = []
        ids = []
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

        if not documents:
            print("No documents to index.")
            return

        print(f"Indexing {len(documents)} chunks from {len(df)} projects...")
        self._vectorstore.add_documents(documents, ids=ids)
        print(f"Successfully indexed {len(documents)} chunks.")

    def retrieve(self, query_text: str) -> list:
        """Renvoie les Documents les plus pertinents (dense retrieval + reranking)."""
        retriever = self.retriever
        if not retriever:
            return []
        try:
            return retriever.invoke(query_text)
        except Exception as e:
            print(f"Retrieval error: {e}")
            return []


# Singleton instance
rag_service = RAGService()
