"""Book endpoints: CRUD + stats."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..db import get_db
from ..models import Book

router = APIRouter(prefix="/books", tags=["books"])


@router.get("", response_model=list[schemas.BookResponse])
def list_books(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.list_books(db, skip=skip, limit=limit)


@router.get("/stats", response_model=schemas.BookStats)
def book_stats(db: Session = Depends(get_db)):
    books = db.query(Book).all()
    total = len(books)
    available = sum(1 for b in books if b.availability_status == "Available")
    borrowed = total - available
    categories: dict[str, int] = {}
    for b in books:
        categories[b.category] = categories.get(b.category, 0) + 1
    return schemas.BookStats(
        total_books=total,
        available_books=available,
        borrowed_books=borrowed,
        categories=categories,
    )


@router.get("/{book_id}", response_model=schemas.BookResponse)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = crud.get_book(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.post("", response_model=schemas.BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(payload: schemas.BookCreate, db: Session = Depends(get_db)):
    if crud.get_book_by_isbn(db, payload.isbn):
        raise HTTPException(
            status_code=409, detail=f"A book with ISBN {payload.isbn} already exists"
        )
    return crud.create_book(db, payload)


@router.put("/{book_id}", response_model=schemas.BookResponse)
def update_book(
    book_id: int, payload: schemas.BookUpdate, db: Session = Depends(get_db)
):
    book = crud.get_book(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if payload.isbn and payload.isbn != book.isbn:
        clash = crud.get_book_by_isbn(db, payload.isbn)
        if clash and clash.book_id != book_id:
            raise HTTPException(
                status_code=409,
                detail=f"A book with ISBN {payload.isbn} already exists",
            )
    return crud.update_book(db, book, payload)


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = crud.get_book(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if crud.book_has_active_loan(db, book_id):
        raise HTTPException(
            status_code=409,
            detail="Cannot delete book with an active (unreturned) loan",
        )
    if crud.book_has_any_transactions(db, book_id):
        raise HTTPException(
            status_code=409,
            detail=(
                "Cannot delete book with historical transactions on file. "
                "Borrowing history must be preserved."
            ),
        )
    crud.delete_book(db, book)
    return None
