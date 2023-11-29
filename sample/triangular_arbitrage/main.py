import asyncio

import actchain
from lib import BooktickerPolingLoop, CostCalculator, OrderCommander, OrderExecutor


async def main() -> None:
    flow_feature_extract = (
        actchain.Flow("triangular_arbitrage")
        .add(BooktickerPolingLoop(interval=1).as_chain("bookticker"))
        .add(CostCalculator().as_chain("cost"))
    )

    flow_order = (
        actchain.Flow("triangular_arbitrage")
        .add(flow_feature_extract)
        .add(OrderCommander(order_profit=0.01 / 100).as_chain("order"))
        .add(
            actchain.PassThroughChain(
                "print_order_command",
                on_handle_cb=lambda event: print("Arb!!", event.data["order"]),
            )
        )
        .add(
            # 未実装
            OrderExecutor().as_chain("order_executor"),
        )
    )

    await actchain.run(flow_feature_extract, flow_order)


if __name__ == "__main__":
    asyncio.run(main())
