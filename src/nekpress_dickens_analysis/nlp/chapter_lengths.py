from __future__ import annotations

import csv
import json
from pathlib import Path

from nekpress_dickens_analysis.book_config import load_book_config


RESULT_NAME = "chapter_lengths.csv"


def build_rows_from_manifest(manifest: dict) -> list[dict]:
    chapters = manifest.get("chapters", [])
    if not isinstance(chapters, list) or not chapters:
        raise ValueError("Manifest must contain a non-empty 'chapters' list")

    rows: list[dict] = []
    running = 0
    for ch in chapters:
        words = int(ch["word_count"])
        running += words
        rows.append(
            {
                "index": int(ch["index"]),
                "id": ch["id"],
                "numeral": ch["numeral"],
                "heading": ch["heading"],
                "filename": ch["filename"],
                "sha256": ch["sha256"],
                "word_count": words,
                "running_word_count": running,
            }
        )
    return rows


def write_chapter_lengths_csv(results_dir: Path, manifest: dict) -> Path:
    rows = build_rows_from_manifest(manifest)
    out_path = results_dir / RESULT_NAME
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "index",
                "id",
                "numeral",
                "heading",
                "filename",
                "sha256",
                "word_count",
                "running_word_count",
            ],
        )
        w.writeheader()
        for row in rows:
            w.writerow(row)
    return out_path


def main() -> None:
    cfg = load_book_config()
    manifest_path = cfg.chapters_manifest_path
    if not manifest_path.exists():
        raise SystemExit(
            "Missing chapters manifest. Run: python tools/update_canonical.py --tag <INGEST_TAG>"
        )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    out_dir = cfg.root / "analysis" / "results"
    out_path = write_chapter_lengths_csv(out_dir, manifest)
    print(f"✅ wrote {out_path}")


if __name__ == "__main__":
    main()
