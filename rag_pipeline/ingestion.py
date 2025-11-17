from __future__ import annotations

import logging
import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any

import faiss
import numpy as np

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

    - Tries to use SentenceTransformer for embeddings.
    - If that fails (e.g. Torch NotImplementedError on Streamlit Cloud),
      it falls back to a lightweight local embedding (byte-based) so the
      app keeps working without GPU or fancy Torch build.
    """

    def __init__(self, paths: PathsConfig, rag_cfg: RAGConfig):
        self.paths = paths
        self.cfg = rag_cfg

        self.st_model = None
        self.embedding_dim = 768  # fallback dimension

        # Try to load SentenceTransformer, but don't crash if it fails
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore

            logger.info(
                "Trying to load SentenceTransformer model '%s'",
                self.cfg.embedding_model_name,
            )
            self.st_model = SentenceTransformer(self.cfg.embedding_model_name)
            # If we reached here, use its real dimension
            test_emb = self.st_model.encode(["test"], convert_to_numpy=True)
            self.embedding_dim = int(test_emb.shape[1])
            logger.info("SentenceTransformer loaded; embedding dim = %d", self.embedding_dim)
        except Exception as e:
            logger.error(
                "Failed to load SentenceTransformer embedding model; "
                "falling back to simple local embeddings. Error: %s",
                e,
            )
            self.st_model = None

        self.index_path = self.paths.vector_store_dir / "index.faiss"
        self.meta_path = self.paths.vector_store_dir / "chunks.pkl"

    # ----- file reading -----

    def _read_pdf(self, path: Path) -> List[Dict[str, Any]]:
        from pypdf import PdfReader  # local import to keep dependencies modular

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

    # ----- embeddings -----

    def _embed_texts(self, texts: List[str]) -> np.ndarray:
        """
        Embed a list of texts using either SentenceTransformer (if available)
        or a simple byte-based fallback.
        """
        if self.st_model is not None:
            embs = self.st_model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
            return embs.astype("float32")

        # Fallback: simple deterministic embedding
        logger.warning("Using fallback byte-based embeddings (SentenceTransformer unavailable).")
        vectors = []
        for t in texts:
            arr = np.zeros(self.embedding_dim, dtype="float32")
            for i, ch in enumerate(t.encode("utf-8")[: self.embedding_dim]):
                arr[i] = ch / 255.0
            vectors.append(arr)
        return np.vstack(vectors)

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
        embs = self._embed_texts(texts)

        dim = int(embs.shape[1])
        index = faiss.IndexFlatL2(dim)
        index.add(embs)

        # persist
        self.paths.vector_store_dir.mkdir(parents=True, exist_ok=True)
        faiss.write_index(index, str(self.index_path))
        with self.meta_path.open("wb") as f:
            pickle.dump(all_chunks, f)

        logger.info("Ingestion completed: %d chunks indexed", len(all_chunks))
        return len(all_chunks)
