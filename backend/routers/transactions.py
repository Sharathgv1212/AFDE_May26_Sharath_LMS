"""Borrow / Return / Transactions endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..db import get_db
from ..models import Transaction

router = APIRouter(tags=["transactions"])


def _hydrate(txn: Transaction) -> schemas.TransactionDetailResponse:
    """Add book_title + borrower_name to a transaction for UI consumption."""
    return schemas.TransactionDetailResponse(
        transaction_id=txn.transaction_id,
        book_id=txn.book_id,
        borrower_id=txn.borrower_id,
        borrow_date=txn.borrow_date,
        return_date=txn.return_date,
        book_title=txn.book.title if txn.book else None,
        borrower_name=txn.borrower.borrower_name if txn.borrower else None,
    )


@router.get("/transactions", response_model=list[schemas.TransactionDetailResponse])
def list_transactions(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
    db: Session = Depends(get_db),
):
    txns = crud.list_transactions(db, skip=skip, limit=limit, active_only=active_only)
    return [_hydrate(t) for t in txns]


@router.get("/transactions/stats", response_model=schemas.TransactionStats)
def transaction_stats(db: Session = Depends(get_db)):
    rows = db.query(Transaction).all()
    total = len(rows)
    active = sum(1 for r in rows if r.return_date is None)
    return schemas.TransactionStats(
        total_transactions=total,
        active_loans=active,
        returned=total - active,
    )


@router.get("/transactions/recent", response_model=list[schemas.TransactionDetailResponse])
def recent_transactions(limit: int = 5, db: Session = Depends(get_db)):
    txns = crud.list_transactions(db, skip=0, limit=limit)
    return [_hydrate(t) for t in txns]


@router.get(
    "/transactions/{transaction_id}",
    response_model=schemas.TransactionDetailResponse,
)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    txn = crud.get_transaction(db, transaction_id)
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return _hydrate(txn)


@router.post(
    "/borrow",
    response_model=schemas.TransactionDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
def borrow_book(payload: schemas.BorrowRequest, db: Session = Depends(get_db)):
    book = crud.get_book(db, payload.book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    borrower = crud.get_borrower(db, payload.borrower_id)
    if not borrower:
        raise HTTPException(status_code=404, detail="Borrower not found")
    if book.availability_status != "Available":
        raise HTTPException(
            status_code=409, detail="Book is not currently available"
        )
    txn = crud.create_transaction(db, book, borrower)
    return _hydrate(txn)


@router.post("/return", response_model=schemas.TransactionDetailResponse)
def return_book(payload: schemas.ReturnRequest, db: Session = Depends(get_db)):
    txn = crud.get_transaction(db, payload.transaction_id)
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    if txn.return_date is not None:
        raise HTTPException(
            status_code=409,
            detail="This transaction has already been closed (book returned)",
        )
    book = crud.get_book(db, txn.book_id)
    if not book:
        raise HTTPException(
            status_code=404, detail="Associated book record not found"
        )
    txn = crud.close_transaction(db, txn, book)
    return _hydrate(txn)
