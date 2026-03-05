"""
Мы разрабатываем модуль для сохранения резервных копий (бэкапов).

Входные данные: Поток байтов (stream). Полный размер бэкапа может достигать 10 TiB.
Обработка: Перед сохранением данные должны пройти через «Процессор» (сжатие + шифрование). Алгоритм ресурсоемкий, коэффициент сжатия 1.5–3x.
Хранение: Данные сохраняются в холодное сетевое хранилище (аналог S3).
"""

import io
import asyncio

from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from typing import AsyncIterator


## interfaces
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


class Processor(ABC):
    """Абстрактный интерфейс для обработки данных (сжатие/шифрование)."""

    @abstractmethod
    async def compress_and_encrypt(self, data: bytes) -> bytes:
        """Сжимает и шифрует данные."""
        pass

    @abstractmethod
    async def decrypt_and_uncompress(self, data: bytes) -> bytes:
        """Расшифровывает и распаковывает данные."""
        pass


class BackupManager:
    def __init__(
        self, folder: Folder, processor: Processor, max_workers: int = 4
    ) -> None:
        self._folder = folder
        self._processor = processor
        self._thread_pool = ThreadPoolExecutor(max_workers=max_workers)

    async def __aenter__(self) -> "BackupManager":
        return self

    async def __aexit__(self) -> None:
        if self._thread_pool:
            self._thread_pool.shutdown(wait=True)
            self._thread_pool = None

    async def _read_by_chunks(
        self, in_stream: io.BufferedIOBase
    ) -> AsyncIterator[bytes | memoryview]:
        # check if there is any existing thread (cause while async manager is called, it should be spin 4 threads)
        if not self._thread_pool:
            raise SystemError("Manager is closed")

        # get active running event loop
        loop = asyncio.get_running_loop()
        # define empty buffer, where we gonna read in (add) chunks from stream
        buffer = io.BytesIO()
        # fetch max size of buffer (according to max file size)
        current_max_size: int = self._folder.MAX_FILE_SIZE
        # in infite loop read in chunks
        while True:
            data = await loop.run_in_executor(
                self._thread_pool, in_stream.read, current_max_size
            )
            if not data:
                break
            buffer.write(data)
            current_max_size -= len(data)

            if current_max_size <= 0:
                yield buffer.getbuffer()
                buffer = io.BytesIO()
                current_max_size = self._folder.MAX_FILE_SIZE

            # clean up (output) remaining bytes if any
            if current_max_size != self._folder.MAX_FILE_SIZE:
                yield buffer.getbuffer()

    @staticmethod
    def _chunk_name(index: int) -> str:
        return f"chunk_{index}.bin"

    async def backup(self, in_stream: io.BufferedIOBase) -> None:
        index = 0
        async for chunk in self._read_by_chunks(in_stream):
            compressed_chunk = await self._processor.compress_and_encrypt(chunk)
            await self._folder.write_file(self._chunk_name(index), compressed_chunk)
            index += 1

    async def restore(self, out_stream: io.BufferedIOBase) -> None:
        files: list[str] = await self._folder.list_files()
        for chunk_index in range(len(files)):
            compressed_chunk = await self._folder.read_file(
                self._chunk_name(chunk_index)
            )
            decompressed_chunk = await self._processor.decrypt_and_uncompress(
                compressed_chunk
            )
            out_stream.write(decompressed_chunk)
