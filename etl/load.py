"""
Load stage — write the cleaned & aggregated frames to analytics_* tables in
the same SQLite file the OLTP API uses. Each table is replaced in full per
ETL run; the OLTP tables (books / borrowers / transactions) are untouched.

We also record a row per run in analytics_etl_runs so the UI can show
"last refreshed at" and recent ETL history.
"""
from __future__ import annotations

import json
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import create_engine, text

from . import config

if TYPE_CHECKING:
    from .transform import TransformResult


ANALYTICS_TABLES = {
    "popular_books": "analytics_popular_books",
    "category_borrowing": "analytics_category_borrowing",
    "monthly_trends": "analytics_monthly_trends",
    "overdue": "analytics_overdue",
}


def _ensure_runs_table(engine) -> None:
    ddl = """
    CREATE TABLE IF NOT EXISTS analytics_etl_runs (
        run_id INTEGER PRIMARY KEY AUTOINCREMENT,
        ran_at DATETIME NOT NULL,
        status VARCHAR(20) NOT NULL,
        rows_extracted INTEGER,
        rows_loaded INTEGER,
        cleaning_stats TEXT,
        error TEXT
    );
    """
    with engine.begin() as conn:
        conn.execute(text(ddl))


def load(result: "TransformResult", rows_extracted: int) -> dict:
    engine = create_engine(config.DB_URL, future=True)
    _ensure_runs_table(engine)

    rows_loaded = 0
    error = None
    status = "success"

    try:
        for key, table in ANALYTICS_TABLES.items():
            df = result[key]
            df.to_sql(table, engine, if_exists="replace", index=False)
            rows_loaded += len(df)
    except Exception as exc:  # pragma: no cover — surfaces via run row
        status = "failed"
        error = f"{type(exc).__name__}: {exc}"

    with engine.begin() as conn:
        conn.execute(
            text(
                """INSERT INTO analytics_etl_runs
                   (ran_at, status, rows_extracted, rows_loaded, cleaning_stats, error)
                   VALUES (:ran_at, :status, :rx, :rl, :stats, :err)"""
            ),
            {
                "ran_at": datetime.utcnow(),
                "status": status,
                "rx": rows_extracted,
                "rl": rows_loaded,
                "stats": json.dumps(result["cleaning_stats"]),
                "err": error,
            },
        )

    return {
        "status": status,
        "rows_extracted": rows_extracted,
        "rows_loaded": rows_loaded,
        "error": error,
    }
