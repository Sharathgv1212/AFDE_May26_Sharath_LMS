"""Borrower endpoints: CRUD."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..db import get_db

router = APIRouter(prefix="/borrowers", tags=["borrowers"])


@router.get("", response_model=list[schemas.BorrowerResponse])
def list_borrowers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.list_borrowers(db, skip=skip, limit=limit)


@router.get("/{borrower_id}", response_model=schemas.BorrowerResponse)
def get_borrower(borrower_id: int, db: Session = Depends(get_db)):
    borrower = crud.get_borrower(db, borrower_id)
    if not borrower:
        raise HTTPException(status_code=404, detail="Borrower not found")
    return borrower


@router.post(
    "", response_model=schemas.BorrowerResponse, status_code=status.HTTP_201_CREATED
)
def create_borrower(payload: schemas.BorrowerCreate, db: Session = Depends(get_db)):
    if crud.get_borrower_by_email(db, payload.email):
        raise HTTPException(
            status_code=409, detail=f"A borrower with email {payload.email} already exists"
        )
    return crud.create_borrower(db, payload)


@router.put("/{borrower_id}", response_model=schemas.BorrowerResponse)
def update_borrower(
    borrower_id: int,
    payload: schemas.BorrowerUpdate,
    db: Session = Depends(get_db),
):
    borrower = crud.get_borrower(db, borrower_id)
    if not borrower:
        raise HTTPException(status_code=404, detail="Borrower not found")
    if payload.email and payload.email != borrower.email:
        clash = crud.get_borrower_by_email(db, payload.email)
        if clash and clash.borrower_id != borrower_id:
            raise HTTPException(
                status_code=409,
                detail=f"A borrower with email {payload.email} already exists",
            )
    return crud.update_borrower(db, borrower, payload)


@router.delete("/{borrower_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_borrower(borrower_id: int, db: Session = Depends(get_db)):
    borrower = crud.get_borrower(db, borrower_id)
    if not borrower:
        raise HTTPException(status_code=404, detail="Borrower not found")
    if crud.borrower_has_active_loan(db, borrower_id):
        raise HTTPException(
            status_code=409,
            detail="Cannot delete borrower with an active (unreturned) loan",
        )
    if crud.borrower_has_any_transactions(db, borrower_id):
        raise HTTPException(
            status_code=409,
            detail=(
                "Cannot delete borrower with historical transactions on file. "
                "Borrowing history must be preserved."
            ),
        )
    crud.delete_borrower(db, borrower)
    return None
