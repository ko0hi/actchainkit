from typing import TypedDict

import actchain
import httpx
import numpy as np
import pandas as pd


class CostCalculatorReceiveEventData(TypedDict):
    # response data by https://api.binance.com/api/v3/ticker/bookTicker
    data: dict


class CostCalculatorSendEventData(TypedDict):
    df_arb: pd.DataFrame


class CostCalculator(
    actchain.Function[CostCalculatorReceiveEventData, CostCalculatorSendEventData]
):
    def __init__(self, swap_amount: float = 100):
        super(CostCalculator, self).__init__()
        self._swap_amount = swap_amount
        # 取引シンボル一覧
        self._exchange_info: dict | None = None
        self._symbols: list[dict] | None = None
        # USDT -> * シンボル一覧
        self._usdt_pairs: list[dict] | None = None
        # USDTベースのペアにおけるアセット一覧
        self._base_assets_in_usdt_pairs: list[str] | None = None
        # USDTベースのペアのうち、第一スワップで使用するアセット一覧
        self._first_swap_assets: set[str] | None = None
        self._first_symbols: list[dict] | None = None
        self._second_symbols: list[dict] | None = None
        self._third_symbols: list[dict] | None = None

    async def handle(self, event: actchain.Event) -> CostCalculatorSendEventData:
        return {"df_arb": await self._compute(event.data["data"])}

    async def _compute(self, booktickers: dict) -> pd.DataFrame:
        if self._exchange_info is None:
            await self._initialize()

        booktickers = {d["symbol"]: d for d in booktickers}

        cost_1st = self._compute_first_swap_costs(booktickers)
        cost_2nd = self._compute_second_swap_costs(booktickers)
        cost_3rd = self._compute_third_swap_costs(booktickers)

        costs = self._compute_costs(cost_1st, cost_2nd, cost_3rd)

        return (
            costs.reset_index()
            .melt(id_vars="index", var_name="second_asset")
            .rename(columns={"index": "first_asset", "value": "result"})
            .assign(
                has_arb=lambda _df: _df["result"] > self._swap_amount,
                expected_profit=lambda _df: _df["result"] / self._swap_amount - 1,
            )
        )

    def _compute_costs(
        self, cost_1st: pd.Series, cost_2nd: pd.DataFrame, cost_3rd: pd.Series
    ) -> pd.DataFrame:
        result_1st = (self._swap_amount / cost_1st).replace(np.inf, 0)
        result_2nd = (result_1st / cost_2nd.T).fillna(0).replace(np.inf, 0)
        result_3rd = (result_2nd.T * cost_3rd).fillna(0).replace(np.inf, 0)
        return result_3rd

    def _compute_first_swap_costs(self, booktickers: dict) -> pd.Series:
        assert self._first_symbols is not None
        return pd.Series(
            [float(booktickers[s["symbol"]]["askPrice"]) for s in self._first_symbols],
            index=[s["baseAsset"] for s in self._first_symbols],
            name="price",
        )

    def _compute_second_swap_costs(self, booktickers: dict) -> pd.DataFrame:
        assert self._second_symbols is not None
        records = []
        for s in self._second_symbols:
            _ = booktickers[s["symbol"]]
            records.append(
                {
                    "quote": s["quoteAsset"],
                    "base": s["baseAsset"],
                    "price": float(_["askPrice"]),
                }
            )
        return (
            pd.DataFrame(records)
            .set_index(["quote", "base"])
            .pivot_table(index="quote", columns="base", values="price")
            .fillna(0)
        )

    def _compute_third_swap_costs(self, booktickers: dict) -> pd.DataFrame:
        assert self._third_symbols is not None
        return pd.Series(
            [float(booktickers[s["symbol"]]["bidPrice"]) for s in self._third_symbols],
            index=[s["baseAsset"] for s in self._third_symbols],
            name="price",
        )

    async def _initialize(self) -> None:
        await self._fetch_exchange_info()
        self._set_symbols()

    async def _fetch_exchange_info(self) -> None:
        async with httpx.AsyncClient() as client:
            resp = await client.get("https://api.binance.com/api/v3/exchangeInfo")
            if resp.status_code != 200:
                raise RuntimeError(f"Failed to fetch exchange info: {resp}")
            self._exchange_info = resp.json()

    def _set_symbols(self) -> None:
        assert self._exchange_info, "Exchange info is not initialized"
        self._symbols = self._exchange_info["symbols"]
        assert self._symbols is not None
        self._usdt_pairs = [s for s in self._symbols if s["quoteAsset"] == "USDT"]
        self._base_assets_in_usdt_pairs = [s["baseAsset"] for s in self._usdt_pairs]
        # quoteAssetとしても使われているアセットを取得
        self._first_swap_assets = set(
            [
                s["baseAsset"]
                for s in self._usdt_pairs
                if any(
                    [_s for _s in self._symbols if _s["quoteAsset"] == s["baseAsset"]]
                )
            ]
        )
        # USDT -> A
        self._first_symbols = [
            s for s in self._usdt_pairs if s["baseAsset"] in self._first_swap_assets
        ]
        # A -> B
        self._second_symbols = [
            s
            for s in self._symbols
            # quoteAssetがAである
            if s["quoteAsset"] in self._first_swap_assets
            # USDTとのペアが存在する
            and s["baseAsset"] in self._base_assets_in_usdt_pairs
        ]
        # B -> USDT
        self._third_symbols = [
            s
            for s in self._usdt_pairs
            if any(
                [_s for _s in self._second_symbols if _s["baseAsset"] == s["baseAsset"]]
            )
        ]
