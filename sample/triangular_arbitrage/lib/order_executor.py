import actchain
from actchain import Event

from .order_commander import OrderCommanderSendEventData


class OrderExecutorSendEventData(OrderCommanderSendEventData):
    ...


class OrderExecutor(
    actchain.Function[OrderCommanderSendEventData, OrderExecutorSendEventData]
):
    async def handle(
        self, event: Event[OrderCommanderSendEventData]
    ) -> OrderExecutorSendEventData | None:
        # TODO: 発注処理を書く
        ...
