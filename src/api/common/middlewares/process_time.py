import time

from litestar.datastructures import MutableScopeHeaders
from litestar.enums import ScopeType
from litestar.middleware.base import MiddlewareProtocol
from litestar.types import ASGIApp, Message, Receive, Scope, Send


class ProcessTimeMiddleware(MiddlewareProtocol):
    __all__ = ("app",)

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == ScopeType.HTTP:
            start_time = time.perf_counter()

            async def send_wrapper(message: Message) -> None:
                if message["type"] == "http.response.start":
                    process_time = time.perf_counter() - start_time
                    headers = MutableScopeHeaders.from_message(message=message)
                    headers["X-Process-Time"] = f"{process_time:.5f}"

                await send(message)

            await self.app(scope, receive, send_wrapper)
        else:
            await self.app(scope, receive, send)
