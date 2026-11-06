import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from rate_limit import RateLimitMiddleware


@pytest.mark.asyncio
async def test_rate_limit_returns_429_after_configured_window_budget() -> None:
    test_app = FastAPI()

    @test_app.get("/")
    async def root() -> dict[str, str]:
        return {"status": "ok"}

    test_app.add_middleware(RateLimitMiddleware, requests_per_minute=1)

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        first = await client.get("/")
        second = await client.get("/")

    assert first.status_code == 200
    assert second.status_code == 429
    assert second.headers["retry-after"] == "60"
