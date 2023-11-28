import asyncio
from typing import AsyncGenerator, TypedDict

import actchain

from actchainkit.exceptions import ActchainKitImportError

try:
    import ccxt.pro as ccxt
except ImportError:
    raise ActchainKitImportError("ccxt")


class CcxtOrderbookData(TypedDict):
    asks: list[list[float]]
    bids: list[list[float]]
    timestamp: int
    datetime: str
    symbol: str
    nonce: int


class CcxtOrderbookLoop(actchain.Loop[CcxtOrderbookData]):
    def __init__(
        self, exchange: str, symbol: str, limit: int = 50, throttling: int | None = None
    ):
        super(CcxtOrderbookLoop, self).__init__()
        self._exchange: ccxt.Exchange = getattr(ccxt, exchange)()
        self._symbol = symbol
        self._limit = limit
        self._throttling = throttling

    async def loop(self) -> AsyncGenerator[CcxtOrderbookData, None]:
        gen = (
            self._loop_realtime()
            if self._throttling is None
            else self._loop_throttling()
        )
        async for orderbook in gen:
            yield orderbook

    async def _loop_realtime(self) -> AsyncGenerator[CcxtOrderbookData, None]:
        while True:
            yield await self._get_orderbook()

    async def _loop_throttling(self) -> AsyncGenerator[CcxtOrderbookData, None]:
        assert self._throttling is not None
        yield await self._get_orderbook()
        while True:
            await asyncio.sleep(self._throttling)
            yield await self._get_orderbook()

    async def _get_orderbook(self) -> CcxtOrderbookData:
        return self._to_ccxt_orderbook(
            await self._exchange.watch_order_book(self._symbol, self._limit)
        )

    @classmethod
    def _to_ccxt_orderbook(cls, data: dict) -> CcxtOrderbookData:
        return CcxtOrderbookData(
            asks=data["asks"],
            bids=data["bids"],
            timestamp=data["timestamp"],
            datetime=data["datetime"],
            symbol=data["symbol"],
            nonce=data["nonce"],
        )
