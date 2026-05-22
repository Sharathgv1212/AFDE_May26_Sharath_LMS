"""ETL configuration. Keep tuning knobs in one place."""
from pathlib import Path

# Project root = the parent of this etl/ package.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATASETS_DIR = PROJECT_ROOT / "datasets"
BOOKS_CSV = DATASETS_DIR / "books.csv"
BORROWERS_CSV = DATASETS_DIR / "borrowers.csv"
TRANSACTIONS_CSV = DATASETS_DIR / "transactions.csv"

# SQLite file the API uses. We add analytics_ tables alongside the OLTP
# tables; the OLTP tables are never modified by the ETL.
DB_PATH = PROJECT_ROOT / "library.db"
DB_URL = f"sqlite:///{DB_PATH}"

# Business rule: any return >14 days after borrow is overdue. Active loans
# whose borrow_date is more than 14 days ago are also flagged overdue.
LOAN_PERIOD_DAYS = 14
