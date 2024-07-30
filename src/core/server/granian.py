from typing import Any

from granian import Granian
from granian import log as granian_log
from granian.constants import Interfaces

from src.core.logger import log
from src.core.settings import Settings


def run_granian(
    target: Any,
    config: Settings,
    *,
    workers: int = 1,
    threads: int = 1,
    reload: bool = False,
    optimize_loop: bool = True,
    log_access: bool = True,
    log_level: str = "info",
    **kw: Any,
) -> None:
    server = Granian(
        target,
        address=config.server.host,
        port=config.server.port,
        loop_opt=optimize_loop,
        log_level=getattr(
            granian_log.LogLevels, log_level.lower(), granian_log.LogLevels.info
        ),
        workers=workers,
        threads=threads,
        log_access=log_access,
        reload=reload,
        interface=Interfaces.ASGI,
        **kw,
    )

    log.info("Running API Granian")
    server.serve()
