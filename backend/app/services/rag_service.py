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
    """Pipeline de retrieval LangChain : Chroma (dense, top-k) -> reranking cross-encoder (CPU)."""

    def __init__(self):
        # Embeddings locaux gratuits (CPU-friendly), identiques à l'index existant
        self.embeddings = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"},
        )

        self.client = None
        self.vectorstore = None
        self.retriever = None
        try:
            # Connect to ChromaDB container via HTTP
            self.client = chromadb.HttpClient(
                host=settings.CHROMA_HOST,
                port=settings.CHROMA_PORT,
            )
            self.vectorstore = Chroma(
                client=self.client,
                collection_name=COLLECTION_NAME,
                embedding_function=self.embeddings,
            )
            self.retriever = self._build_retriever()
        except Exception as e:
            print(f"ChromaDB connection error (HTTP): {e}")

    def _build_retriever(self):
        """Retriever dense large (k candidats) + reranker cross-encoder multilingue sur CPU."""
        base_retriever = self.vectorstore.as_retriever(
            search_kwargs={"k": settings.RETRIEVER_K}
        )
        cross_encoder = HuggingFaceCrossEncoder(
            model_name=settings.RERANKER_MODEL,
            model_kwargs={"device": "cpu"},
        )
        reranker = CrossEncoderReranker(model=cross_encoder, top_n=settings.RERANK_TOP_N)
        return ContextualCompressionRetriever(
            base_compressor=reranker,
            base_retriever=base_retriever,
        )

    def index_csv(self, csv_path: str):
        if not self.vectorstore:
            print("ChromaDB client not initialized. Skipping indexing.")
            return

        if not os.path.exists(csv_path):
            print(f"CSV file not found: {csv_path}")
            return

        # Only index if collection is empty
        collection = self.client.get_or_create_collection(name=COLLECTION_NAME)
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
        self.vectorstore.add_documents(documents, ids=ids)
        print(f"Successfully indexed {len(documents)} chunks.")

    def retrieve(self, query_text: str) -> list:
        """Renvoie les Documents les plus pertinents (dense retrieval + reranking)."""
        if not self.retriever:
            return []
        try:
            return self.retriever.invoke(query_text)
        except Exception as e:
            print(f"Retrieval error: {e}")
            return []


# Singleton instance
rag_service = RAGService()
