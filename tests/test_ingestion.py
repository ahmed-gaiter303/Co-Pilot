# tests/test_ingestion.py
from pathlib import Path

from app.config import load_config
from rag_pipeline.ingestion import IngestionEngine


def test_ingestion_runs_on_sample(tmp_path: Path):
    cfg = load_config()
    sample = tmp_path / "sample.txt"
    sample.write_text("This is a small test document about pricing and support.", encoding="utf-8")
    cfg.paths.vector_store_dir = tmp_path / "vs"
    engine = IngestionEngine(cfg.paths, cfg.rag)
    n_chunks = engine.ingest_files([sample])
    assert n_chunks > 0
