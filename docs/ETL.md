# ETL Pipeline — Phase 2

The Phase 2 deliverable adds a pandas-based Extract / Transform / Load
pipeline that turns the raw CSV datasets in `datasets/` into clean,
analytics-ready tables inside the same `library.db` file the live API uses.

## Pipeline overview

```
┌──────────────────────┐
│   datasets/*.csv     │   books.csv (32) · borrowers.csv (26) · transactions.csv (205)
│   raw, with dupes    │
│   and nulls          │
└──────────┬───────────┘
           │ extract.py
           ▼
┌──────────────────────┐
│   pandas DataFrames  │
└──────────┬───────────┘
           │ transform.py
           │  • drop exact-duplicate rows
           │  • drop transactions missing borrow_date
           │  • normalize whitespace, "" → NULL
           │  • coerce borrow_date / return_date to datetime
           │  • derive loan_duration_days, is_overdue, year_month, status
           │  • build aggregations
           ▼
┌──────────────────────┐
│  clean frames +      │
│  aggregations        │
└──────────┬───────────┘
           │ load.py
           ▼
┌──────────────────────────────────────────────────────────────┐
│   library.db (SQLite)                                        │
│   ├── books / borrowers / transactions   ← OLTP (untouched)  │
│   ├── analytics_popular_books                                │
│   ├── analytics_category_borrowing                           │
│   ├── analytics_monthly_trends                               │
│   ├── analytics_overdue                                      │
│   └── analytics_etl_runs (audit log)                         │
└──────────────────────────────────────────────────────────────┘
```

## How to run

From the project root, with the backend dependencies installed:

```powershell
py -m etl.run
```

Expected output (numbers are deterministic — the dataset was generated
with `random.seed(42)`):

```
[ETL] Extracting…
      {'books_rows': 32, 'borrowers_rows': 26, 'transactions_rows': 205, 'rows_extracted': 263}
[ETL] Transforming…
      cleaning_stats: {"books_duplicates_removed": 2, "borrowers_duplicates_removed": 1,
                       "borrowers_missing_email": 1, "borrowers_missing_phone": 1,
                       "transactions_exact_duplicates_removed": 5,
                       "transactions_dropped_missing_borrow": 7,
                       "transactions_total_clean": 193, "transactions_overdue": 99}
[ETL] Loading…
      {'status': 'success', 'rows_extracted': 263, 'rows_loaded': 160, 'error': None}
```

You can also trigger a run from inside the running app via
`POST /analytics/refresh`, or by clicking **Refresh analytics** on the
`/analytics` page in the UI. Both paths use the same `run_pipeline()`
function and write a row to `analytics_etl_runs` for the audit log.

## Files in the `etl/` package

| File             | Purpose                                                                                                |
|------------------|--------------------------------------------------------------------------------------------------------|
| `config.py`      | Single source of truth for dataset paths, DB URL, and the loan period (14 days).                       |
| `extract.py`     | Reads the three CSVs with `pandas.read_csv` and returns an `ExtractResult` dataclass.                  |
| `transform.py`   | Cleaning rules + aggregation builders. Returns a typed dict of DataFrames keyed by output table name.  |
| `load.py`        | Writes each aggregation to `analytics_*` via `df.to_sql(..., if_exists="replace")`, then records an audit row in `analytics_etl_runs`. |
| `run.py`         | Orchestrator. `py -m etl.run` is the CLI entry point; the API endpoint imports `run_pipeline` from here. |

## Cleaning rules (Transform stage)

| Rule                                          | Why                                                                              |
|-----------------------------------------------|----------------------------------------------------------------------------------|
| Drop exact-duplicate rows                     | Source CSVs have intentional duplicates so analytics aren't inflated.            |
| Drop transactions missing `borrow_date`       | A borrow with no timestamp cannot be bucketed into months and isn't usable.      |
| Normalize whitespace; empty strings → NULL    | Pandas treats `""` as a string by default; downstream aggregations need real NULLs. |
| Coerce `borrow_date` / `return_date` to `datetime` | Enables month bucketing and duration arithmetic.                               |
| Compute `loan_duration_days`                  | `(return_date or today) - borrow_date` in days.                                  |
| Compute `is_overdue`                          | `loan_duration_days > 14`. The 14-day loan period is in `etl/config.py`.         |
| Compute `year_month`                          | `borrow_date.strftime('%Y-%m')` — drives the monthly trends report.              |
| Compute `status` / `overdue_label`            | "Active" vs "Returned"; "Active Overdue", "Returned Late", or "On Time / Open".  |

## Analytics outputs (Load stage)

Each ETL run **replaces** the contents of these tables (no incremental
loads in Phase 1):

### `analytics_popular_books`
One row per book, sorted by `borrow_count` descending.
Columns: `book_id, title, author, category, borrow_count, last_borrowed_at`.

### `analytics_category_borrowing`
One row per category.
Columns: `category, borrow_count, unique_borrowers`.

### `analytics_monthly_trends`
One row per `year_month`.
Columns: `year_month, borrow_count, return_count, overdue_count`.

### `analytics_overdue`
One row per overdue transaction (closed late or still open past the loan
period). Columns: `transaction_id, book_id, book_title, book_author,
borrower_id, borrower_name, borrow_date, return_date,
loan_duration_days, overdue_label`.

### `analytics_etl_runs`
Audit log, **append-only** across runs.
Columns: `run_id, ran_at, status, rows_extracted, rows_loaded,
cleaning_stats (JSON), error`.

## Tuning the loan period

Change `LOAN_PERIOD_DAYS` in `etl/config.py` and re-run the pipeline.
Everything downstream — `is_overdue`, `overdue_label`, monthly overdue
counts, the overdue table — recomputes automatically.

## Safety properties

- The OLTP tables (`books`, `borrowers`, `transactions`) are **never**
  read or modified by the ETL. The pipeline is read-only against
  `datasets/*.csv` and write-only against `analytics_*`.
- Every API analytics endpoint degrades gracefully if `analytics_*`
  tables don't exist yet (returns `[]` rather than 500). This means the
  dashboard works on a fresh checkout before the first ETL run.
- Failures are logged to `analytics_etl_runs` with `status='failed'` and
  an `error` message so the UI's run log surfaces them.
