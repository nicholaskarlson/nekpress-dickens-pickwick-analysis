from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

from nekpress_dickens_analysis.book_config import load_book_config

ASSETS = ["canonical.txt", "canonical.sha256", "provenance.json", "chapters.json", "volume_plan_draft.json"]


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_sha256_file(p: Path) -> tuple[str, str]:
    line = p.read_text(encoding="utf-8").strip()
    parts = line.split()
    if len(parts) < 2:
        raise ValueError(f"Bad sha256 file format: {p}")
    return parts[0], parts[-1]


def main() -> int:
    cfg = load_book_config()
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True, help="Private ingest release tag, e.g. v0.1.0")
    ap.add_argument("--repo", default=cfg.repos.ingest, help="Private ingest repo owner/name")
    ap.add_argument(
        "--work",
        default=cfg.work_id,
        help="Work id (defaults from data/book.json). Only used for metadata.",
    )
    ap.add_argument(
        "--out-name",
        default=cfg.canonical_filename,
        help="Output canonical filename under data/canonical/ (defaults from data/book.json)",
    )
    args = ap.parse_args()

    root = Path(__file__).resolve().parents[1]
    out_dir = root / "data" / "canonical"
    out_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        for asset in ASSETS:
            run(["gh", "release", "download", args.tag, "-R", args.repo, "-p", asset, "--dir", str(td_path)])

        canon = td_path / "canonical.txt"
        sha_file = td_path / "canonical.sha256"
        prov = td_path / "provenance.json"
        chapters = td_path / "chapters.json"
        volume_plan = td_path / "volume_plan_draft.json"

        expected_sha, expected_name = parse_sha256_file(sha_file)
        if expected_name != "canonical.txt":
            raise RuntimeError(f"canonical.sha256 expected canonical.txt but got: {expected_name}")

        actual_sha = sha256_file(canon)
        if actual_sha != expected_sha:
            raise RuntimeError(f"SHA mismatch for canonical.txt: expected {expected_sha}, got {actual_sha}")

        dest_canon = out_dir / args.out_name
        shutil.copy2(canon, dest_canon)
        shutil.copy2(chapters, out_dir / "chapters.json")
        shutil.copy2(volume_plan, out_dir / "volume_plan_draft.json")

        meta = json.loads(prov.read_text(encoding="utf-8"))
        pin = {
            "kind": "canonical",
            "source": {
                "repo": args.repo,
                "tag": args.tag,
            },
            "path": f"data/canonical/{args.out_name}",
            "sha256": actual_sha,
            "work": args.work,
            "provenance": meta,
            "supporting_files": {
                "chapters_manifest": "data/canonical/chapters.json",
                "ingest_volume_plan_draft": "data/canonical/volume_plan_draft.json",
            },
        }
        (out_dir / "pin.json").write_text(json.dumps(pin, indent=2) + "\n", encoding="utf-8")
        shutil.copy2(prov, out_dir / "provenance.json")

    print(f"✅ pinned canonical + chapter assets to {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
