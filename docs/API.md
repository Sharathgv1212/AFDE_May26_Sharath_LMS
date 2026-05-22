# Library Management System — API Reference

Base URL: `http://localhost:8000`
Interactive docs: `/docs` (Swagger UI) and `/redoc`.

All requests/responses use `application/json`. Timestamps are UTC ISO-8601.

## Error model

```json
{
  "detail": "Validation failed",
  "errors": [
    { "field": "isbn", "message": "isbn must be 10 or 13 digits after removing dashes" }
  ]
}
```

| Status | Meaning                                                |
|--------|--------------------------------------------------------|
| 200    | OK                                                     |
| 201    | Created                                                |
| 204    | Deleted (no body)                                      |
| 404    | Resource not found                                     |
| 409    | Conflict (duplicate ISBN/email, active loan, etc.)     |
| 422    | Validation failed — see `errors[]`                     |

---

## Books

### `GET /books`
List books. Supports `skip` and `limit` query params.

```bash
curl http://localhost:8000/books
```

### `GET /books/{book_id}`
Retrieve a book by id. Returns 404 if missing.

```bash
curl http://localhost:8000/books/1
```

### `POST /books`
Create a book. Category is restricted to: `Fiction`, `Non-Fiction`,
`Science`, `History`, `Technology`, `Biography`, `Children`. ISBN must
be 10 or 13 digits (dashes and spaces accepted).

```bash
curl -X POST http://localhost:8000/books \
  -H "Content-Type: application/json" \
  -d '{
    "title": "The Mythical Man-Month",
    "author": "Frederick P. Brooks Jr.",
    "category": "Technology",
    "isbn": "9780201835953"
  }'
```

Returns **201** with the created book and `availability_status: "Available"`.

### `PUT /books/{book_id}`
Partial update — pass any subset of `title`, `author`, `category`,
`isbn`, `availability_status`.

```bash
curl -X PUT http://localhost:8000/books/1 \
  -H "Content-Type: application/json" \
  -d '{"title": "Clean Code (2nd ed.)"}'
```

### `DELETE /books/{book_id}`
Returns **204** on success, **404** if missing, **409** if the book has
an active (unreturned) loan **or any historical transaction on file**.
The ledger is preserved by design — once a book has been borrowed
(even if subsequently returned), it cannot be hard-deleted.

```bash
curl -X DELETE http://localhost:8000/books/1
```

### `GET /books/stats`
Aggregate counts used by the dashboard.

```bash
curl http://localhost:8000/books/stats
# { "total_books": 10, "available_books": 8, "borrowed_books": 2,
#   "categories": { "Fiction": 2, "Technology": 3, ... } }
```

---

## Borrowers

### `GET /borrowers`
List borrowers (supports `skip` / `limit`).

```bash
curl http://localhost:8000/borrowers
```

### `GET /borrowers/{borrower_id}`
Returns the borrower, or 404.

### `POST /borrowers`
Create a borrower. Email is validated; phone must be 7–15 digits
(with optional `+`, dashes, spaces).

```bash
curl -X POST http://localhost:8000/borrowers \
  -H "Content-Type: application/json" \
  -d '{
    "borrower_name": "Sharath Babu",
    "email": "sharath@example.com",
    "phone": "+919876543210"
  }'
```

### `PUT /borrowers/{borrower_id}`
Partial update — `borrower_name`, `email`, `phone` optional.

### `DELETE /borrowers/{borrower_id}`
**204** on success, **404** if missing, **409** if the borrower has an
active loan **or any historical transaction on file** (ledger
preservation, same rule as books).

---

## Borrow / Return / Transactions

### `POST /borrow`
Issue a book to a borrower. Returns **201** with the created
transaction. Marks the book as `Borrowed`.

```bash
curl -X POST http://localhost:8000/borrow \
  -H "Content-Type: application/json" \
  -d '{"book_id": 1, "borrower_id": 2}'
```

