from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

from nekpress_dickens_analysis.book_config import load_book_config


def test_package_imports():
    import nekpress_dickens_analysis  # noqa: F401


def _write_minimal_canonical_bundle(root: Path) -> None:
    cfg = load_book_config()
    canon_dir = root / "data" / "canonical"
    canon_dir.mkdir(parents=True, exist_ok=True)

    canon = canon_dir / cfg.canonical_filename
    canon.write_text(
        "THE PICKWICK PAPERS\n\nCHAPTER I. THE PICKWICKIANS\nMr Pickwick at Eatanswill and Rochester.\n\n"
        "CHAPTER II. THE FIRST DAY'S JOURNEY\nSam Weller at an inn in London.\n",
        encoding="utf-8",
    )

    chapters_manifest = {
        "work_id": cfg.work_id,
        "canonical_filename": "canonical.txt",
        "canonical_sha256": "deadbeef",
        "chapter_split_regex": "^CHAPTER\\s+([IVXLCDM]+)\\.",
        "chapter_count": 2,
        "chapters": [
            {
                "index": 1,
                "id": "ch01",
                "numeral": "I",
                "heading": "CHAPTER I. THE PICKWICKIANS",
                "filename": "chapters/01.txt",
                "sha256": "aaa",
                "word_count": 8,
            },
            {
                "index": 2,
                "id": "ch02",
                "numeral": "II",
                "heading": "CHAPTER II. THE FIRST DAY'S JOURNEY",
                "filename": "chapters/02.txt",
                "sha256": "bbb",
                "word_count": 9,
            },
        ],
    }
    (canon_dir / "chapters.json").write_text(json.dumps(chapters_manifest, indent=2) + "\n", encoding="utf-8")

    volume_plan = {
        "work_id": cfg.work_id,
        "canonical_sha256": "deadbeef",
        "chapter_count": 2,
        "planning_basis": {
            "target_story_pages_per_volume": 60,
            "assumed_words_per_story_page": 300,
            "target_words_per_volume": 18000,
        },
        "total_word_count": 17,
        "volume_count": 1,
        "volumes": [
            {
                "volume_id": "vol01",
                "volume_number": 1,
                "start_chapter_index": 1,
                "end_chapter_index": 2,
                "chapter_ids": ["ch01", "ch02"],
                "chapter_numerals": ["I", "II"],
                "chapter_filenames": ["chapters/01.txt", "chapters/02.txt"],
                "total_word_count": 17,
            }
        ],
    }
    (canon_dir / "volume_plan_draft.json").write_text(json.dumps(volume_plan, indent=2) + "\n", encoding="utf-8")


def test_build_analysis_writes_expected_files():
    root = Path(__file__).resolve().parents[1]
    _write_minimal_canonical_bundle(root)

    out_dir = root / "analysis" / "results"
    if out_dir.exists():
        shutil.rmtree(out_dir)

    subprocess.run([sys.executable, "tools/build_analysis.py"], check=True)

    expected = [
        out_dir / "window_metrics.csv",
        out_dir / "keyness_last_vs_first.csv",
        out_dir / "chapter_lengths.csv",
        out_dir / "volume_plan_candidates.json",
    ]
    for p in expected:
        assert p.exists() and p.stat().st_size > 0

    subprocess.run([sys.executable, "tools/write_analysis_sha256.py"], check=True)
    sha = (out_dir / "analysis.sha256").read_text(encoding="utf-8")
    assert "window_metrics.csv" in sha
    assert "keyness_last_vs_first.csv" in sha
    assert "chapter_lengths.csv" in sha
    assert "volume_plan_candidates.json" in sha
