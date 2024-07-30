from dataclasses import dataclass

from litestar import get, status_codes


@dataclass
class Healthcheck:
    ok: bool


@get(
    "/healthcheck",
    status_code=status_codes.HTTP_200_OK,
    tags=["healthcheck"],
    exclude_from_auth=True,
)
async def healthcheck_endpoint() -> Healthcheck:
    return Healthcheck(ok=True)
