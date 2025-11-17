from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Literal


BASE_DIR = Path(__file__).resolve().parent.parent


@dataclass
class PathsConfig:
    data_dir: Path = BASE_DIR / "data"
    uploads_dir: Path = BASE_DIR / "data" / "uploads"
    vector_store_dir: Path = BASE_DIR / "data" / "vector_store"
    leads_csv: Path = BASE_DIR / "data" / "leads.csv"

    def ensure(self) -> None:
        self.data_dir.mkdir(exist_ok=True, parents=True)
        self.uploads_dir.mkdir(exist_ok=True, parents=True)
        self.vector_store_dir.mkdir(exist_ok=True, parents=True)


@dataclass
class LLMConfig:
    provider: str = os.getenv("LLM_PROVIDER", "dummy")  # "openai", "dummy", etc.
    model_name: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
    api_key: str | None = os.getenv("LLM_API_KEY")  # or taken from st.secrets


@dataclass
class RAGConfig:
    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    top_k: int = 5
    score_threshold: float = 0.35  # filter low-similarity chunks
    chunk_size_chars: int = 1200
    chunk_overlap_chars: int = 250


@dataclass
class AppConfig:
    paths: PathsConfig
    llm: LLMConfig
    rag: RAGConfig
    niches: List[str]
    default_niche: str
    themes: List[Literal["Dark", "Light"]]
    default_theme: Literal["Dark", "Light"]


def load_config() -> AppConfig:
    paths = PathsConfig()
    paths.ensure()

    llm = LLMConfig()
    rag = RAGConfig()

    niches = ["Gyms & Fitness Studios", "Clinics & Healthcare", "Online Courses", "Restaurants & Cafes"]
    themes: List[Literal["Dark", "Light"]] = ["Dark", "Light"]

    return AppConfig(
        paths=paths,
        llm=llm,
        rag=rag,
        niches=niches,
        default_niche=niches[0],
        themes=themes,
        default_theme="Dark",
    )
