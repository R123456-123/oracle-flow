import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from schemas import PropertyInput, FinalValuation
from agents import run_orchestration
from config import API_HOST, API_PORT

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
    allow_origins=["*"],  # Restrict to frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "message": "Welcome to the Oracle Flow Engine",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/api/v1/evaluate", response_model=FinalValuation)
async def evaluate_property(payload: PropertyInput):
    """
    Evaluate a property using the multi-agent orchestration system.

    Returns a FinalValuation with market range, distress range, confidence,
    and a full audit log.
    """
    try:
        logger.info("Evaluation request: %s", payload.address)

        data = payload.model_dump()
        result = await run_orchestration(data)

        logger.info("Evaluation complete: safe=%s", result.get("is_safe_to_process"))
        return result

    except ValueError as e:
        logger.error("Validation error: %s", e)
        raise HTTPException(status_code=400, detail=f"Validation error: {str(e)}")
    except TimeoutError as e:
        logger.error("Timeout error: %s", e)
        raise HTTPException(status_code=504, detail="Evaluation timeout")
    except Exception as e:
        logger.error("Unexpected error: %s: %s", type(e).__name__, e)
        raise HTTPException(
            status_code=500,
            detail="Internal server error. Check logs for details.",
        )


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting Oracle Flow on %s:%s", API_HOST, API_PORT)
    uvicorn.run(app, host=API_HOST, port=API_PORT)