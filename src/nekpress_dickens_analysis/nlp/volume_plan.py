from __future__ import annotations

import json
from pathlib import Path

from nekpress_dickens_analysis.book_config import load_book_config


RESULT_NAME = "volume_plan_candidates.json"


def build_candidates(ingest_plan: dict, *, target_min: int, target_max: int) -> dict:
    volumes = ingest_plan.get("volumes", [])
    if not isinstance(volumes, list) or not volumes:
        raise ValueError("Ingest volume plan draft must contain a non-empty 'volumes' list")

    volume_count = int(ingest_plan.get("volume_count", len(volumes)))
    within_target = target_min <= volume_count <= target_max

    return {
        "work_id": ingest_plan["work_id"],
        "canonical_sha256": ingest_plan["canonical_sha256"],
        "source": {
            "kind": "ingest_volume_plan_draft",
            "filename": "volume_plan_draft.json",
        },
        "target_volume_count": {
            "min": target_min,
            "max": target_max,
        },
        "observed_volume_count": volume_count,
        "within_target_range": within_target,
        "planning_basis": ingest_plan.get("planning_basis", {}),
        "volumes": volumes,
    }


def write_volume_plan_candidates(results_dir: Path, candidates: dict) -> Path:
    out_path = results_dir / RESULT_NAME
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(candidates, indent=2) + "\n", encoding="utf-8")
    return out_path


def main() -> None:
    cfg = load_book_config()
    plan_path = cfg.ingest_volume_plan_draft_path
    if not plan_path.exists():
        raise SystemExit(
            "Missing ingest volume plan draft. Run: python tools/update_canonical.py --tag <INGEST_TAG>"
        )
    ingest_plan = json.loads(plan_path.read_text(encoding="utf-8"))
    candidates = build_candidates(
        ingest_plan,
        target_min=cfg.analysis.target_volume_count_min,
        target_max=cfg.analysis.target_volume_count_max,
    )
    out_dir = cfg.root / "analysis" / "results"
    out_path = write_volume_plan_candidates(out_dir, candidates)
    print(f"✅ wrote {out_path}")


if __name__ == "__main__":
    main()
