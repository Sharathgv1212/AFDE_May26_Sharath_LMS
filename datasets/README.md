# Phase 2 Datasets

Synthetic but realistic seed data for the ETL pipeline. Three CSV files
represent the historical state of the library that we run analytics over.

## Files

| File              | Rows | Notes                                                                   |
|-------------------|------|-------------------------------------------------------------------------|
| `books.csv`       | 32   | 30 unique titles + 2 intentional duplicate rows (ETL must dedup).       |
| `borrowers.csv`   | 26   | 25 unique borrowers + 1 duplicate. Row #7 has a missing email, row #12 has a missing phone. ETL must handle nulls. |
| `transactions.csv`| 205  | 200 unique transactions + 5 duplicates. ~4% have a missing `borrow_date` (ETL drops). Includes returned (on-time), overdue, and still-active loans across 2024-06 to 2026-05. |

Reproducibility: `etl/datagen.py` regenerates the files deterministically
(`random.seed(42)`).

## Schemas

**books.csv** — `book_id, title, author, category, isbn`

**borrowers.csv** — `borrower_id, borrower_name, email, phone`

**transactions.csv** — `transaction_id, book_id, borrower_id, borrow_date, return_date`
(empty `return_date` = still on loan).

## Cleaning rules applied by ETL

1. Drop exact duplicate rows.
2. Drop transaction rows with missing `borrow_date` (cannot bucket).
3. Coerce `borrow_date` and `return_date` to datetime; invalid → drop / null.
4. Trim whitespace; normalize empty strings to NULL.
5. Compute derived fields: `loan_duration_days`, `is_overdue` (>14 days from borrow), `year_month` (YYYY-MM).
