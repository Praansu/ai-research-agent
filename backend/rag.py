"""Vector store for document retrieval (RAG)."""

from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

CHROMA_DIR = Path("chroma_db")
COLLECTION_NAME = "agent_docs"
MODEL_NAME = "all-MiniLM-L6-v2"


class VectorStore:
    """Embeddings + similarity search over indexed documents."""

    def __init__(self, persist_dir: str | Path = CHROMA_DIR):
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(exist_ok=True)
        self.client = chromadb.PersistentClient(str(self.persist_dir))
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
        self.model = SentenceTransformer(MODEL_NAME)

    def add_document(self, doc_id: str, chunks: list[dict]) -> int:
        texts = [c["text"] for c in chunks]
        metadatas = [
            {"doc_id": doc_id, "page_num": c.get("page_num", 0), "source": c.get("source", doc_id)}
            for c in chunks
        ]
        ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
        embeddings = self.model.encode(texts, show_progress_bar=False).tolist()
        self.collection.add(embeddings=embeddings, documents=texts, metadatas=metadatas, ids=ids)
        return len(chunks)

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        query_embedding = self.model.encode(query).tolist()
        results = self.collection.query(query_embeddings=[query_embedding], n_results=top_k)
        chunks = []
        if results["documents"]:
            for i, doc in enumerate(results["documents"][0]):
                meta = results["metadatas"][0][i]
                chunks.append({
                    "text": doc,
                    "page_num": meta.get("page_num", 0),
                    "source": meta.get("source", ""),
                    "score": results["distances"][0][i] if results.get("distances") else 0,
                })
        return chunks

    def count(self) -> int:
        return self.collection.count()

    def delete_document(self, doc_id: str) -> None:
        self.collection.delete(where={"doc_id": doc_id})
