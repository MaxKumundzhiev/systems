import io
from abc import ABC, abstractmethod


## interfaces ##
class Folder(ABC):
    """
    1 KB --> 1024 BYTE
    1 MB --> 1024 KB

    1 MB   --> 1024 BYTE * 1024 BYTE
    100 MB --> 1 MB * 100 --> 1024 BYTE * 1024 BYTE * 100 ~= 10^22 BYTE
    """

    MAX_FILE_SIZE: int = 1024 * 1024 * 100  # 100 MB

    @abstractmethod
    async def write_file(self, name: str, data: bytes) -> None:
        raise NotImplementedError

    @abstractmethod
    async def read_file(self, name: str) -> bytes:
        raise NotImplementedError

    @abstractmethod
    async def list_files(self) -> list[str]:
        raise NotImplementedError


class Processor(ABC):
    @abstractmethod
    async def compress_and_encrypt(self, data: bytes) -> bytes:
        raise NotImplementedError

    @abstractmethod
    async def decrypt_and_uncompress(self, data: bytes) -> bytes:
        raise NotImplementedError


## implementation ##
class BackupManager:
    def __init__(self, folder: Folder, processor: Processor) -> None:
        self._folder = folder
        self._processor = processor

    async def backup(self, in_stream: io.BufferedIOBase) -> None:
        pass
