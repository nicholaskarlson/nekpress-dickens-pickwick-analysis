Apply this pack from the repo root.

Files replaced:
- src/nekpress_dickens_analysis/book_config.py
- src/nekpress_dickens_analysis/nlp/chapter_lengths.py
- src/nekpress_dickens_analysis/nlp/volume_plan.py
- tools/build_analysis.py
- tools/update_canonical.py
- tools/write_analysis_sha256.py
- tests/test_repo_basics.py
- tests/test_chapter_lengths_and_volume_plan.py
- .github/workflows/release-analysis.yml
- README.md

Purpose:
- pin chapters.json and volume_plan_draft.json from the ingest release
- generate chapter_lengths.csv
- generate volume_plan_candidates.json
- include those outputs in the sha256 manifest and release workflow
