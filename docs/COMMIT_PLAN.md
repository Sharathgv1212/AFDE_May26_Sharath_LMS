# 3-Day Commit Plan — AFDE_Jan26_Sharath_LMS

The rubric requires daily, meaningful commits — no last-day bulk uploads.
Follow this cadence; adjust messages if the work order shifts. Conventional
prefixes (`feat:`, `fix:`, `docs:`, `chore:`, `test:`) are used throughout.

## Day 1 — Backend + Database

1. `chore: scaffold repo structure (frontend/backend/database/docs/screenshots)`
2. `feat(backend): add SQLAlchemy engine, models, and base session`
3. `feat(backend): add Pydantic v2 schemas with category + ISBN validation`
4. `feat(backend): wire FastAPI app with CORS and 422 error handler`
5. `feat(backend): implement books CRUD router with /stats`
6. `feat(backend): implement borrowers CRUD router with 409 guard on delete`
7. `feat(backend): implement borrow/return + transactions endpoints`
8. `feat(backend): add /search endpoint with keyword and per-field filters`
9. `feat(database): add schema.sql with indexes and seed data`
10. `test(backend): add smoke_test.py covering all endpoints`
11. `docs: README + docs/API.md endpoint reference`

## Day 2 — Frontend + Integration

1. `chore(frontend): bootstrap Vite + React + React Router + axios`
2. `feat(frontend): add styles, layout shell, and nav`
3. `feat(frontend): add api.js with 422 error normalisation`
4. `feat(frontend): build Dashboard page with stats + recent transactions`
5. `feat(frontend): build Books page with list + add + edit + delete`
6. `feat(frontend): build Borrowers page with full CRUD`
7. `feat(frontend): build Borrow/Return page wired to transactions API`
8. `fix(frontend): hide deleted books and refresh tables after mutations`

## Day 3 — Search, Polish, Submission

1. `feat(frontend): build Search page with combinable filters`
2. `test(backend): extend smoke_test for 404/409 paths`
3. `docs: add docs/SCREENSHOTS.md capture checklist`
4. `docs: add LMS.postman_collection.json with positive + 422 + 404 cases`
5. `chore: add start_backend.ps1 / start_frontend.ps1 + .gitignore`
6. `chore: capture screenshots and commit under screenshots/`
7. `docs: finalise README, link API/Postman/screenshots`
8. `chore: final pass — lint, formatting, repo cleanup`

---

# Phase 2 — ETL + Analytics (3-day plan)

Phase 2 extends Phase 1 with a pandas ETL pipeline and an analytics
dashboard. Same daily-commit rule applies.

## Day 1 (Phase 2) — Datasets + ETL

1. `chore(datasets): add books/borrowers/transactions CSVs with intentional dupes + nulls`
2. `docs(datasets): add datasets/README.md describing schemas and cleaning rules`
3. `feat(etl): scaffold etl/ package with config (paths, 14-day loan period)`
4. `feat(etl): add extract.py reading the three CSVs into pandas DataFrames`
5. `feat(etl): add transform.py with dedup, null handling, derived columns, aggregations`
6. `feat(etl): add load.py writing analytics_* tables + audit row`
7. `feat(etl): add run.py orchestrator (CLI entrypoint)`
8. `chore(deps): add pandas to requirements.txt`

## Day 2 (Phase 2) — Analytics API + Dashboard

1. `feat(backend): add analytics_schemas.py with Pydantic v2 models`
2. `feat(backend): add /analytics router (summary, popular-books, category, monthly, overdue, runs)`
3. `feat(backend): add POST /analytics/refresh that triggers the ETL`
4. `chore(frontend): add recharts dependency`
5. `feat(frontend): add services/analytics.js`
6. `feat(frontend): build /analytics page — summary cards, bar/pie/line charts, overdue table, ETL log`
7. `feat(frontend): wire Analytics into App.jsx nav + route`

## Day 3 (Phase 2) — Testing + Docs + Submission

1. `test(backend): extend smoke_test.py with ETL refresh + all analytics endpoints`
2. `docs: add Analytics folder to LMS.postman_collection.json`
3. `docs: write docs/ETL.md walkthrough with pipeline diagram and cleaning rules`
4. `docs: update README with Phase 2 section, structure, ETL workflow, analytics endpoints`
5. `docs: append Phase 2 entries to docs/API.md`
6. `chore: capture ETL run + Analytics page screenshots under screenshots/`
7. `chore: final pass — verify py -m etl.run and py backend\smoke_test.py both green`

## Commit etiquette

- Aim for **2–4 commits per day minimum**.
- Each commit message should describe the *outcome*, not "changes".
- Keep frontend and backend commits separate where possible — easier to
  review and easier to bisect.
- Push at the end of every working session, not at the end of Day 3.
