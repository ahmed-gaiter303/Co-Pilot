from __future__ import annotations

import logging
import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

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
    """

    def __init__(self, paths: PathsConfig, rag_cfg: RAGConfig):
        self.paths = paths
        self.cfg = rag_cfg
        self.index_path = self.paths.vector_store_dir / "index.faiss"
        self.meta_path = self.paths.vector_store_dir / "chunks.pkl"
        self.model = SentenceTransformer(self.cfg.embedding_model_name)

        self.index: faiss.Index | None = None
        self.chunks: List[ChunkMetadata] = []

    def load(self) -> bool:
        if not self.index_path.exists() or not self.meta_path.exists():
            logger.warning("Vector store not found. Index or metadata file missing.")
            return False
        self.index = faiss.read_index(str(self.index_path))
        with self.meta_path.open("rb") as f:
            self.chunks = pickle.load(f)
        logger.info("Vector store loaded: %d chunks", len(self.chunks))
        return True

    def is_ready(self) -> bool:
        return self.index is not None and len(self.chunks) > 0

    def search(self, query: str, top_k: int | None = None) -> List[RetrievedChunk]:
        if not self.is_ready():
            logger.warning("Vector store is not ready for search.")
            return []

        if top_k is None:
            top_k = self.cfg.top_k

        q_emb = self.model.encode([query], convert_to_numpy=True)
        q_emb = q_emb.astype("float32")

        distances, indices = self.index.search(q_emb, top_k)
        results: List[RetrievedChunk] = []

        for score, idx in zip(distances[0], indices[0]):
            if idx < 0 or idx >= len(self.chunks):
                continue
            # faiss gives L2 distance; we turn it into pseudo-similarity
            sim = float(max(0.0, 1.0 - score))
            if sim < self.cfg.score_threshold:
                continue
            results.append(RetrievedChunk(metadata=self.chunks[idx], score=sim))

        logger.info("Search for '%s' returned %d hits", query, len(results))
        return results
