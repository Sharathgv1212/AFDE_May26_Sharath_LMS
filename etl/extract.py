"""
Extract stage — read the raw CSV datasets into pandas DataFrames.

Kept deliberately simple: the only responsibility here is "get the bytes
off disk into a DataFrame and report sizes." All cleaning is in transform.py.
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from . import config


@dataclass
class ExtractResult:
    books: pd.DataFrame
    borrowers: pd.DataFrame
    transactions: pd.DataFrame
    rows_extracted: int

    def summary(self) -> dict:
        return {
            "books_rows": len(self.books),
            "borrowers_rows": len(self.borrowers),
            "transactions_rows": len(self.transactions),
            "rows_extracted": self.rows_extracted,
        }


def extract() -> ExtractResult:
    books = pd.read_csv(config.BOOKS_CSV, dtype={"isbn": str})
    borrowers = pd.read_csv(config.BORROWERS_CSV, dtype={"phone": str})
    transactions = pd.read_csv(config.TRANSACTIONS_CSV)
    total = len(books) + len(borrowers) + len(transactions)
    return ExtractResult(books, borrowers, transactions, total)
