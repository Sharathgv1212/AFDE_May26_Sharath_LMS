"""
Orchestrator. Runs Extract -> Transform -> Load and prints a summary.

Usage (from project root):

    py -m etl.run

Returns exit code 0 on success, 1 on failure.
"""
from __future__ import annotations

import sys
import json

from .extract import extract
from .transform import transform
from .load import load


def run_pipeline() -> dict:
    print("[ETL] Extracting…")
    ex = extract()
    print(f"      {ex.summary()}")

    print("[ETL] Transforming…")
    tr = transform(ex.books, ex.borrowers, ex.transactions)
    print(f"      cleaning_stats: {json.dumps(tr['cleaning_stats'])}")

    print("[ETL] Loading…")
    out = load(tr, rows_extracted=ex.rows_extracted)
    print(f"      {out}")
    return out


def main() -> int:
    out = run_pipeline()
    return 0 if out["status"] == "success" else 1


if __name__ == "__main__":
    sys.exit(main())
