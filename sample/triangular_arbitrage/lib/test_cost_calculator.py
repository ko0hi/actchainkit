import httpx
import pytest

from .cost_calculator import CostCalculator


@pytest.mark.asyncio
@pytest.mark.skip(reason="Manual test")
async def test_cost_estimation() -> None:
    async with httpx.AsyncClient() as client:
        resp = await client.get("https://api.binance.com/api/v3/ticker/bookTicker")
        if resp.status_code != 200:
            raise RuntimeError(f"Failed to fetch book ticker: {resp}")
        data = resp.json()
        calculator = CostCalculator()
        costs = await calculator._compute(data)
        assert costs.columns.tolist() == [
            "first_asset",
            "second_asset",
            "result",
            "has_arb",
        ]
