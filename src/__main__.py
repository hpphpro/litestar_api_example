import logging

from src.api import init_app
from src.api.v1 import init_v1_router
from src.core.server import run_granian, run_gunicorn, run_uvicorn, workers_count
from src.core.settings import DATETIME_FORMAT, LOGGING_FORMAT, load_settings

settings = load_settings()
app = init_app(settings, init_v1_router())


if __name__ == "__main__":
    # one-shot configuration to your logger
    logging.basicConfig(
        format=LOGGING_FORMAT,
        datefmt=DATETIME_FORMAT,
        level=settings.server.log_level.upper(),
        force=True,
    )
    workers = workers_count() if (w := settings.server.workers) == "max" else w
    match settings.server.type:
        case "granian":
            run_granian(
                "src.__main__:app",
                settings,
                optimize_loop=False,  # breaks db-connections if True. ¯\_(ツ)_/¯. Maybe it'll be fixed sometime
                workers=workers,
            )
        case "gunicorn":
            run_gunicorn(app, settings, workers=workers)
        case "uvicorn":
            run_uvicorn(app, settings, workers=workers)
