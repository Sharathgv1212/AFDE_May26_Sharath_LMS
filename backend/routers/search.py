"""Top-level /search endpoint for books."""
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..db import get_db

router = APIRouter(tags=["search"])


@router.get("/search", response_model=list[schemas.BookResponse])
def search(
    q: Optional[str] = Query(
        None,
        description="Keyword search across title, author, category, ISBN",
    ),
    title: Optional[str] = Query(None, description="Partial match on title"),
    author: Optional[str] = Query(None, description="Partial match on author"),
    category: Optional[str] = Query(None, description="Partial match on category"),
    available: Optional[bool] = Query(
        None, description="If set, restrict to Available or Borrowed"
    ),
    db: Session = Depends(get_db),
):
    return crud.search_books(
        db, q=q, title=title, author=author, category=category, available=available
    )
