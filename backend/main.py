import logging
import time
from datetime import UTC, datetime

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from agents import run_orchestration
from config import API_HOST, API_PORT, LLM_MODEL_ID, settings
from database import get_db_session
from models import EvaluationRun
from rate_limit import RateLimitMiddleware
from schemas import EvaluationHistory, EvaluationSummary, FinalValuation, PropertyInput

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Oracle Flow Agentic Valuation Engine",
    description="AI-powered real estate valuation with multi-agent safety verification",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware, requests_per_minute=settings.rate_limit_per_minute)


@app.get("/")
async def root():
    return {
        "message": "Welcome to the Oracle Flow Engine",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
async def health(session: AsyncSession = Depends(get_db_session)):
    """Return service health after checking database connectivity."""
    try:
        await session.execute(text("SELECT 1"))
    except Exception as exc:
        logger.error("Database health check failed: %s", exc)
        raise HTTPException(status_code=503, detail="Database unavailable") from exc
    return {"status": "healthy"}


@app.post("/api/v1/evaluate", response_model=FinalValuation)
async def evaluate_property(
    payload: PropertyInput,
    session: AsyncSession = Depends(get_db_session),
):
    """
    Evaluate a property using the multi-agent orchestration system.

    Returns a FinalValuation with market range, distress range, confidence,
    and a full audit log.
    """
    run: EvaluationRun | None = None
    started_at = time.perf_counter()
    try:
        logger.info("Evaluation request: %s", payload.address)

        data = payload.model_dump()
        run = EvaluationRun(input=data, status="running", model=LLM_MODEL_ID)
        session.add(run)
        await session.commit()
        await session.refresh(run)

        result = await run_orchestration(data)
        run.output = result
        run.status = "completed"
        run.latency_ms = round((time.perf_counter() - started_at) * 1000)
        await session.commit()

        logger.info("Evaluation complete: safe=%s", result.get("is_safe_to_process"))
        return result

    except ValueError as e:
        logger.error("Validation error: %s", e)
        if run is not None:
            run.status = "failed"
            run.latency_ms = round((time.perf_counter() - started_at) * 1000)
            await session.commit()
        raise HTTPException(status_code=400, detail=f"Validation error: {str(e)}") from e
    except TimeoutError as e:
        logger.error("Timeout error: %s", e)
        if run is not None:
            run.status = "failed"
            run.latency_ms = round((time.perf_counter() - started_at) * 1000)
            await session.commit()
        raise HTTPException(status_code=504, detail="Evaluation timeout") from e
    except Exception as e:
        logger.error("Unexpected error: %s: %s", type(e).__name__, e)
        if run is not None:
            run.status = "failed"
            run.latency_ms = round((time.perf_counter() - started_at) * 1000)
            await session.commit()
        await session.rollback()
        raise HTTPException(
            status_code=500,
            detail="Internal server error. Check logs for details.",
        ) from e


@app.get("/api/v1/evaluations", response_model=EvaluationHistory)
async def list_evaluations(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """Return paginated evaluation history ordered from newest to oldest."""
    total = int((await session.scalar(select(func.count()).select_from(EvaluationRun))) or 0)
    offset = (page - 1) * page_size
    runs = (
        await session.scalars(
            select(EvaluationRun)
            .order_by(EvaluationRun.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
    ).all()
    items = [
        EvaluationSummary(
            id=str(run.id),
            status=run.status,
            latency_ms=run.latency_ms,
            model=run.model,
            created_at=(run.created_at or datetime.now(UTC)).isoformat(),
            input=PropertyInput.model_validate(run.input),
            output=FinalValuation.model_validate(run.output) if run.output else None,
        )
        for run in runs
    ]
    return EvaluationHistory(items=items, page=page, page_size=page_size, total=total)


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting Oracle Flow on %s:%s", API_HOST, API_PORT)
    uvicorn.run(app, host=API_HOST, port=API_PORT)
