from typing import TypedDict

import actchain
from actchain import Event

from .cost_calculator import CostCalculatorSendEventData


class Order(TypedDict):
    path: tuple[str, str, str]
    expected_profit: float
    # TODO: 発注数量などの情報を追加する


class OrderCommanderSendEventData(CostCalculatorSendEventData):
    order: Order


class OrderCommander(
    actchain.Function[CostCalculatorSendEventData, OrderCommanderSendEventData]
):
    def __init__(self, order_profit: float = 0.00001):
        super(OrderCommander, self).__init__()
        self._order_profit = order_profit

    async def handle(
        self, event: Event[CostCalculatorSendEventData]
    ) -> OrderCommanderSendEventData | None:
        df_arb = event.data["df_arb"]

        df_tar = df_arb[df_arb["expected_profit"] > self._order_profit]
        if len(df_tar):
            row = df_tar.sort_values("expected_profit", ascending=False).iloc[0]
            order = Order(
                path=(
                    f"""{row["first_asset"]}USDT""",
                    f"""{row["second_asset"]}{row["first_asset"]}""",
                    f"""{row["second_asset"]}USDT""",
                ),
                expected_profit=row["expected_profit"],
            )
            return OrderCommanderSendEventData(df_arb=df_arb, order=order)
        else:
            return None
