import asyncio
from typing import Any, AsyncGenerator, Awaitable, Callable, Generic, TypeVar, TypedDict

import actchain

from .exceptions import ActchainKitImportError

try:
    import httpx
except ImportError:
    raise ActchainKitImportError("httpx")


T = TypeVar("T")


class PeriodicLoop(Generic[T], actchain.Loop[T]):
    def __init__(self, fnc: Callable[..., T | Awaitable[T]], interval: float | int):
        super(PeriodicLoop, self).__init__()
        self._fnc = fnc
        self._interval = interval
        self._is_awaitable = asyncio.iscoroutinefunction(fnc)

    async def loop(self) -> AsyncGenerator[T, None]:
        while True:
            yield await self._run()
            await asyncio.sleep(self._interval)

    async def _run(self) -> T:
        if self._is_awaitable:
            return await self._fnc()  # type: ignore
        else:
            return self._fnc()  # type: ignore


class HttpRequestPeriodicLoopData(TypedDict):
    data: Any
    resp: httpx.Response


class HttpRequestPeriodicLoop(PeriodicLoop[HttpRequestPeriodicLoopData]):
    def __init__(
        self,
        url: str,
        interval: int,
        method: str = "GET",
        data: dict | None = None,
        params: dict | None = None,
        **kwargs,
    ):
        super(HttpRequestPeriodicLoop, self).__init__(self._run, interval)
        self._url = url
        self._method = method
        self._data = data
        self._params = params
        self._kwargs = kwargs

    async def _run(self) -> HttpRequestPeriodicLoopData:
        async with httpx.AsyncClient() as client:
            resp = await client.request(
                self._method,
                self._url,
                params=self._params,
                data=self._data,
                **self._kwargs,
            )

            if resp.status_code != 200:
                raise ValueError(f"Invalid response: {resp.text}")
            resp.json()
            return {"data": resp.json(), "resp": resp}
