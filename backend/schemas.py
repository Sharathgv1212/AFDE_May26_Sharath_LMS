"""Pydantic v2 schemas for request/response separation."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

# Categories are a fixed enum on the backend, surfaced as a dropdown on the frontend.
ALLOWED_CATEGORIES = {
    "Fiction",
    "Non-Fiction",
    "Science",
    "History",
    "Technology",
    "Biography",
    "Children",
}

ALLOWED_AVAILABILITY = {"Available", "Borrowed"}


# ---------- Book ----------
class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    author: str = Field(..., min_length=1, max_length=120)
    category: str = Field(..., min_length=1, max_length=40)
    isbn: str = Field(..., min_length=10, max_length=20)

    @field_validator("category")
    @classmethod
    def _validate_category(cls, v: str) -> str:
        if v not in ALLOWED_CATEGORIES:
            raise ValueError(
                f"category must be one of: {sorted(ALLOWED_CATEGORIES)}"
            )
        return v

    @field_validator("isbn")
    @classmethod
    def _validate_isbn(cls, v: str) -> str:
        cleaned = v.replace("-", "").replace(" ", "")
        if not cleaned.isdigit():
            raise ValueError("isbn must contain only digits, dashes, or spaces")
        if len(cleaned) not in (10, 13):
            raise ValueError("isbn must be 10 or 13 digits after removing dashes")
        return v


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    author: Optional[str] = Field(None, min_length=1, max_length=120)
    category: Optional[str] = Field(None, min_length=1, max_length=40)
    isbn: Optional[str] = Field(None, min_length=10, max_length=20)
    availability_status: Optional[str] = None

    @field_validator("category")
    @classmethod
    def _validate_category(cls, v):
        if v is not None and v not in ALLOWED_CATEGORIES:
            raise ValueError(
                f"category must be one of: {sorted(ALLOWED_CATEGORIES)}"
            )
        return v

    @field_validator("availability_status")
    @classmethod
    def _validate_status(cls, v):
        if v is not None and v not in ALLOWED_AVAILABILITY:
            raise ValueError(
                f"availability_status must be one of: {sorted(ALLOWED_AVAILABILITY)}"
            )
        return v


class BookResponse(BookBase):
    book_id: int
    availability_status: str

    model_config = {"from_attributes": True}


# ---------- Borrower ----------
class BorrowerBase(BaseModel):
    borrower_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: str = Field(..., min_length=7, max_length=20)

    @field_validator("phone")
    @classmethod
    def _validate_phone(cls, v: str) -> str:
        cleaned = v.replace(" ", "").replace("-", "").replace("+", "")
        if not cleaned.isdigit():
            raise ValueError("phone must contain only digits, spaces, dashes, or a leading +")
        return v


class BorrowerCreate(BorrowerBase):
    pass


class BorrowerUpdate(BaseModel):
    borrower_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, min_length=7, max_length=20)

    @field_validator("phone")
    @classmethod
    def _validate_phone(cls, v):
        if v is None:
            return v
        cleaned = v.replace(" ", "").replace("-", "").replace("+", "")
        if not cleaned.isdigit():
            raise ValueError("phone must contain only digits, spaces, dashes, or a leading +")
        return v


class BorrowerResponse(BorrowerBase):
    borrower_id: int

    model_config = {"from_attributes": True}


# ---------- Transaction ----------
class BorrowRequest(BaseModel):
    book_id: int = Field(..., gt=0)
    borrower_id: int = Field(..., gt=0)


class ReturnRequest(BaseModel):
    transaction_id: int = Field(..., gt=0)


class TransactionResponse(BaseModel):
    transaction_id: int
    book_id: int
    borrower_id: int
    borrow_date: datetime
    return_date: Optional[datetime] = None

    model_config = {"from_attributes": True}


class TransactionDetailResponse(TransactionResponse):
    """Transaction enriched with book + borrower for the UI."""

    book_title: Optional[str] = None
    borrower_name: Optional[str] = None


# ---------- Stats ----------
class BookStats(BaseModel):
    total_books: int
    available_books: int
    borrowed_books: int
    categories: dict[str, int]


class TransactionStats(BaseModel):
    total_transactions: int
    active_loans: int
    returned: int
