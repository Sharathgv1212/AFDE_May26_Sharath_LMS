-- ============================================================
-- Library Management System — Phase 1 schema + seed data
-- Compatible with SQLite (default) and easily portable to PostgreSQL.
-- The FastAPI backend will auto-create these tables on startup via
-- SQLAlchemy; this script is the authoritative reference and is used
-- when bootstrapping the DB manually with `sqlite3 library.db < schema.sql`.
-- ============================================================

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS borrowers;
DROP TABLE IF EXISTS books;

-- ------------------------------------------------------------
-- Books
-- ------------------------------------------------------------
CREATE TABLE books (
    book_id              INTEGER PRIMARY KEY AUTOINCREMENT,
    title                VARCHAR(200) NOT NULL,
    author               VARCHAR(120) NOT NULL,
    category             VARCHAR(40)  NOT NULL,
    isbn                 VARCHAR(20)  NOT NULL UNIQUE,
    availability_status  VARCHAR(20)  NOT NULL DEFAULT 'Available'
        CHECK (availability_status IN ('Available', 'Borrowed'))
);
CREATE INDEX idx_books_title    ON books(title);
CREATE INDEX idx_books_author   ON books(author);
CREATE INDEX idx_books_category ON books(category);

-- ------------------------------------------------------------
-- Borrowers
-- ------------------------------------------------------------
CREATE TABLE borrowers (
    borrower_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    borrower_name  VARCHAR(100) NOT NULL,
    email          VARCHAR(120) NOT NULL UNIQUE,
    phone          VARCHAR(20)  NOT NULL
);
CREATE INDEX idx_borrowers_name ON borrowers(borrower_name);

-- ------------------------------------------------------------
-- Transactions (borrow / return ledger)
-- ------------------------------------------------------------
CREATE TABLE transactions (
    transaction_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id         INTEGER NOT NULL,
    borrower_id     INTEGER NOT NULL,
    borrow_date     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    return_date     DATETIME NULL,
    FOREIGN KEY (book_id)     REFERENCES books(book_id),
    FOREIGN KEY (borrower_id) REFERENCES borrowers(borrower_id)
);
CREATE INDEX idx_transactions_book      ON transactions(book_id);
CREATE INDEX idx_transactions_borrower  ON transactions(borrower_id);
CREATE INDEX idx_transactions_return    ON transactions(return_date);

-- ============================================================
-- Seed data
-- ============================================================
INSERT INTO books (title, author, category, isbn, availability_status) VALUES
    ('Clean Code',                                  'Robert C. Martin',     'Technology',  '9780132350884', 'Available'),
    ('The Pragmatic Programmer',                    'Andrew Hunt',          'Technology',  '9780201616224', 'Borrowed'),
    ('Designing Data-Intensive Applications',       'Martin Kleppmann',     'Technology',  '9781449373320', 'Available'),
    ('To Kill a Mockingbird',                       'Harper Lee',           'Fiction',     '9780061120084', 'Available'),
    ('1984',                                        'George Orwell',        'Fiction',     '9780451524935', 'Borrowed'),
    ('A Brief History of Time',                     'Stephen Hawking',      'Science',     '9780553380163', 'Available'),
    ('Sapiens',                                     'Yuval Noah Harari',    'History',     '9780062316097', 'Available'),
    ('Steve Jobs',                                  'Walter Isaacson',      'Biography',   '9781451648539', 'Available'),
    ('Charlie and the Chocolate Factory',           'Roald Dahl',           'Children',    '9780142410318', 'Available'),
    ('Atomic Habits',                               'James Clear',          'Non-Fiction', '9780735211292', 'Available');

INSERT INTO borrowers (borrower_name, email, phone) VALUES
    ('Sharath Babu',  'sharath@example.com',  '+919876543210'),
    ('Ananya Rao',    'ananya@example.com',   '+919812345678'),
    ('Rahul Mehta',   'rahul@example.com',    '+919800011223'),
    ('Karthik Iyer',  'karthik@example.com',  '+919811122334');

-- Two open loans corresponding to the 'Borrowed' books above.
INSERT INTO transactions (book_id, borrower_id, borrow_date, return_date) VALUES
    (2, 1, '2026-05-10 10:30:00', NULL),                    -- Pragmatic Programmer -> Sharath
    (5, 2, '2026-05-12 14:00:00', NULL),                    -- 1984 -> Ananya
    (4, 3, '2026-05-01 09:15:00', '2026-05-09 18:00:00');   -- Mockingbird returned by Rahul