Errors: 404 (unknown book/borrower), 409 (book already borrowed).

### `POST /return`
Close a transaction. Sets `return_date` and marks the book as
`Available`.

```bash
curl -X POST http://localhost:8000/return \
  -H "Content-Type: application/json" \
  -d '{"transaction_id": 4}'
```

Errors: 404 (unknown txn), 409 (already returned).

### `GET /transactions`
List transactions, newest first. Supports `skip`, `limit`,
`active_only=true` (only open loans).

```bash
curl "http://localhost:8000/transactions?active_only=true"
```

### `GET /transactions/recent?limit=5`
Convenience endpoint for the dashboard.

### `GET /transactions/stats`
```json
{ "total_transactions": 12, "active_loans": 3, "returned": 9 }
```

### `GET /transactions/{id}`
Retrieve one transaction (enriched with book title + borrower name).

---

## Search

### `GET /search`
All parameters optional and combinable.

| Query param | Type   | Description                                              |
|-------------|--------|----------------------------------------------------------|
| `q`         | string | Substring match across title, author, category, ISBN    |
| `title`     | string | Substring match on title                                |
| `author`    | string | Substring match on author                               |
| `author`    | string | Substring match on category                             |
| `available` | bool   | `true` restricts to Available, `false` to Borrowed       |

```bash
curl "http://localhost:8000/search?author=harari"
curl "http://localhost:8000/search?category=Technology&available=true"
curl "http://localhost:8000/search?q=orwell"
```

Returns a list of `BookResponse` objects.

---

## Analytics (Phase 2)

All analytics endpoints read from `analytics_*` tables populated by the
ETL pipeline (see [`ETL.md`](ETL.md)). Endpoints degrade gracefully and
return empty lists if the ETL has never run.

### `POST /analytics/refresh`
Runs the full Extract → Transform → Load pipeline synchronously and
records an audit row in `analytics_etl_runs`. Used by the dashboard's
"Refresh analytics" button.

```bash
curl -X POST http://localhost:8000/analytics/refresh
# {
#   "status": "success",
#   "rows_extracted": 263,
#   "rows_loaded": 160,
#   "error": null,
#   "ran_at": "2026-05-22T10:14:08.421Z"
# }
```

### `GET /analytics/summary`
Headline stats for the dashboard's top cards.

```bash
curl http://localhost:8000/analytics/summary
# {
#   "total_books": 30, "total_borrowers": 25,
#   "total_transactions": 193, "active_loans": 58,
#   "overdue_count": 99,
#   "most_borrowed_title": "Designing Data-Intensive Applications",
#   "most_borrowed_count": 15,
#   "top_category": "Technology",
#   "last_etl_run": "2026-05-22T10:14:08.421Z",
#   "last_etl_status": "success"
# }
```

### `GET /analytics/popular-books?limit=10`
Top borrowed books. `limit` is 1–100.

```bash
curl "http://localhost:8000/analytics/popular-books?limit=5"
```

### `GET /analytics/category-borrowing`
Borrows + unique borrowers per category, ordered by borrows.

```bash
curl http://localhost:8000/analytics/category-borrowing
```

### `GET /analytics/monthly-trends`
Borrow / return / overdue counts bucketed by `YYYY-MM`.

```bash
curl http://localhost:8000/analytics/monthly-trends
```

### `GET /analytics/overdue`
Enriched overdue transactions, sorted by loan duration descending.

| Query param | Type   | Description                                                                |
|-------------|--------|----------------------------------------------------------------------------|
| `status`    | string | Optional filter — `"Active Overdue"` or `"Returned Late"`.                 |
| `limit`     | int    | 1–1000 (default 200).                                                      |

```bash
curl "http://localhost:8000/analytics/overdue?status=Active%20Overdue"
```

### `GET /analytics/runs?limit=10`
Recent ETL runs from the audit log (newest first).

```bash
curl http://localhost:8000/analytics/runs?limit=3
```
