from __future__ import annotations

import logging
import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any

import faiss
import numpy as np
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

from app.config import RAGConfig, PathsConfig

logger = logging.getLogger(__name__)


@dataclass
class ChunkMetadata:
    id: str
    content: str
    source: str
    page: int | None
    section: str | None


class IngestionEngine:
    """
    Handles document loading, chunking, embedding, and vector index creation.
    """

    def __init__(self, paths: PathsConfig, rag_cfg: RAGConfig):
        self.paths = paths
        self.cfg = rag_cfg
        self.model = SentenceTransformer(self.cfg.embedding_model_name)
        self.index_path = self.paths.vector_store_dir / "index.faiss"
        self.meta_path = self.paths.vector_store_dir / "chunks.pkl"

    # ----- file reading -----

    def _read_pdf(self, path: Path) -> List[Dict[str, Any]]:
        reader = PdfReader(str(path))
        results = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            results.append({"page": i + 1, "text": text})
        return results

    def _read_text_like(self, path: Path) -> str:
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    # ----- chunking -----

    def _chunk_text(self, text: str, source: str, page: int | None = None) -> List[ChunkMetadata]:
        text = text.replace("\r", "\n")
        text = "\n".join(line.strip() for line in text.splitlines() if line.strip())

        size = self.cfg.chunk_size_chars
        overlap = self.cfg.chunk_overlap_chars

        chunks: List[ChunkMetadata] = []
        start = 0
        idx = 0
        while start < len(text):
            end = start + size
            chunk = text[start:end].strip()
            if chunk:
                chunk_id = f"{source}::p{page or 0}::c{idx}"
                chunks.append(
                    ChunkMetadata(
                        id=chunk_id,
                        content=chunk,
                        source=source,
                        page=page,
                        section=None,
                    )
                )
                idx += 1
            start = end - overlap
        return chunks

    # ----- public API -----

    def ingest_files(self, file_paths: List[Path]) -> int:
        """
        Ingests files, builds FAISS index, and persists both index and metadata.
        Returns number of chunks.
        """
        all_chunks: List[ChunkMetadata] = []

        for path in file_paths:
            if not path.exists():
                logger.warning("File not found during ingestion: %s", path)
                continue

            ext = path.suffix.lower()
            source_name = path.name

            logger.info("Ingesting file: %s", path)

            if ext == ".pdf":
                pages = self._read_pdf(path)
                for page_info in pages:
                    page_chunks = self._chunk_text(
                        page_info["text"],
                        source=source_name,
                        page=page_info["page"],
                    )
                    all_chunks.extend(page_chunks)
            elif ext in {".txt", ".md"}:
                text = self._read_text_like(path)
                all_chunks.extend(self._chunk_text(text, source=source_name))
            else:
                logger.warning("Unsupported file type for ingestion: %s", path.suffix)

        if not all_chunks:
            logger.warning("No chunks produced during ingestion.")
            return 0

        # embeddings
        texts = [c.content for c in all_chunks]
        logger.info("Encoding %d chunks into embeddings", len(texts))
        embs = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        embs = embs.astype("float32")

        dim = embs.shape[1]
        index = faiss.IndexFlatL2(dim)
        index.add(embs)

        # persist
        self.paths.vector_store_dir.mkdir(parents=True, exist_ok=True)
        faiss.write_index(index, str(self.index_path))
        with self.meta_path.open("wb") as f:
            pickle.dump(all_chunks, f)

        logger.info("Ingestion completed: %d chunks indexed", len(all_chunks))
        return len(all_chunks)
