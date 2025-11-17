from __future__ import annotations

import logging
import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import List

import faiss
import numpy as np

from app.config import RAGConfig, PathsConfig
from rag_pipeline.ingestion import ChunkMetadata

logger = logging.getLogger(__name__)


@dataclass
class RetrievedChunk:
    metadata: ChunkMetadata
    score: float


class VectorStore:
    """
    Local FAISS-based vector store with metadata.

    - Tries to use SentenceTransformer for query embeddings.
    - Falls back to the same byte-based embedding used in ingestion
      if the model is not available (to avoid Torch NotImplementedError).
    """

    def __init__(self, paths: PathsConfig, rag_cfg: RAGConfig):
        self.paths = paths
        self.cfg = rag_cfg
        self.index_path = self.paths.vector_store_dir / "index.faiss"
        self.meta_path = self.paths.vector_store_dir / "chunks.pkl"

        self.index: faiss.Index | None = None
        self.chunks: List[ChunkMetadata] = []
        self.embedding_dim: int = 768

        self.st_model = None
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore

            logger.info(
                "Trying to load SentenceTransformer model '%s' for retrieval",
                self.cfg.embedding_model_name,
            )
            self.st_model = SentenceTransformer(self.cfg.embedding_model_name)
        except Exception as e:
            logger.error(
                "Failed to load SentenceTransformer for retrieval; "
                "fallback embeddings will be used. Error: %s",
                e,
            )
            self.st_model = None

    def load(self) -> bool:
        if not self.index_path.exists() or not self.meta_path.exists():
            logger.warning("Vector store not found. Index or metadata file missing.")
            return False
        self.index = faiss.read_index(str(self.index_path))
        self.embedding_dim = int(self.index.d)
        with self.meta_path.open("rb") as f:
            self.chunks = pickle.load(f)
        logger.info("Vector store loaded: %d chunks (dim=%d)", len(self.chunks), self.embedding_dim)
        return True

    def is_ready(self) -> bool:
        return self.index is not None and len(self.chunks) > 0

    def _embed_query(self, query: str) -> np.ndarray:
        if self.st_model is not None:
            emb = self.st_model.encode([query], convert_to_numpy=True)
            return emb.astype("float32")

        logger.warning("Using fallback byte-based embedding for query.")
        dim = self.embedding_dim or 768
        arr = np.zeros(dim, dtype="float32")
        for i, ch in enumerate(query.encode("utf-8")[:dim]):
            arr[i] = ch / 255.0
        return arr.reshape(1, -1)

    def search(self, query: str, top_k: int | None = None) -> List[RetrievedChunk]:
        if not self.is_ready():
            logger.warning("Vector store is not ready for search.")
            return []

        if top_k is None:
            top_k = self.cfg.top_k

        q_emb = self._embed_query(query)

        distances, indices = self.index.search(q_emb, top_k)
        results: List[RetrievedChunk] = []

        for score, idx in zip(distances[0], indices[0]):
            if idx < 0 or idx >= len(self.chunks):
                continue
            # faiss gives L2 distance; turn into pseudo-similarity [0,1]
            sim = float(max(0.0, 1.0 - score))
            if sim < self.cfg.score_threshold:
                continue
            results.append(RetrievedChunk(metadata=self.chunks[idx], score=sim))

        logger.info("Search for '%s' returned %d hits", query, len(results))
        return results
