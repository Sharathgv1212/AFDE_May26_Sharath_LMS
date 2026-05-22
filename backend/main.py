"""FastAPI entrypoint for the Library Management System."""
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from .db import Base, engine
from .routers import analytics, books, borrowers, search, transactions

# Auto-create tables (Phase 1 convenience; production would use migrations).
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Library Management System API",
    description=(
        "REST API for managing books, borrowers, and borrow/return "
        "transactions, plus Phase 2 analytics endpoints fed by a "
        "pandas-based ETL pipeline. Built with FastAPI + SQLAlchemy + SQLite."
    ),
    version="2.0.0",
)

# CORS for local frontend dev servers (Vite default 5173, CRA fallback 3000).
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- Exception handlers ----------
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
):
    """Reshape FastAPI's default 422 payload into a flat, frontend-friendly form."""
    errors = []
    for err in exc.errors():
        # loc looks like ('body', 'isbn'); take the trailing user-facing field.
        loc = err.get("loc", [])
        field = ".".join(str(p) for p in loc if p not in ("body", "query", "path"))
        errors.append({"field": field or "request", "message": err.get("msg", "")})
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation failed", "errors": errors},
    )


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    return JSONResponse(
        status_code=409,
        content={
            "detail": "Database integrity error",
            "errors": [{"field": "request", "message": str(exc.orig)}],
        },
    )


# ---------- Routers ----------
app.include_router(books.router)
app.include_router(borrowers.router)
app.include_router(transactions.router)
app.include_router(search.router)
app.include_router(analytics.router)


@app.get("/", tags=["meta"])
def root():
    return {
        "name": "Library Management System API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}
