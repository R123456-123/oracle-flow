from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from schemas import PropertyInput, FinalValuation
from agents import run_orchestration

app = FastAPI(title="Oracle Flow Agentic Valuation Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to the Oracle Flow Engine. Visit /docs to test the API."}

@app.post("/api/v1/evaluate", response_model=FinalValuation)
async def evaluate_property(payload: PropertyInput):
    try:
        # Convert Pydantic input to dict
        data = payload.model_dump()
        
        # Run the Multi-Agent Orchestration
        result = run_orchestration(data)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# To run: uvicorn main:app --reload