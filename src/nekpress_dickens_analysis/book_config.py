from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, List, Optional


@dataclass(frozen=True)
class ReposConfig:
    ingest: str
    analysis: str
    apparatus_public: Optional[str] = None


@dataclass(frozen=True)
class AnalysisTargets:
    chapter_manifest: str
    target_volume_count_min: int
    target_volume_count_max: int


@dataclass(frozen=True)
class BookConfig:
    root: Path
    work_id: str
    canonical_filename: str
    canonical_heading_markers: List[str]
    repos: ReposConfig
    analysis: AnalysisTargets

    @property
    def canonical_path(self) -> Path:
        return self.root / "data" / "canonical" / self.canonical_filename

    @property
    def chapters_manifest_path(self) -> Path:
        return self.root / self.analysis.chapter_manifest

    @property
    def ingest_volume_plan_draft_path(self) -> Path:
        return self.root / "data" / "canonical" / "volume_plan_draft.json"


def _repo_root() -> Path:
    # src/nekpress_dickens_analysis/book_config.py -> repo root is 3 parents up
    return Path(__file__).resolve().parents[2]


def load_book_config(path: Optional[str] = None) -> BookConfig:
    """Load deterministic per-book configuration from data/book.json."""
    root = _repo_root()
    cfg_path = Path(path) if path else (root / "data" / "book.json")
    if not cfg_path.exists():
        raise FileNotFoundError(f"Missing book config: {cfg_path}")

    raw: dict[str, Any] = json.loads(cfg_path.read_text(encoding="utf-8"))

    def req_str(obj: dict[str, Any], key: str) -> str:
        v = obj.get(key)
        if not isinstance(v, str) or not v.strip():
            raise ValueError(f"data/book.json: '{key}' must be a non-empty string")
        return v.strip()

    def req_list_str(obj: dict[str, Any], key: str) -> List[str]:
        v = obj.get(key)
        if not isinstance(v, list) or not all(isinstance(x, str) and x.strip() for x in v):
            raise ValueError(f"data/book.json: '{key}' must be a list of non-empty strings")
        return [x.strip() for x in v]

    def req_int(obj: dict[str, Any], key: str) -> int:
        v = obj.get(key)
        if not isinstance(v, int):
            raise ValueError(f"data/book.json: '{key}' must be an int")
        return v

    repos_raw = raw.get("repos", {})
    if not isinstance(repos_raw, dict):
        raise ValueError("data/book.json: 'repos' must be an object")

    repos = ReposConfig(
        ingest=req_str(repos_raw, "ingest"),
        analysis=req_str(repos_raw, "analysis"),
        apparatus_public=repos_raw.get("apparatus_public") if isinstance(repos_raw.get("apparatus_public"), str) else None,
    )

    analysis_raw = raw.get("analysis", {})
    if not isinstance(analysis_raw, dict):
        raise ValueError("data/book.json: 'analysis' must be an object")

    analysis = AnalysisTargets(
        chapter_manifest=req_str(analysis_raw, "chapter_manifest"),
        target_volume_count_min=req_int(analysis_raw, "target_volume_count_min"),
        target_volume_count_max=req_int(analysis_raw, "target_volume_count_max"),
    )

    return BookConfig(
        root=root,
        work_id=req_str(raw, "work_id"),
        canonical_filename=req_str(raw, "canonical_filename"),
        canonical_heading_markers=req_list_str(raw, "canonical_heading_markers"),
        repos=repos,
        analysis=analysis,
    )
