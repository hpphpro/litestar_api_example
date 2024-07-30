from typing import Any

import uvicorn

from src.core.logger import log
from src.core.settings import Settings


def run_uvicorn(app: Any, settings: Settings, workers: int = 1, **kw: Any) -> None:
    uv_config = uvicorn.Config(
        app,
        host=settings.server.host,
        port=settings.server.port,
        workers=workers,
        **kw,
    )
    server = uvicorn.Server(uv_config)
    log.info("Running API Uvicorn")
    server.run()
