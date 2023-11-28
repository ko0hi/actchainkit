from actchainkit.periodic_loops import HttpRequestPeriodicLoop


class BooktickerPolingLoop(HttpRequestPeriodicLoop):
    def __init__(self, interval: int = 1):
        super(BooktickerPolingLoop, self).__init__(
            "https://api.binance.com/api/v3/ticker/bookTicker",
            interval,
        )
