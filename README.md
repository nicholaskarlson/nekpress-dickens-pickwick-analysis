# NEKpress — The Pickwick Papers Analysis (Public)

Public, MIT-licensed **quantitative / text-only analysis** supporting a private NEKpress paperback series for
Charles Dickens’s *The Pickwick Papers*.

This repository intentionally focuses on:
- pinning the public-domain canonical story text from a deterministic private ingest release, and
- generating reproducible analysis artifacts (CSV + SHA receipts).

Private historical essays, glossary prose, and volume-specific editorial writing remain in the paperback repo.

## Run locally

```bash
ruff check .
pytest -q
python -m nekpress_dickens_analysis.analyze
python tools/build_analysis.py
```
