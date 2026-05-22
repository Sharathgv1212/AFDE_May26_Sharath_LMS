"""Analytics endpoints — read from analytics_* tables populated by the ETL.

All endpoints degrade gracefully: if the ETL hasn't run yet (tables missing
or empty), reads return [] / sensible zeros rather than 500s. The
/analytics/refresh endpoint triggers an ETL run from the API.
"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from .. import analytics_schemas as aschemas
from ..db import engine, get_db
from ..models import Book, Borrower, Transaction

router = APIRouter(prefix="/analytics", tags=["analytics"])


# ---------- Helpers ----------
def _rows(sql: str, params: dict | None = None) -> list[dict]:
    """Run a raw SQL query and return list[dict]. Empty list on missing table."""
    try:
        with engine.connect() as conn:
            rs = conn.execute(text(sql), params or {})
            return [dict(r._mapping) for r in rs]
    except OperationalError:
        # analytics_* tables don't exist yet — ETL has never run.
        return []


def _scalar(sql: str, default=None):
    try:
        with engine.connect() as conn:
            row = conn.execute(text(sql)).fetchone()
            return row[0] if row else default
    except OperationalError:
        return default


# ---------- Endpoints ----------
@router.get("/popular-books", response_model=list[aschemas.PopularBook])
def popular_books(limit: int = Query(10, ge=1, le=100)):
    return _rows(
        "SELECT book_id, title, author, category, borrow_count, last_borrowed_at "
        "FROM analytics_popular_books ORDER BY borrow_count DESC LIMIT :lim",
        {"lim": limit},
    )


@router.get("/category-borrowing", response_model=list[aschemas.CategoryBorrowing])
def category_borrowing():
    return _rows(
        "SELECT category, borrow_count, unique_borrowers "
        "FROM analytics_category_borrowing ORDER BY borrow_count DESC"
    )


@router.get("/monthly-trends", response_model=list[aschemas.MonthlyTrend])
def monthly_trends():
    return _rows(
        "SELECT year_month, borrow_count, return_count, overdue_count "
        "FROM analytics_monthly_trends ORDER BY year_month ASC"
    )


@router.get("/overdue", response_model=list[aschemas.OverdueRow])
def overdue(
    status: Optional[str] = Query(
        None,
        description="Filter by overdue_label: 'Active Overdue' or 'Returned Late'",
    ),
    limit: int = Query(200, ge=1, le=1000),
):
    sql = (
        "SELECT transaction_id, book_id, book_title, book_author, "
        "borrower_id, borrower_name, borrow_date, return_date, "
        "loan_duration_days, overdue_label "
        "FROM analytics_overdue "
    )
    params = {"lim": limit}
    if status:
        sql += "WHERE overdue_label = :label "
        params["label"] = status
    sql += "ORDER BY loan_duration_days DESC LIMIT :lim"
    return _rows(sql, params)


@router.get("/runs", response_model=list[aschemas.EtlRun])
def etl_runs(limit: int = Query(10, ge=1, le=100)):
    return _rows(
        "SELECT run_id, ran_at, status, rows_extracted, rows_loaded, "
        "cleaning_stats, error FROM analytics_etl_runs "
        "ORDER BY run_id DESC LIMIT :lim",
        {"lim": limit},
    )


@router.get("/summary", response_model=aschemas.AnalyticsSummary)
def summary(db: Session = Depends(get_db)):
    total_books = db.query(Book).count()
    total_borrowers = db.query(Borrower).count()
    total_transactions = db.query(Transaction).count()
    active_loans = (
        db.query(Transaction).filter(Transaction.return_date.is_(None)).count()
    )
    overdue_count = _scalar(
        "SELECT COUNT(*) FROM analytics_overdue", default=0
    ) or 0
    top_pop = _rows(
        "SELECT title, borrow_count FROM analytics_popular_books "
        "ORDER BY borrow_count DESC LIMIT 1"
    )
    top_cat = _rows(
        "SELECT category FROM analytics_category_borrowing "
        "ORDER BY borrow_count DESC LIMIT 1"
    )
    last_run = _rows(
        "SELECT ran_at, status FROM analytics_etl_runs "
        "ORDER BY run_id DESC LIMIT 1"
    )
    return aschemas.AnalyticsSummary(
        total_books=total_books,
        total_borrowers=total_borrowers,
        total_transactions=total_transactions,
        active_loans=active_loans,
        overdue_count=overdue_count,
        most_borrowed_title=top_pop[0]["title"] if top_pop else None,
        most_borrowed_count=top_pop[0]["borrow_count"] if top_pop else None,
        top_category=top_cat[0]["category"] if top_cat else None,
        last_etl_run=last_run[0]["ran_at"] if last_run else None,
        last_etl_status=last_run[0]["status"] if last_run else None,
    )


@router.post("/refresh", response_model=aschemas.RefreshResponse)
def refresh():
    """Trigger an ETL run from the API. Useful for the dashboard's
    'Refresh analytics' button."""
    # Import lazily so the FastAPI app starts even if pandas is missing.
    try:
        from etl.run import run_pipeline
    except ImportError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"ETL package not importable: {exc}. Did you install pandas?",
        )
    try:
        out = run_pipeline()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"ETL failed: {exc}")
    return aschemas.RefreshResponse(
        status=out["status"],
        rows_extracted=out["rows_extracted"],
        rows_loaded=out["rows_loaded"],
        error=out.get("error"),
        ran_at=datetime.utcnow(),
    )
