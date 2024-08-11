from dataclasses import dataclass

from litestar import MediaType, status_codes
from litestar.openapi.datastructures import ResponseSpec
from litestar.openapi.spec import Example


class BaseDoc:
    message: str

    @classmethod
    def to_spec(
        cls,
        status_code: int,
        message: str | None = None,
        examples: list[Example] | None = None,
        media_type: MediaType = MediaType.JSON,
    ) -> dict[int, ResponseSpec]:
        return {
            status_code: ResponseSpec(
                cls,
                generate_examples=True,
                description=cls.message,
                media_type=media_type,
                examples=[
                    Example(
                        summary=message or cls.message,
                        value={"message": message or cls.message},
                    )
                ]
                + (examples or []),
            )
        }


@dataclass
class UnAuthorized(BaseDoc):
    message: str = "Unauthorized"

    @classmethod
    def to_spec(
        cls,
        status_code: int = status_codes.HTTP_401_UNAUTHORIZED,
        message: str | None = None,
        examples: list[Example] | None = None,
        media_type: MediaType = MediaType.JSON,
    ) -> dict[int, ResponseSpec]:
        return super().to_spec(
            status_code=status_code,
            message=message,
            examples=examples,
            media_type=media_type,
        )


@dataclass
class NotFound(BaseDoc):
    message: str = "Not found"

    @classmethod
    def to_spec(
        cls,
        status_code: int = status_codes.HTTP_404_NOT_FOUND,
        message: str | None = None,
        examples: list[Example] | None = None,
        media_type: MediaType = MediaType.JSON,
    ) -> dict[int, ResponseSpec]:
        return super().to_spec(
            message=message,
            status_code=status_code,
            examples=examples,
            media_type=media_type,
        )


@dataclass
class BadRequest(BaseDoc):
    message: str = "Bad Request"

    @classmethod
    def to_spec(
        cls,
        status_code: int = status_codes.HTTP_400_BAD_REQUEST,
        message: str | None = None,
        examples: list[Example] | None = None,
        media_type: MediaType = MediaType.JSON,
    ) -> dict[int, ResponseSpec]:
        return super().to_spec(
            message=message,
            status_code=status_code,
            examples=examples,
            media_type=media_type,
        )


@dataclass
class TooManyRequests(BaseDoc):
    message: str = "Too many requests"

    @classmethod
    def to_spec(
        cls,
        status_code: int = status_codes.HTTP_429_TOO_MANY_REQUESTS,
        message: str | None = None,
        examples: list[Example] | None = None,
        media_type: MediaType = MediaType.JSON,
    ) -> dict[int, ResponseSpec]:
        return super().to_spec(
            message=message,
            status_code=status_code,
            examples=examples,
            media_type=media_type,
        )


@dataclass
class ServiceUnavailable(BaseDoc):
    message: str = "Service temporary unavailable"

    @classmethod
    def to_spec(
        cls,
        status_code: int = status_codes.HTTP_503_SERVICE_UNAVAILABLE,
        message: str | None = None,
        examples: list[Example] | None = None,
        media_type: MediaType = MediaType.JSON,
    ) -> dict[int, ResponseSpec]:
        return super().to_spec(
            message=message,
            status_code=status_code,
            examples=examples,
            media_type=media_type,
        )


@dataclass
class Forbidden(BaseDoc):
    message: str = "You have no permission"

    @classmethod
    def to_spec(
        cls,
        status_code: int = status_codes.HTTP_403_FORBIDDEN,
        message: str | None = None,
        examples: list[Example] | None = None,
        media_type: MediaType = MediaType.JSON,
    ) -> dict[int, ResponseSpec]:
        return super().to_spec(
            message=message,
            status_code=status_code,
            examples=examples,
            media_type=media_type,
        )


@dataclass
class ServiceNotImplemented(BaseDoc):
    message: str = "Service not implemented"

    @classmethod
    def to_spec(
        cls,
        status_code: int = status_codes.HTTP_501_NOT_IMPLEMENTED,
        message: str | None = None,
        examples: list[Example] | None = None,
        media_type: MediaType = MediaType.JSON,
    ) -> dict[int, ResponseSpec]:
        return super().to_spec(
            message=message,
            status_code=status_code,
            examples=examples,
            media_type=media_type,
        )


@dataclass
class Conflict(BaseDoc):
    message: str = "Conflict"

    @classmethod
    def to_spec(
        cls,
        status_code: int = status_codes.HTTP_409_CONFLICT,
        message: str | None = None,
        examples: list[Example] | None = None,
        media_type: MediaType = MediaType.JSON,
    ) -> dict[int, ResponseSpec]:
        return super().to_spec(
            message=message,
            status_code=status_code,
            examples=examples,
            media_type=media_type,
        )
