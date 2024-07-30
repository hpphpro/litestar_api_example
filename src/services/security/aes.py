import base64
from typing import Final, Union, cast

from Crypto.Cipher import AES


def _resolve_key(key: Union[str, bytes]) -> bytes:
    if isinstance(key, bytes):
        return key

    return base64.urlsafe_b64decode(key)


class AESEncrypt:
    __slots__ = ("__key",)
    _bytes_slice: Final[int] = 16

    def __init__(self, key: Union[str, bytes]) -> None:
        self.__key = _resolve_key(key)

    def encrypt(self, plain_text: str) -> str:
        cipher = AES.new(self.__key, AES.MODE_CFB)
        encrypted = cast(bytes, cipher.iv) + cipher.encrypt(plain_text.encode())

        return base64.urlsafe_b64encode(encrypted).decode()

    def decrypt(self, encrypted_text: str) -> str:
        decrypted = base64.urlsafe_b64decode(encrypted_text)
        cipher = AES.new(self.__key, AES.MODE_CFB, iv=decrypted[: self._bytes_slice])

        return cipher.decrypt(decrypted[self._bytes_slice :]).decode()
