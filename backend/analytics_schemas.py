"""Pydantic v2 schemas for analytics endpoints."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PopularBook(BaseModel):
    book_id: int
    title: Optional[str] = None
    author: Optional[str] = None
    category: Optional[str] = None
    borrow_count: int
    last_borrowed_at: Optional[datetime] = None


class CategoryBorrowing(BaseModel):
    category: str
    borrow_count: int
    unique_borrowers: int


class MonthlyTrend(BaseModel):
    year_month: str
    borrow_count: int
    return_count: int
    overdue_count: int


class OverdueRow(BaseModel):
    transaction_id: int
    book_id: int
    book_title: Optional[str] = None
    book_author: Optional[str] = None
    borrower_id: int
    borrower_name: Optional[str] = None
    borrow_date: datetime
    return_date: Optional[datetime] = None
    loan_duration_days: int
    overdue_label: str


class EtlRun(BaseModel):
    run_id: int
    ran_at: datetime
    status: str
    rows_extracted: Optional[int] = None
    rows_loaded: Optional[int] = None
    cleaning_stats: Optional[str] = None
    error: Optional[str] = None


class AnalyticsSummary(BaseModel):
    total_books: int
    total_borrowers: int
    total_transactions: int
    active_loans: int
    overdue_count: int
    most_borrowed_title: Optional[str] = None
    most_borrowed_count: Optional[int] = None
    top_category: Optional[str] = None
    last_etl_run: Optional[datetime] = None
    last_etl_status: Optional[str] = None


class RefreshResponse(BaseModel):
    status: str
    rows_extracted: int
    rows_loaded: int
    error: Optional[str] = None
    ran_at: datetime
