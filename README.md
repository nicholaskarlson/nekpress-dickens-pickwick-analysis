# NEKpress — The Pickwick Papers Analysis (Public)

Public, MIT-licensed **quantitative / text-only analysis** supporting a private NEKpress paperback series for
Charles Dickens’s *The Pickwick Papers*.

This repository intentionally focuses on:
- pinning the public-domain canonical story text and supporting manifests from a deterministic private ingest release, and
- generating reproducible analysis artifacts (CSV + JSON + SHA receipts).

Private historical essays, glossary prose, and volume-specific editorial writing remain in the paperback repo.

## Run locally

```bash
ruff check .
pytest -q
python tools/build_analysis.py
python tools/write_analysis_sha256.py
```

## Expected outputs

The first real Dickens analysis pass writes:
- `analysis/results/window_metrics.csv`
- `analysis/results/keyness_last_vs_first.csv`
- `analysis/results/chapter_lengths.csv`
- `analysis/results/volume_plan_candidates.json`
- `analysis/results/analysis.sha256`

## Pin canonical + ingest manifests from the private ingest release

```bash
python tools/update_canonical.py --tag v0.3.0
```
