# Library Management System (LMS) — Phase 1 + Phase 2 Capstone

Full-stack web application for managing books, borrowers, and borrow/return
workflows, **extended in Phase 2 with a pandas-based ETL pipeline that
populates analytics tables and powers a Recharts dashboard**. Built as the
AFDE Jan26 capstone (Sharath).

> **Repository:** `AFDE_Jan26_Sharath_LMS`

## Project Information

A centralized digital platform that replaces manual notebooks and spreadsheets
for tracking library inventory and borrower activity. Phase 1 covers the
foundational full-stack application: REST API, persistent storage, CRUD,
search, and a responsive React UI. The architecture is intentionally modular so
later phases can layer analytics dashboards, recommendation systems, semantic
search, and authentication on top without restructuring.

### Features implemented

- Book management — add, view, edit, delete with ISBN validation
- Borrower management — add, view, edit, delete with email/phone validation
- Borrow workflow — issues a transaction, flips book to *Borrowed*
- Return workflow — closes the transaction, flips book to *Available*
- Multi-field search — keyword (any field) or specific filters on title, author, category, availability
- Dashboard with live statistics — totals, available vs. borrowed, by category, recent activity
- Structured 422 validation responses and 409 conflict responses (active-loan deletes, historical-ledger deletes, double-borrow, double-return)
- Borrowing-history preservation — books and borrowers cannot be hard-deleted once they have any transaction on file
- Auto-generated OpenAPI docs at `/docs` and `/redoc`

### Phase 2 additions

- **ETL pipeline** (`etl/` package) — Extract from CSV datasets → Transform (dedup, null handling, date parsing, derived columns) → Load into `analytics_*` tables in the same SQLite file. Runnable as `py -m etl.run` or via `POST /analytics/refresh`.
- **Analytics tables** — `analytics_popular_books`, `analytics_category_borrowing`, `analytics_monthly_trends`, `analytics_overdue`, plus `analytics_etl_runs` for an audit log of every ETL execution.
- **Analytics API** — `/analytics/summary`, `/analytics/popular-books`, `/analytics/category-borrowing`, `/analytics/monthly-trends`, `/analytics/overdue`, `/analytics/runs`, `POST /analytics/refresh`.
- **Analytics dashboard** — new `/analytics` page in the React UI with summary cards, bar / pie / line charts via Recharts, an overdue table with filter, an ETL run log, and a one-click "Refresh analytics" button.
- **Synthetic dataset** — `datasets/{books,borrowers,transactions}.csv` totalling 263 raw rows (200+ unique transactions across 24 months) with intentional duplicates and nulls for the ETL to clean.

## Technology Stack

| Layer            | Technology                                  |
|------------------|---------------------------------------------|
| Frontend         | React 18, Vite, React Router, Axios, Recharts, plain CSS |
| Backend          | FastAPI, Pydantic v2, SQLAlchemy            |
| ETL              | Python 3.14, pandas, SQLAlchemy             |
| Database         | SQLite (OLTP tables + `analytics_*` reporting tables in one file) |
| API Testing      | Postman, Python `smoke_test.py`             |
| Version Control  | Git + GitHub                                |

## Repository Structure

```
AFDE_Jan26_Sharath_LMS/
├── backend/
│   ├── __init__.py
│   ├── main.py              # FastAPI app, CORS, exception handlers
│   ├── db.py                # SQLAlchemy engine + get_db (NOT database.py)
│   ├── models.py            # ORM models
│   ├── schemas.py           # Pydantic v2 schemas (Create / Update / Response)
│   ├── crud.py              # Data-access helpers
│   ├── analytics_schemas.py # Pydantic schemas for Phase 2 analytics endpoints
│   ├── smoke_test.py        # End-to-end API check (now incl. analytics)
│   └── routers/
│       ├── books.py
│       ├── borrowers.py
│       ├── transactions.py
│       ├── search.py
│       └── analytics.py     # Phase 2: reads analytics_* tables, POST /refresh
├── etl/                     # Phase 2 ETL package
│   ├── __init__.py
│   ├── config.py            # Paths + LOAN_PERIOD_DAYS
│   ├── extract.py           # CSV -> DataFrames
│   ├── transform.py         # Dedup, nulls, derived columns, aggregations
│   ├── load.py              # Write analytics_* tables + log to analytics_etl_runs
│   └── run.py               # Orchestrator (CLI entrypoint)
├── datasets/                # Phase 2 source data
│   ├── books.csv
│   ├── borrowers.csv
│   ├── transactions.csv
│   └── README.md
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Routes + nav (incl. /analytics)
│   │   ├── main.jsx
│   │   ├── api.js           # Axios instance
│   │   ├── styles.css
│   │   ├── components/      # AvailabilityBadge, Alert, BookForm, BorrowerForm
│   │   ├── pages/           # Dashboard, Books, Borrowers, BorrowReturn, SearchPage, Analytics
│   │   └── services/        # books, borrowers, transactions, search, analytics
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── .env.example
├── database/
│   └── schema.sql           # CREATE TABLE + indexes + seed data
├── docs/
│   ├── API.md               # Endpoint reference + curl examples (incl. analytics)
│   ├── ETL.md               # Phase 2 ETL workflow walkthrough
│   ├── LMS.postman_collection.json
│   ├── SCREENSHOTS.md
│   └── COMMIT_PLAN.md
├── screenshots/             # Captured UI + Postman screenshots go here
├── start_backend.ps1
├── start_frontend.ps1
├── requirements.txt
├── .gitignore
└── README.md
```

