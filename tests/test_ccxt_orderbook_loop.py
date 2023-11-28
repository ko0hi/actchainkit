import time

import pytest

from actchainkit.ccxt_orderbook_loop import CcxtOrderbookLoop


@pytest.mark.asyncio
@pytest.mark.skip(reason="This test is for manual testing")
async def test_run_realtime() -> None:
    loop = CcxtOrderbookLoop("binance", "BTC/USDT")
    n = 0
    async for _ in loop.loop():
        print(time.monotonic())
        n += 1
        if n == 3:
            break
    await loop._exchange.close()


@pytest.mark.asyncio
@pytest.mark.skip(reason="This test is for manual testing")
async def test_run_throttling() -> None:
    loop = CcxtOrderbookLoop("binance", "BTC/USDT", throttling=1)
    n = 0
    async for _ in loop.loop():
        print(time.monotonic())
        n += 1
        if n == 3:
            break
    await loop._exchange.close()
