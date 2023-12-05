import asyncio

import pytest
import pytest_mock

from actchainkit.periodic_loops import HttpRequestPeriodicLoop, PeriodicLoop


async def _run_loop(loop: PeriodicLoop[int]) -> None:
    async for _ in loop.loop():
        pass


class TestPeriodicLoop:
    @pytest.mark.asyncio
    async def test_calls_run_periodically(self, mocker: pytest_mock.MockerFixture):
        periodic_loop = PeriodicLoop[int](lambda: 1, 0.01)
        spy = mocker.spy(periodic_loop, "_run")

        task = asyncio.create_task(_run_loop(periodic_loop))
        await asyncio.sleep(0.03)
        assert spy.call_count == 3
        task.cancel()

    @pytest.mark.asyncio
    async def test_async_function(self, mocker: pytest_mock.MockerFixture):
        async def async_fnc() -> int:
            return 1

        periodic_loop = PeriodicLoop[int](async_fnc, 0.01)
        spy = mocker.spy(periodic_loop, "_run")

        task = asyncio.create_task(_run_loop(periodic_loop))
        await asyncio.sleep(0.03)
        assert spy.call_count == 3
        task.cancel()


class TestHttpRequestPeriodicLoop:
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="This test is for manual testing")
    async def test_calls_run_periodically(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        periodic_loop = HttpRequestPeriodicLoop[dict]("https://www.google.com/", 1)
        spy = mocker.spy(periodic_loop, "_run")

        task = asyncio.create_task(_run_loop(periodic_loop))
        await asyncio.sleep(3)
        assert spy.call_count == 3
        task.cancel()