## Setup Instructions (Windows / PowerShell)

> Tested with **Python 3.14** and **Node 22.x** on Windows 11. `cmd.exe` is not
> required — everything runs through PowerShell.

### 1. Clone

```powershell
git clone <repo-url> AFDE_Jan26_Sharath_LMS
cd AFDE_Jan26_Sharath_LMS
```

### 2. Backend

```powershell
py -m pip install -r requirements.txt
py -m uvicorn backend.main:app --reload
```

The API will be available at **http://localhost:8000** with interactive docs
at **http://localhost:8000/docs**. The first run auto-creates `library.db`
in the project root and the seed inserts from `database/schema.sql` are
optional (the app works on an empty DB). To preload seed data:

```powershell
# SQLite must be installed locally; the bundled DB file works as well.
sqlite3 library.db ".read database/schema.sql"
```

### 3. ETL pipeline (Phase 2)

Populate the `analytics_*` tables from the bundled CSV datasets:

```powershell
py -m etl.run
```

You should see Extract → Transform → Load logs, ending with
`{'status': 'success', 'rows_extracted': 263, 'rows_loaded': 160, ...}`.
The cleaned data lands in five new tables inside the same `library.db`:
`analytics_popular_books`, `analytics_category_borrowing`,
`analytics_monthly_trends`, `analytics_overdue`, `analytics_etl_runs`.

You can also trigger a re-run from inside the running app via
`POST /analytics/refresh` (or the "Refresh analytics" button on the
Analytics page). Full walkthrough: [`docs/ETL.md`](docs/ETL.md).

### 4. Frontend

In a second PowerShell window:

```powershell
npm config set script-shell "powershell.exe"   # one-time, cmd is disabled
cd frontend
npm install
npm run dev
```

The UI will open at **http://localhost:5173**. Set `VITE_API_URL` in
`frontend/.env` if the backend runs anywhere other than
`http://localhost:8000`.

### 5. Smoke test

With the backend running:

```powershell
py backend\smoke_test.py
```

The script makes ~60 API calls covering every endpoint (Phase 1 CRUD,
borrow/return, search, plus Phase 2 ETL refresh and all analytics
endpoints) and exits non-zero on any failure.

### 6. Helper scripts

`start_backend.ps1` and `start_frontend.ps1` in the project root wrap the
commands above for convenience.

## API Details

Full reference with curl examples lives in [`docs/API.md`](docs/API.md). Short
summary:

| Method | Endpoint                  | Purpose                                           |
|--------|---------------------------|---------------------------------------------------|
| GET    | `/books`                  | List books                                        |
| GET    | `/books/{id}`             | Retrieve one book                                 |
| POST   | `/books`                  | Create a book                                     |
| PUT    | `/books/{id}`             | Update a book                                     |
| DELETE | `/books/{id}`             | Delete a book (409 if active loan or any history) |
| GET    | `/books/stats`            | Total / available / borrowed / by category        |
| GET    | `/borrowers`              | List borrowers                                    |
| POST   | `/borrowers`              | Create borrower                                   |
| PUT    | `/borrowers/{id}`         | Update borrower                                   |
| DELETE | `/borrowers/{id}`         | Delete borrower (409 if active loan or any history) |
| POST   | `/borrow`                 | Borrow a book                                     |
| POST   | `/return`                 | Return a book                                     |
| GET    | `/transactions`           | List transactions (`?active_only=true` supported) |
| GET    | `/transactions/recent`    | Latest N transactions (default 5)                 |
| GET    | `/transactions/stats`     | Total / active / returned counts                  |
| GET    | `/search`                 | Search books by `q`, `title`, `author`, `category`, `available` |
| GET    | `/analytics/summary`           | Phase 2: dashboard headline stats                   |
| GET    | `/analytics/popular-books`     | Phase 2: top borrowed books (default 10)            |
| GET    | `/analytics/category-borrowing`| Phase 2: borrows + unique borrowers per category    |
| GET    | `/analytics/monthly-trends`    | Phase 2: borrow / return / overdue counts by month  |
| GET    | `/analytics/overdue`           | Phase 2: overdue transactions (`?status=...`)       |
| GET    | `/analytics/runs`              | Phase 2: recent ETL runs (audit log)                |
| POST   | `/analytics/refresh`           | Phase 2: trigger an ETL run from the API            |

Postman collection: [`docs/LMS.postman_collection.json`](docs/LMS.postman_collection.json).

