import asyncio
import io
import time
from abc import ABC, abstractmethod

from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

from collections.abc import AsyncIterator
from typing import Union


class Processor(ABC):
    """Абстрактный интерфейс для обработки данных (сжатие/шифрование)."""

    @abstractmethod
    def compress_and_encrypt(self, data: bytes) -> bytes:
        """Сжимает и шифрует данные."""
        pass

    @abstractmethod
    def decrypt_and_uncompress(self, data: bytes) -> bytes:
        """Расшифровывает и распаковывает данные."""
        pass


class Folder(ABC):
    """Абстрактный интерфейс для работы с хранилищем файлов."""

    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MiB

    @abstractmethod
    async def write_file(self, name: str, data: bytes) -> None:
        """Записывает файл в хранилище."""
        pass

    @abstractmethod
    async def read_file(self, name: str) -> bytes:
        """Читает файл из хранилища."""
        pass

    @abstractmethod
    async def list_files(self) -> list[str]:
        """Возвращает список всех файлов в хранилище."""
        pass


"""
operations
    I/O - read_files, write_files
    CPU - compress, decompress

for backup we want read by chunks, compress (by chunks) and write by chunks
"""


class BackupManager:
    def __init__(self, folder: Folder, processor: Processor):
        self._folder = folder
        self._processor = processor

    async def _read_by_chunks(self, in_stream: io.BufferedIOBase) -> bytes:
        """async iterator which read in stream bytes by chunks."""
        async def __aenter__(self):
            ...
        
        async def __aexit__(self):
            ...

        

    async def backup(self, in_stream: io.BufferedIOBase) -> None:
        pass

    async def restore(self, out_stream: io.BufferedIOBase) -> None:
        pass
