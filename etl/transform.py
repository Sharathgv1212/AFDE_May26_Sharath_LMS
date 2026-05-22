"""
Transform stage — clean and enrich the extracted DataFrames.

Cleaning rules:
  * drop exact-duplicate rows
  * drop rows with critical missing values (borrow_date for transactions)
  * normalize empty strings to NaN, then NaN -> None for SQLite
  * coerce date columns to datetime
  * compute derived columns (loan_duration_days, is_overdue, year_month, status)

The output is a dict of DataFrames ready to be loaded as analytics_ tables.
"""
from __future__ import annotations

from datetime import datetime
from typing import TypedDict

import pandas as pd

from . import config


class TransformResult(TypedDict):
    clean_books: pd.DataFrame
    clean_borrowers: pd.DataFrame
    clean_transactions: pd.DataFrame
    popular_books: pd.DataFrame
    category_borrowing: pd.DataFrame
    monthly_trends: pd.DataFrame
    overdue: pd.DataFrame
    cleaning_stats: dict


def _normalize_text(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    for c in cols:
        if c in df.columns:
            df[c] = (
                df[c]
                .astype("string")
                .str.strip()
                .replace({"": pd.NA, "nan": pd.NA, "NaN": pd.NA})
            )
    return df


def transform(books_raw: pd.DataFrame, borrowers_raw: pd.DataFrame,
              transactions_raw: pd.DataFrame) -> TransformResult:
    stats: dict = {}

    # ---------- Books ----------
    books = books_raw.copy()
    pre = len(books)
    books = _normalize_text(books, ["title", "author", "category", "isbn"])
    books = books.drop_duplicates(subset=["book_id"], keep="first")
    books = books.drop_duplicates(subset=["isbn"], keep="first")
    stats["books_duplicates_removed"] = pre - len(books)

    # ---------- Borrowers ----------
    borrowers = borrowers_raw.copy()
    pre = len(borrowers)
    borrowers = _normalize_text(borrowers, ["borrower_name", "email", "phone"])
    borrowers = borrowers.drop_duplicates(subset=["borrower_id"], keep="first")
    stats["borrowers_duplicates_removed"] = pre - len(borrowers)
    stats["borrowers_missing_email"] = int(borrowers["email"].isna().sum())
    stats["borrowers_missing_phone"] = int(borrowers["phone"].isna().sum())

    # ---------- Transactions ----------
    txn = transactions_raw.copy()
    pre = len(txn)
    txn = txn.drop_duplicates()
    stats["transactions_exact_duplicates_removed"] = pre - len(txn)

    txn["borrow_date"] = pd.to_datetime(txn["borrow_date"], errors="coerce")
    txn["return_date"] = pd.to_datetime(txn["return_date"], errors="coerce")

    pre = len(txn)
    txn = txn.dropna(subset=["borrow_date"])
    stats["transactions_dropped_missing_borrow"] = pre - len(txn)

    # Derived columns
    today = pd.Timestamp(datetime.utcnow())
    # loan_duration_days: if returned, return - borrow; else today - borrow
    end = txn["return_date"].fillna(today)
    txn["loan_duration_days"] = (end - txn["borrow_date"]).dt.days
    txn["is_overdue"] = txn["loan_duration_days"] > config.LOAN_PERIOD_DAYS
    txn["year_month"] = txn["borrow_date"].dt.strftime("%Y-%m")
    txn["status"] = txn["return_date"].notna().map({True: "Returned", False: "Active"})
    # Make a friendly "overdue label" for the analytics overdue table.
    def _overdue_label(row):
        if row["is_overdue"] and pd.isna(row["return_date"]):
            return "Active Overdue"
        if row["is_overdue"] and pd.notna(row["return_date"]):
            return "Returned Late"
        return "On Time / Open"
    txn["overdue_label"] = txn.apply(_overdue_label, axis=1)

    stats["transactions_total_clean"] = len(txn)
    stats["transactions_overdue"] = int(txn["is_overdue"].sum())

    # ---------- Analytics aggregations ----------
    # Most borrowed books (joined to books for title/author)
    book_counts = (
        txn.groupby("book_id")
        .agg(borrow_count=("transaction_id", "count"),
             last_borrowed_at=("borrow_date", "max"))
        .reset_index()
    )
    popular_books = book_counts.merge(
        books[["book_id", "title", "author", "category"]],
        on="book_id", how="left"
    )
    popular_books = popular_books.sort_values("borrow_count", ascending=False)
    popular_books = popular_books[[
        "book_id", "title", "author", "category", "borrow_count", "last_borrowed_at"
    ]]

    # Category-wise borrowing
    cat_join = txn.merge(books[["book_id", "category"]], on="book_id", how="left")
    category_borrowing = (
        cat_join.groupby("category")
        .agg(borrow_count=("transaction_id", "count"),
             unique_borrowers=("borrower_id", "nunique"))
        .reset_index()
        .sort_values("borrow_count", ascending=False)
    )
    category_borrowing["category"] = category_borrowing["category"].fillna("Unknown")

    # Monthly borrowing trends
    monthly = (
        txn.groupby("year_month")
        .agg(borrow_count=("transaction_id", "count"),
             return_count=("return_date", lambda s: s.notna().sum()),
             overdue_count=("is_overdue", "sum"))
        .reset_index()
        .sort_values("year_month")
    )

    # Overdue analytics — show enriched rows
    overdue = txn[txn["is_overdue"]].merge(
        books[["book_id", "title", "author"]], on="book_id", how="left"
    ).merge(
        borrowers[["borrower_id", "borrower_name"]], on="borrower_id", how="left"
    )
    overdue = overdue[[
        "transaction_id", "book_id", "title", "author",
        "borrower_id", "borrower_name",
        "borrow_date", "return_date", "loan_duration_days",
        "overdue_label",
    ]].rename(columns={"title": "book_title", "author": "book_author"})
    overdue = overdue.sort_values("loan_duration_days", ascending=False)

    return TransformResult(
        clean_books=books,
        clean_borrowers=borrowers,
        clean_transactions=txn,
        popular_books=popular_books,
        category_borrowing=category_borrowing,
        monthly_trends=monthly,
        overdue=overdue,
        cleaning_stats=stats,
    )