### Example request/response

```bash
# Borrow a book
curl -X POST http://localhost:8000/borrow \
  -H "Content-Type: application/json" \
  -d '{"book_id": 1, "borrower_id": 2}'

# Response (201)
{
  "transaction_id": 4,
  "book_id": 1,
  "borrower_id": 2,
  "borrow_date": "2026-05-16T10:30:00",
  "return_date": null,
  "book_title": "Clean Code",
  "borrower_name": "Ananya Rao"
}
```

### Error model

All 422 responses share the same flat shape so the frontend can render them
identically:

```json
{
  "detail": "Validation failed",
  "errors": [
    { "field": "category", "message": "category must be one of: ['Biography','Children',...]" }
  ]
}
```

## Database

`database/schema.sql` contains the authoritative DDL plus seed rows (10
books, 4 borrowers, 3 transactions including one open loan). SQLAlchemy
also calls `Base.metadata.create_all` at startup so the API runs even
without the seed file.

Schema summary:

- **books**(book_id PK, title, author, category, isbn UNIQUE, availability_status)
- **borrowers**(borrower_id PK, borrower_name, email UNIQUE, phone)
- **transactions**(transaction_id PK, book_id FK, borrower_id FK, borrow_date, return_date)

Indexes: title, author, category on books; name on borrowers; book_id,
borrower_id, return_date on transactions.

### Phase 2 analytics tables

Populated by the ETL pipeline (see [`docs/ETL.md`](docs/ETL.md)):

- **analytics_popular_books**(book_id, title, author, category, borrow_count, last_borrowed_at)
- **analytics_category_borrowing**(category, borrow_count, unique_borrowers)
- **analytics_monthly_trends**(year_month, borrow_count, return_count, overdue_count)
- **analytics_overdue**(transaction_id, book_id, book_title, book_author, borrower_id, borrower_name, borrow_date, return_date, loan_duration_days, overdue_label)
- **analytics_etl_runs**(run_id, ran_at, status, rows_extracted, rows_loaded, cleaning_stats, error)

These tables are replaced in full on every ETL run; the OLTP tables are
never modified by the pipeline.

## ETL Workflow

The Phase 2 pipeline lives in `etl/` and follows the classic
Extract → Transform → Load shape:

```
datasets/*.csv  →  extract.py  →  pandas DataFrames
                                       ↓
                  transform.py:  drop dupes, drop missing borrow dates,
                                 normalize whitespace, coerce dates,
                                 compute is_overdue (>14 days),
                                 derive year_month + status,
                                 build aggregations
                                       ↓
                  load.py:       write 4 analytics_* tables
                                 +1 audit row to analytics_etl_runs
```

Loan period for overdue analytics is **14 days** (`etl/config.py`).
Triggers: `py -m etl.run` on the CLI, or `POST /analytics/refresh` from
the API. Full walkthrough in [`docs/ETL.md`](docs/ETL.md).

## Screenshots

See [`docs/SCREENSHOTS.md`](docs/SCREENSHOTS.md) for the capture checklist.
Place captured images under `screenshots/`.

## Commit Plan

The 3-day commit cadence is in [`docs/COMMIT_PLAN.md`](docs/COMMIT_PLAN.md).
Daily meaningful commits are required by the rubric — no last-day bulk
uploads.

## Evaluation Coverage

| Criterion              | Weight | Where it's covered                                        |
|------------------------|--------|-----------------------------------------------------------|
| Frontend Development   | 20%    | `frontend/` — Vite + React Router, 6 pages (incl. Analytics + Recharts), forms, validation |
| Backend API Development| 25%    | `backend/` — FastAPI, Pydantic v2, layered routers, CORS, analytics endpoints |
| Database Integration   | 15%    | `database/schema.sql` + Phase 2 `analytics_*` tables loaded by ETL |
| CRUD Functionality     | 15%    | Full CRUD on books + borrowers; borrow/return ledger      |
| Search Functionality   | 10%    | `/search` with `q`, `title`, `author`, `category`, `available` |
| Code Quality & Structure | 10%  | Modular packages, schema/CRUD/router separation, ETL package |
| Documentation          | 5%     | `README.md`, `docs/API.md`, `docs/ETL.md`, Postman, screenshots guide |
| **ETL Pipeline (Phase 2)** | — | `etl/` — pandas-based E/T/L, cleaning rules, 5 analytics tables, audit log |
| **Dashboard Reports (Phase 2)** | — | `/analytics` page with summary cards, bar / pie / line charts, overdue table |

## Future-Phase Hooks

- **Authentication** — `borrower` table is the natural user pivot; add a hashed `password` column + JWT middleware.
- **Analytics** — `transactions` already records both timestamps and can power lent-per-day / popular-category dashboards.
- **Semantic search** — swap `/search` for a vector-store backed handler (the route signature is stable).
- **AI recommendations** — borrower → category affinity is one join away.

## License

For educational use as part of the AFDE capstone program.
