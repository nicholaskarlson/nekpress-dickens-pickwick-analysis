from __future__ import annotations

from nekpress_dickens_analysis.nlp.chapter_lengths import build_rows_from_manifest
from nekpress_dickens_analysis.nlp.volume_plan import build_candidates


def test_build_rows_from_manifest_accumulates_running_total():
    manifest = {
        "chapters": [
            {"index": 1, "id": "ch01", "numeral": "I", "heading": "CHAPTER I", "filename": "chapters/01.txt", "sha256": "aaa", "word_count": 10},
            {"index": 2, "id": "ch02", "numeral": "II", "heading": "CHAPTER II", "filename": "chapters/02.txt", "sha256": "bbb", "word_count": 20},
        ]
    }
    rows = build_rows_from_manifest(manifest)
    assert rows[0]["running_word_count"] == 10
    assert rows[1]["running_word_count"] == 30


def test_build_candidates_marks_volume_count_outside_target_range():
    ingest_plan = {
        "work_id": "pickwick_papers",
        "canonical_sha256": "deadbeef",
        "volume_count": 17,
        "volumes": [{"volume_id": "vol01"}],
        "planning_basis": {"target_words_per_volume": 18000},
    }
    candidates = build_candidates(ingest_plan, target_min=9, target_max=12)
    assert candidates["observed_volume_count"] == 17
    assert candidates["within_target_range"] is False
