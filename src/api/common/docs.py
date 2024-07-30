from dataclasses import dataclass


@dataclass
class BaseDoc:
    message: str


@dataclass
class UnAuthorized:
    message: str = "Unauthorized"


@dataclass
class NotFound:
    message: str = "Not found"


@dataclass
class BadRequest:
    message: str = "Bad Request"


@dataclass
class TooManyRequests:
    message: str = "Too many requests"


@dataclass
class ServiceUnavailable:
    message: str = "Service temporary unavailable"


@dataclass
class Forbidden:
    message: str = "You have not permission"


@dataclass
class ServiceNotImplemented:
    message: str = "Service not implemented"


@dataclass
class Conflict:
    message: str = "Conflict"
