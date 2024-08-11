from typing import Literal, NotRequired, TypedDict

LoadsType = Literal["roles", "permissions"]


class CreateType(TypedDict):
    login: str
    password: str


class UpdateType(TypedDict, total=False):
    login: NotRequired[str]
    password: NotRequired[str]
