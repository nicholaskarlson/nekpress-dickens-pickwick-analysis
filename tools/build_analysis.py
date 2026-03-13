from __future__ import annotations

import argparse

from nekpress_dickens_analysis.nlp.constraint_shift import main as constraint_shift_main


def cli() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--work",
        default=None,
        help="Deprecated; analysis is config-driven via data/book.json. (Ignored.)",
    )
    ap.parse_args()
    constraint_shift_main()
    return 0


if __name__ == "__main__":
    raise SystemExit(cli())
