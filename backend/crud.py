"""Data-access layer. Routes call these helpers; they don't touch the DB directly."""
from datetime import datetime
from typing import Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from . import models, schemas


# ---------- Books ----------
def list_books(db: Session, skip: int = 0, limit: int = 100) -> list[models.Book]:
    return db.query(models.Book).offset(skip).limit(limit).all()


def get_book(db: Session, book_id: int) -> Optional[models.Book]:
    return db.query(models.Book).filter(models.Book.book_id == book_id).first()


def get_book_by_isbn(db: Session, isbn: str) -> Optional[models.Book]:
    return db.query(models.Book).filter(models.Book.isbn == isbn).first()


def create_book(db: Session, payload: schemas.BookCreate) -> models.Book:
    book = models.Book(
        title=payload.title,
        author=payload.author,
        category=payload.category,
        isbn=payload.isbn,
        availability_status="Available",
    )
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


def update_book(
    db: Session, book: models.Book, payload: schemas.BookUpdate
) -> models.Book:
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(book, field, value)
    db.commit()
    db.refresh(book)
    return book


def delete_book(db: Session, book: models.Book) -> None:
    db.delete(book)
    db.commit()


def book_has_active_loan(db: Session, book_id: int) -> bool:
    return (
        db.query(models.Transaction)
        .filter(
            models.Transaction.book_id == book_id,
            models.Transaction.return_date.is_(None),
        )
        .first()
        is not None
    )


def book_has_any_transactions(db: Session, book_id: int) -> bool:
    return (
        db.query(models.Transaction)
        .filter(models.Transaction.book_id == book_id)
        .first()
        is not None
    )


# ---------- Borrowers ----------
def list_borrowers(db: Session, skip: int = 0, limit: int = 100) -> list[models.Borrower]:
    return db.query(models.Borrower).offset(skip).limit(limit).all()


def get_borrower(db: Session, borrower_id: int) -> Optional[models.Borrower]:
    return (
        db.query(models.Borrower)
        .filter(models.Borrower.borrower_id == borrower_id)
        .first()
    )


def get_borrower_by_email(db: Session, email: str) -> Optional[models.Borrower]:
    return db.query(models.Borrower).filter(models.Borrower.email == email).first()


def create_borrower(
    db: Session, payload: schemas.BorrowerCreate
) -> models.Borrower:
    borrower = models.Borrower(
        borrower_name=payload.borrower_name,
        email=payload.email,
        phone=payload.phone,
    )
    db.add(borrower)
    db.commit()
    db.refresh(borrower)
    return borrower


def update_borrower(
    db: Session, borrower: models.Borrower, payload: schemas.BorrowerUpdate
) -> models.Borrower:
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(borrower, field, value)
    db.commit()
    db.refresh(borrower)
    return borrower


def delete_borrower(db: Session, borrower: models.Borrower) -> None:
    db.delete(borrower)
    db.commit()


def borrower_has_active_loan(db: Session, borrower_id: int) -> bool:
    return (
        db.query(models.Transaction)
        .filter(
            models.Transaction.borrower_id == borrower_id,
            models.Transaction.return_date.is_(None),
        )
        .first()
        is not None
    )


def borrower_has_any_transactions(db: Session, borrower_id: int) -> bool:
    return (
        db.query(models.Transaction)
        .filter(models.Transaction.borrower_id == borrower_id)
        .first()
        is not None
    )


# ---------- Transactions ----------
def list_transactions(
    db: Session, skip: int = 0, limit: int = 100, active_only: bool = False
) -> list[models.Transaction]:
    q = db.query(models.Transaction).order_by(models.Transaction.borrow_date.desc())
    if active_only:
        q = q.filter(models.Transaction.return_date.is_(None))
    return q.offset(skip).limit(limit).all()


def get_transaction(db: Session, transaction_id: int) -> Optional[models.Transaction]:
    return (
        db.query(models.Transaction)
        .filter(models.Transaction.transaction_id == transaction_id)
        .first()
    )


def create_transaction(
    db: Session, book: models.Book, borrower: models.Borrower
) -> models.Transaction:
    txn = models.Transaction(
        book_id=book.book_id,
        borrower_id=borrower.borrower_id,
        borrow_date=datetime.utcnow(),
        return_date=None,
    )
    book.availability_status = "Borrowed"
    db.add(txn)
    db.commit()
    db.refresh(txn)
    return txn


def close_transaction(
    db: Session, txn: models.Transaction, book: models.Book
) -> models.Transaction:
    txn.return_date = datetime.utcnow()
    book.availability_status = "Available"
    db.commit()
    db.refresh(txn)
    return txn


# ---------- Search ----------
def search_books(
    db: Session,
    q: Optional[str] = None,
    title: Optional[str] = None,
    author: Optional[str] = None,
    category: Optional[str] = None,
    available: Optional[bool] = None,
) -> list[models.Book]:
    query = db.query(models.Book)
    if title:
        query = query.filter(models.Book.title.ilike(f"%{title}%"))
    if author:
        query = query.filter(models.Book.author.ilike(f"%{author}%"))
    if category:
        query = query.filter(models.Book.category.ilike(f"%{category}%"))
    if available is not None:
        target = "Available" if available else "Borrowed"
        query = query.filter(models.Book.availability_status == target)
    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                models.Book.title.ilike(like),
                models.Book.author.ilike(like),
                models.Book.category.ilike(like),
                models.Book.isbn.ilike(like),
            )
        )
    return query.all()
