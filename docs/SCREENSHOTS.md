# Screenshot Capture Checklist

Place captured images in the top-level `screenshots/` folder. Suggested
naming: `<area>-<state>.png` (e.g. `dashboard-loaded.png`,
`books-add-form.png`). The rubric calls for UI, CRUD, search, and Postman
captures, so cover at least the items below.

## UI screens

- [ ] `dashboard-loaded.png` — Dashboard with non-zero stats and the
      "Recent Transactions" table populated.
- [ ] `books-list.png` — `/books` page with the seed table rendered.
- [ ] `books-add-form.png` — "Add Book" form expanded.
- [ ] `books-edit-form.png` — "Edit Book" form for an existing row.
- [ ] `books-delete-confirm.png` — Browser confirm dialog when deleting.
- [ ] `borrowers-list.png` — `/borrowers` page with rows.
- [ ] `borrowers-add-form.png` — "Add Borrower" form expanded.
- [ ] `transactions-borrow.png` — `/transactions` page with the Borrow
      form filled.
- [ ] `transactions-return.png` — Same page after clicking Return.
- [ ] `search-results.png` — `/search` page with results table.

## Validation / error cases

- [ ] `books-validation-error.png` — Submitting an invalid ISBN to show
      the inline error from the 422 handler.
- [ ] `delete-with-loan-409.png` — Attempting to delete a book that has
      an active loan, showing the 409 alert.

## API testing

- [ ] `postman-collection-loaded.png` — Postman with the imported
      collection visible in the sidebar.
- [ ] `postman-get-books-200.png` — Response of `GET /books`.
- [ ] `postman-post-book-201.png` — Successful book creation response.
- [ ] `postman-post-book-422.png` — Validation failure response showing
      the `{detail, errors[]}` shape.
- [ ] `postman-borrow-201.png` — Borrow response.
- [ ] `postman-return-200.png` — Return response.
- [ ] `postman-search-200.png` — Search response.
- [ ] `swagger-docs.png` — `/docs` page (FastAPI auto-generated OpenAPI).

## Database

- [ ] `sqlite-tables.png` — `sqlite3 library.db ".schema"` output.
- [ ] `sqlite-sample-rows.png` — `SELECT * FROM books LIMIT 5;` output.

## Phase 2 — ETL + Analytics

- [ ] `etl-run-success.png` — terminal capture of `py -m etl.run` finishing with `status='success'` and the cleaning_stats line.
- [ ] `analytics-tables.png` — `sqlite3 library.db ".tables"` showing the new `analytics_*` tables alongside the OLTP tables.
- [ ] `analytics-page-summary.png` — `/analytics` page top: summary cards + Refresh button.
- [ ] `analytics-popular-books.png` — bar chart of most borrowed books.
- [ ] `analytics-category-pie.png` — category-borrowing pie chart + table.
- [ ] `analytics-monthly-trends.png` — line chart with borrow/return/overdue series.
- [ ] `analytics-overdue-table.png` — overdue table with the status filter.
- [ ] `analytics-etl-runs.png` — ETL run log table.
- [ ] `postman-analytics-summary-200.png` — Postman response of `/analytics/summary`.
- [ ] `postman-analytics-refresh-200.png` — Postman response of `POST /analytics/refresh`.

## How to capture on Windows

- `Win + Shift + S` to launch Snipping Tool, drag a rectangle, save.
- For terminal screenshots in PowerShell, maximise the window first and
  zoom (`Ctrl + Mouse wheel`) so text is readable.
