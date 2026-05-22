"""
Smoke test for the Library Management System API.

Run with the backend already up (`py -m uvicorn backend.main:app --reload`):

    py backend/smoke_test.py            # uses default http://127.0.0.1:8000
    py backend/smoke_test.py http://localhost:8000

Exits 0 when every assertion passes, non-zero on the first failure.
"""
import sys
import time
import urllib.error
import urllib.request
import json
from urllib.parse import urlencode

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"
PASS = "[PASS]"
FAIL = "[FAIL]"
results = []


def _req(method, path, body=None, params=None, expect=200):
    url = BASE + path
    if params:
        url += "?" + urlencode(params)
    data = None
    headers = {"Accept": "application/json"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            status = resp.status
            payload = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        status = e.code
        payload = e.read().decode("utf-8")
    parsed = None
    if payload:
        try:
            parsed = json.loads(payload)
        except json.JSONDecodeError:
            parsed = payload
    return status, parsed


def check(name, condition, detail=""):
    label = PASS if condition else FAIL
    results.append((label, name, detail))
    print(f"{label} {name}" + (f"  -- {detail}" if detail else ""))
    if not condition:
        print("\nSmoke test failed.\n")
        for r in results:
            print(r)
        sys.exit(1)


def main():
    print(f"Smoke testing API at {BASE}\n")

    # ---------- Meta ----------
    s, body = _req("GET", "/health")
    check("GET /health returns 200", s == 200)
    check("GET /health has status=ok", isinstance(body, dict) and body.get("status") == "ok")

    s, body = _req("GET", "/")
    check("GET / returns 200", s == 200)

    # ---------- Books CRUD ----------
    isbn = f"978014240{int(time.time()) % 10000:04d}"
    s, body = _req("POST", "/books", {
        "title": "Smoke Test Book",
        "author": "Test Author",
        "category": "Technology",
        "isbn": isbn,
    })
    check("POST /books creates a book (201)", s == 201, f"got {s}")
    new_book_id = body["book_id"]
    check("New book is Available", body["availability_status"] == "Available")

    s, body = _req("GET", f"/books/{new_book_id}")
    check("GET /books/{id} returns the book", s == 200 and body["book_id"] == new_book_id)

    s, body = _req("PUT", f"/books/{new_book_id}", {"title": "Smoke Test Book v2"})
    check("PUT /books/{id} updates", s == 200 and body["title"] == "Smoke Test Book v2")

    # 422: bad category
    s, body = _req("POST", "/books", {
        "title": "X", "author": "Y", "category": "InvalidCategory", "isbn": "9780000000000"
    })
    check("POST /books with bad category returns 422", s == 422)
    check("422 payload has detail + errors", isinstance(body, dict) and "errors" in body)

    # 404: missing book
    s, _ = _req("GET", "/books/99999999")
    check("GET /books/{missing} returns 404", s == 404)

    s, _ = _req("PUT", "/books/99999999", {"title": "Nope"})
    check("PUT /books/{missing} returns 404", s == 404)

    s, _ = _req("DELETE", "/books/99999999")
    check("DELETE /books/{missing} returns 404", s == 404)

    # ---------- Borrowers CRUD ----------
    email = f"smoke_{int(time.time())}@example.com"
    s, body = _req("POST", "/borrowers", {
        "borrower_name": "Smoke Borrower",
        "email": email,
        "phone": "+919876543210",
    })
    check("POST /borrowers creates (201)", s == 201, f"got {s}")
    new_borrower_id = body["borrower_id"]

    s, body = _req("PUT", f"/borrowers/{new_borrower_id}", {"borrower_name": "Smoke Borrower v2"})
    check("PUT /borrowers/{id} updates", s == 200 and body["borrower_name"] == "Smoke Borrower v2")

    s, _ = _req("POST", "/borrowers", {
        "borrower_name": "Bad", "email": "not-an-email", "phone": "123"
    })
    check("POST /borrowers with bad email returns 422", s == 422)

    # ---------- Borrow / Return ----------
    s, body = _req("POST", "/borrow", {
        "book_id": new_book_id,
        "borrower_id": new_borrower_id,
    })
    check("POST /borrow returns 201", s == 201, f"got {s}")
    txn_id = body["transaction_id"]
    check("Borrow returns transaction with no return_date", body["return_date"] is None)

    s, body = _req("GET", f"/books/{new_book_id}")
    check("Book is now Borrowed", body["availability_status"] == "Borrowed")

    # Cannot delete book with active loan
    s, body = _req("DELETE", f"/books/{new_book_id}")
    check("DELETE active-loan book returns 409", s == 409, f"got {s}")

    # Cannot delete borrower with active loan
    s, body = _req("DELETE", f"/borrowers/{new_borrower_id}")
    check("DELETE active-loan borrower returns 409", s == 409, f"got {s}")

    # Borrow same book again -> 409
    s, body = _req("POST", "/borrow", {
        "book_id": new_book_id,
        "borrower_id": new_borrower_id,
    })
    check("Double-borrow returns 409", s == 409, f"got {s}")

    # Return
    s, body = _req("POST", "/return", {"transaction_id": txn_id})
    check("POST /return returns 200", s == 200, f"got {s}")
    check("Returned transaction has a return_date", body["return_date"] is not None)

    s, body = _req("POST", "/return", {"transaction_id": txn_id})
    check("Double-return returns 409", s == 409)

    s, body = _req("GET", f"/books/{new_book_id}")
    check("Book is Available again", body["availability_status"] == "Available")

    # ---------- Transactions ----------
    s, body = _req("GET", "/transactions")
    check("GET /transactions returns 200", s == 200)
    check("Transactions list is non-empty", isinstance(body, list) and len(body) > 0)

    s, body = _req("GET", "/transactions/stats")
    check("GET /transactions/stats returns 200", s == 200)
    check("Stats payload has required keys",
          all(k in body for k in ("total_transactions", "active_loans", "returned")))

    s, body = _req("GET", "/transactions/recent", params={"limit": 3})
    check("GET /transactions/recent returns 200", s == 200)
    check("Recent transactions <= limit", len(body) <= 3)

    # ---------- Search ----------
    s, body = _req("GET", "/search", params={"q": "Smoke"})
    check("GET /search?q=Smoke returns 200", s == 200)
    check("Search finds our book", any(b["book_id"] == new_book_id for b in body))

    s, body = _req("GET", "/search", params={"category": "Technology"})
    check("Search by category works", s == 200 and all(b["category"] == "Technology" for b in body))

    s, body = _req("GET", "/search", params={"available": "true"})
    check("Search available=true works",
          s == 200 and all(b["availability_status"] == "Available" for b in body))

    # ---------- Book stats ----------
    s, body = _req("GET", "/books/stats")
    check("GET /books/stats returns 200", s == 200)
    check("Book stats has totals",
          all(k in body for k in ("total_books", "available_books", "borrowed_books", "categories")))

    # ---------- Historical-transaction protection ----------
    # Book/borrower now have a closed transaction on file. Deleting them
    # should be blocked with 409 to preserve the ledger history.
    s, body = _req("DELETE", f"/books/{new_book_id}")
    check("DELETE book with historical transaction returns 409", s == 409, f"got {s}")
    s, body = _req("DELETE", f"/borrowers/{new_borrower_id}")
    check(
        "DELETE borrower with historical transaction returns 409",
        s == 409,
        f"got {s}",
    )

    # ---------- Cleanup ----------
    # Create a transaction-free book and borrower so we can verify the
    # happy-path DELETE still returns 204.
    isbn2 = f"978014240{int(time.time() + 1) % 10000:04d}"
    s, body = _req("POST", "/books", {
        "title": "Smoke Test Book (disposable)",
        "author": "Test Author",
        "category": "Technology",
        "isbn": isbn2,
    })
    check("POST disposable book (201)", s == 201)
    disposable_book_id = body["book_id"]
    s, _ = _req("DELETE", f"/books/{disposable_book_id}")
    check("DELETE disposable book returns 204", s == 204, f"got {s}")

    email2 = f"smoke_dispose_{int(time.time())}@example.com"
    s, body = _req("POST", "/borrowers", {
        "borrower_name": "Disposable Borrower",
        "email": email2,
        "phone": "+919999999999",
    })
    check("POST disposable borrower (201)", s == 201)
    disposable_borrower_id = body["borrower_id"]
    s, _ = _req("DELETE", f"/borrowers/{disposable_borrower_id}")
    check("DELETE disposable borrower returns 204", s == 204, f"got {s}")

    # ============================================================
    # Phase 2 — Analytics endpoints (fed by the ETL pipeline)
    # ============================================================
    # The ETL may not have been run yet; refresh it from the API to
    # guarantee analytics_ tables are populated, then assert.
    s, body = _req("POST", "/analytics/refresh")
    check("POST /analytics/refresh returns 200", s == 200, f"got {s}")
    check("Refresh status is success",
          isinstance(body, dict) and body.get("status") == "success")
    check("Refresh loaded rows > 0",
          isinstance(body, dict) and (body.get("rows_loaded") or 0) > 0)

    s, body = _req("GET", "/analytics/summary")
    check("GET /analytics/summary returns 200", s == 200)
    check("Summary has all required keys",
          isinstance(body, dict) and all(
              k in body for k in (
                  "total_books", "total_borrowers", "total_transactions",
                  "active_loans", "overdue_count", "most_borrowed_title",
                  "top_category", "last_etl_run", "last_etl_status",
              )
          ))

    s, body = _req("GET", "/analytics/popular-books", params={"limit": 5})
    check("GET /analytics/popular-books returns 200", s == 200)
    check("Popular books list <= limit", isinstance(body, list) and len(body) <= 5)
    if body:
        first = body[0]
        check("Popular book row has borrow_count",
              "borrow_count" in first and first["borrow_count"] >= 1)

    s, body = _req("GET", "/analytics/category-borrowing")
    check("GET /analytics/category-borrowing returns 200", s == 200)
    check("Category list is non-empty after ETL",
          isinstance(body, list) and len(body) > 0)

    s, body = _req("GET", "/analytics/monthly-trends")
    check("GET /analytics/monthly-trends returns 200", s == 200)
    check("Monthly trends has rows",
          isinstance(body, list) and len(body) > 0)
    if body:
        first = body[0]
        check("Monthly row has year_month + counts",
              all(k in first for k in ("year_month", "borrow_count", "return_count", "overdue_count")))

    s, body = _req("GET", "/analytics/overdue", params={"limit": 10})
    check("GET /analytics/overdue returns 200", s == 200)
    check("Overdue rows have overdue_label",
          isinstance(body, list)
          and all("overdue_label" in r for r in body))

    s, body = _req("GET", "/analytics/overdue", params={"status": "Active Overdue"})
    check("GET /analytics/overdue filtered by status returns 200", s == 200)
    check("Filtered overdue only contains Active Overdue",
          isinstance(body, list)
          and all(r["overdue_label"] == "Active Overdue" for r in body))

    s, body = _req("GET", "/analytics/runs", params={"limit": 3})
    check("GET /analytics/runs returns 200", s == 200)
    check("At least one ETL run recorded",
          isinstance(body, list) and len(body) >= 1)

    print(f"\nAll {len(results)} checks passed.")


if __name__ == "__main__":
    main()
