from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

import main
from database import get_db_session
from main import app
from models import EvaluationRun

SAFE_RESULT = {
    "currency": "INR",
    "is_safe_to_process": True,
    "refusal_reason": None,
    "market_value_range": [100, 200],
    "distress_value_range": [80, 150],
    "resale_potential_index": 75,
    "estimated_time_to_sell_days": [30, 60],
    "agent_confidence_score": 0.9,
    "oversight_audit_log": {
        "verified_drivers": ["size_sqft"],
        "flagged_risks": [],
        "hallucination_check": "passed",
        "prompt_injection_detected": False,
        "bias_or_unsubstantiated_premium_flagged": False,
    },
}


class ScalarResult:
    def __init__(self, values: list[Any]):
        self.values = values

    def all(self) -> list[Any]:
        return self.values


class RecordingSession:
    """In-memory async session double for persistence endpoint tests."""

    def __init__(self, runs: list[EvaluationRun]):
        self.runs = runs

    def add(self, instance: EvaluationRun) -> None:
        if instance not in self.runs:
            self.runs.append(instance)

    async def commit(self) -> None:
        return None

    async def refresh(self, instance: EvaluationRun) -> None:
        instance.id = instance.id or uuid4()
        instance.created_at = instance.created_at or datetime.now(UTC)

    async def rollback(self) -> None:
        return None

    async def execute(self, statement: Any) -> None:
        return None

    async def scalar(self, statement: Any) -> int:
        return len(self.runs)

    async def scalars(self, statement: Any) -> ScalarResult:
        return ScalarResult(sorted(self.runs, key=lambda run: run.created_at, reverse=True))


@pytest.mark.asyncio
async def test_evaluate_persists_run_and_currency(monkeypatch: pytest.MonkeyPatch) -> None:
    runs: list[EvaluationRun] = []
    session = RecordingSession(runs)

    async def override_session():
        yield session

    async def fake_orchestration(data: dict[str, Any]) -> dict[str, Any]:
        assert data["currency"] == "INR"
        return SAFE_RESULT

    monkeypatch.setattr(main, "run_orchestration", fake_orchestration)
    app.dependency_overrides[get_db_session] = override_session
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/evaluate",
                json={
                    "address": "123 Main Street",
                    "property_type": "Residential House",
                    "size_sqft": 1500,
                    "age_years": 10,
                    "currency": "INR",
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["currency"] == "INR"
    assert len(runs) == 1
    assert runs[0].status == "completed"
    assert runs[0].output == SAFE_RESULT


@pytest.mark.asyncio
async def test_evaluation_history_is_paginated() -> None:
    run = EvaluationRun(
        id=uuid4(),
        input={
            "address": "123 Main Street",
            "property_type": "Residential House",
            "size_sqft": 1500,
            "age_years": 10,
            "has_legal_disputes": False,
            "currency": "USD",
        },
        output={**SAFE_RESULT, "currency": "USD"},
        status="completed",
        latency_ms=125,
        model="test-model",
        created_at=datetime.now(UTC),
    )
    session = RecordingSession([run])

    async def override_session():
        yield session

    app.dependency_overrides[get_db_session] = override_session
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/evaluations?page=1&page_size=1")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert len(body["items"]) == 1
    assert body["items"][0]["input"]["currency"] == "USD"
