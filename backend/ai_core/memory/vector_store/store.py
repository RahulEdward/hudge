"""ChromaDB-backed vector store for semantic search across agent memory."""

import os
import uuid
from typing import List, Dict, Any, Optional
from loguru import logger

_store = None


class VectorStore:
    """Wrapper around ChromaDB for storing and retrieving embeddings."""

    def __init__(self, persist_dir: str = "database/vector_store"):
        self.persist_dir = persist_dir
        os.makedirs(persist_dir, exist_ok=True)
        self._client = None
        self._collections: Dict[str, Any] = {}

    def _get_client(self):
        if self._client is None:
            try:
                import chromadb
                from chromadb.config import Settings
                self._client = chromadb.PersistentClient(
                    path=self.persist_dir,
                    settings=Settings(anonymized_telemetry=False),
                )
                logger.info(f"ChromaDB client initialized at {self.persist_dir}")
            except ImportError:
                logger.warning("chromadb not installed — vector store unavailable")
                return None
        return self._client

    def _get_collection(self, name: str):
        if name not in self._collections:
            client = self._get_client()
            if client is None:
                return None
            self._collections[name] = client.get_or_create_collection(
                name=name,
                metadata={"hnsw:space": "cosine"},
            )
        return self._collections[name]

    async def add_documents(
        self,
        collection_name: str,
        documents: List[str],
        metadatas: Optional[List[Dict]] = None,
        ids: Optional[List[str]] = None,
    ) -> List[str]:
        """Add documents to a named collection."""
        collection = self._get_collection(collection_name)
        if collection is None:
            return []

        if ids is None:
            ids = [str(uuid.uuid4()) for _ in documents]
        if metadatas is None:
            metadatas = [{} for _ in documents]

        try:
            collection.add(documents=documents, metadatas=metadatas, ids=ids)
            logger.debug(f"Added {len(documents)} docs to '{collection_name}'")
        except Exception as e:
            logger.error(f"Vector store add failed: {e}")
        return ids

    async def search(
        self,
        collection_name: str,
        query: str,
        n_results: int = 5,
        where: Optional[Dict] = None,
    ) -> List[Dict[str, Any]]:
        """Semantic search in a named collection."""
        collection = self._get_collection(collection_name)
        if collection is None:
            return []

        try:
            kwargs: Dict[str, Any] = {"query_texts": [query], "n_results": n_results}
            if where:
                kwargs["where"] = where
            results = collection.query(**kwargs)
            out = []
            for i, doc in enumerate(results["documents"][0]):
                out.append({
                    "id": results["ids"][0][i],
                    "document": doc,
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "distance": results["distances"][0][i] if results.get("distances") else None,
                })
            return out
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []

    async def delete(self, collection_name: str, ids: List[str]):
        """Delete documents by ID."""
        collection = self._get_collection(collection_name)
        if collection is None:
            return
        try:
            collection.delete(ids=ids)
        except Exception as e:
            logger.error(f"Vector delete failed: {e}")

    async def count(self, collection_name: str) -> int:
        collection = self._get_collection(collection_name)
        if collection is None:
            return 0
        return collection.count()


def get_vector_store() -> VectorStore:
    global _store
    if _store is None:
        _store = VectorStore()
    return _store
