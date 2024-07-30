from typing import Literal, NotRequired, TypedDict

LoadsType = Literal["roles", "permissions"]


class UpdateType(TypedDict, total=False):
    login: NotRequired[str]
    password: NotRequired[str]
