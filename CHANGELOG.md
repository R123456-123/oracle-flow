# Changelog

## 0.2.0 - 2026-11-05

- Restructured the backend under `backend/` and added Python project tooling.
- Added PostgreSQL/pgvector Docker Compose support and Alembic migrations.
- Rebuilt orchestration as a LangGraph state graph with structured actor/judge output.
- Added persisted evaluation history, database health checks, pagination, currency, CORS configuration, and rate limiting.
- Added deterministic fake-LLM graph and API persistence tests.
