from typing import TypedDict

from actchainkit.periodic_loops import HttpRequestPeriodicLoop


class Bookticker(TypedDict):
    symbol: str
    bidPrice: str
    bidQty: str
    askPrice: str
    askQty: str


class BooktickerData(TypedDict):
    data: list[Bookticker]


class BooktickerPolingLoop(HttpRequestPeriodicLoop[BooktickerData]):
    def __init__(self, interval: int = 1):
        super(BooktickerPolingLoop, self).__init__(
            "https://api.binance.com/api/v3/ticker/bookTicker",
            interval,
        )
