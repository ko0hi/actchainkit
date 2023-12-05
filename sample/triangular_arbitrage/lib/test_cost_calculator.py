import httpx
import pytest
import pytest_mock

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


@pytest.fixture
def dummy_exchange_info() -> dict:
    return {
        "symbols": [
            {"symbol": "BTCUSDT", "baseAsset": "BTC", "quoteAsset": "USDT"},
            {"symbol": "ETHUSDT", "baseAsset": "ETH", "quoteAsset": "USDT"},
            {"symbol": "ETHBTC", "baseAsset": "ETH", "quoteAsset": "BTC"},
        ]
    }


@pytest.mark.asyncio
async def test_compute_costs(
    mocker: pytest_mock.MockerFixture, dummy_exchange_info: dict
) -> None:
    calculator = CostCalculator()
    mocker.patch.object(calculator, "_initialize")
    calculator._exchange_info = dummy_exchange_info
    await calculator._set_symbols()

    booktickers = [
        {
            "symbol": "BTCUSDT",
            "askPrice": "10000",
            "askQty": "0.1",
            "bidPrice": "9999",
            "bidQty": "0.1",
        },
        {
            "symbol": "ETHUSDT",
            "askPrice": "1000",
            "askQty": "0.1",
            "bidPrice": "999",
            "bidQty": "0.1",
        },
        {
            "symbol": "ETHBTC",
            "askPrice": "0.01",
            "askQty": "0.001",
            "bidPrice": "0.009",
            "bidQty": "0.001",
        },
    ]

    df_result = await calculator._compute(booktickers)  # type: ignore

    assert df_result.iloc[0].to_dict() == {
        "first_asset": "BTC",
        "second_asset": "ETH",
        "result": 999.0,
        "has_arb": True,
        "expected_profit": 8.99,
    }
