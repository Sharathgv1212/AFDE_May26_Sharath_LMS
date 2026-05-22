"""SQLAlchemy ORM models for the Library Management System."""
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .db import Base


class Book(Base):
    __tablename__ = "books"

    book_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, nullable=False, index=True)
    author = Column(String, nullable=False, index=True)
    category = Column(String, nullable=False, index=True)
    isbn = Column(String, nullable=False, unique=True, index=True)
    availability_status = Column(String, nullable=False, default="Available")

    transactions = relationship(
        "Transaction", back_populates="book", cascade="save-update, merge"
    )


class Borrower(Base):
    __tablename__ = "borrowers"

    borrower_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    borrower_name = Column(String, nullable=False, index=True)
    email = Column(String, nullable=False, unique=True, index=True)
    phone = Column(String, nullable=False)

    transactions = relationship(
        "Transaction", back_populates="borrower", cascade="save-update, merge"
    )


class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    book_id = Column(Integer, ForeignKey("books.book_id"), nullable=False, index=True)
    borrower_id = Column(
        Integer, ForeignKey("borrowers.borrower_id"), nullable=False, index=True
    )
    borrow_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    return_date = Column(DateTime, nullable=True)

    book = relationship("Book", back_populates="transactions")
    borrower = relationship("Borrower", back_populates="transactions")
