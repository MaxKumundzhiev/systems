import asyncio
import io
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from concurrent.futures import ThreadPoolExecutor
from typing import Any


## interfaces ##
class Folder(ABC):
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


class BackupManager:
    RAW_CHUNK_SIZE: int = 1024 * 1024  # 1 MB
    MAX_IN_FLIGHT: int = 8

    def __init__(
        self,
        folder: Folder,
        processor: Processor,
        max_workers: int = 4,
    ) -> None:
        self._folder = folder
        self._processor = processor
        self._thread_pool = ThreadPoolExecutor(max_workers=max_workers)

    async def __aenter__(self) -> "BackupManager":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        self._thread_pool.shutdown(wait=True)

    async def backup(self, in_stream: io.BufferedIOBase) -> None:
        in_flight: set[asyncio.Task[tuple[int, bytes]]] = set()
        pending_results: dict[int, bytes] = {}

        next_to_schedule: int = 0
        next_to_write: int = 0

        current_part_idx: int = 0
        current_part: bytearray = bytearray()

        async with asyncio.TaskGroup() as tg:
            async for raw_chunk in self._read_raw_chunks(in_stream):
                task: asyncio.Task[tuple[int, bytes]] = tg.create_task(
                    self._process_chunk(next_to_schedule, raw_chunk)
                )
                in_flight.add(task)
                next_to_schedule += 1

                if len(in_flight) >= self.MAX_IN_FLIGHT:
                    done, _ = await asyncio.wait(
                        in_flight,
                        return_when=asyncio.FIRST_COMPLETED,
                    )

                    for task in done:
                        idx, processed = task.result()
                        pending_results[idx] = processed

                    in_flight -= done

                    current_part_idx, current_part, next_to_write = (
                        await self._drain_ready_chunks(
                            pending_results=pending_results,
                            next_to_write=next_to_write,
                            current_part_idx=current_part_idx,
                            current_part=current_part,
                        )
                    )

            while in_flight:
                done, _ = await asyncio.wait(
                    in_flight,
                    return_when=asyncio.FIRST_COMPLETED,
                )

                for task in done:
                    idx, processed = task.result()
                    pending_results[idx] = processed

                in_flight -= done

                current_part_idx, current_part, next_to_write = (
                    await self._drain_ready_chunks(
                        pending_results=pending_results,
                        next_to_write=next_to_write,
                        current_part_idx=current_part_idx,
                        current_part=current_part,
                    )
                )

        if current_part:
            await self._flush_part(current_part_idx, current_part)

    async def _read_raw_chunks(
        self,
        in_stream: io.BufferedIOBase,
    ) -> AsyncIterator[bytes]:
        loop = asyncio.get_running_loop()

        while True:
            chunk: bytes = await loop.run_in_executor(
                self._thread_pool,
                in_stream.read,
                self.RAW_CHUNK_SIZE,
            )
            if not chunk:
                break
            yield chunk

    async def _process_chunk(self, index: int, raw_chunk: bytes) -> tuple[int, bytes]:
        processed: bytes = await self._processor.compress_and_encrypt(raw_chunk)

        if len(processed) > self._folder.MAX_FILE_SIZE:
            raise ValueError(
                f"processed chunk {index} exceeds max file size: "
                f"{len(processed)} > {self._folder.MAX_FILE_SIZE}"
            )

        return index, processed

    async def _drain_ready_chunks(
        self,
        pending_results: dict[int, bytes],
        next_to_write: int,
        current_part_idx: int,
        current_part: bytearray,
    ) -> tuple[int, bytearray, int]:
        while next_to_write in pending_results:
            processed_chunk: bytes = pending_results.pop(next_to_write)

            if len(current_part) + len(processed_chunk) > self._folder.MAX_FILE_SIZE:
                await self._flush_part(current_part_idx, current_part)
                current_part_idx += 1
                current_part = bytearray()

            current_part.extend(processed_chunk)
            next_to_write += 1

        return current_part_idx, current_part, next_to_write

    async def _flush_part(self, part_idx: int, data: bytearray) -> None:
        file_name = self._part_name(part_idx)
        await self._folder.write_file(file_name, bytes(data))

    async def restore(self, out_stream: io.BufferedIOBase) -> None:
        part_names: list[str] = sorted(
            [
                name
                for name in await self._folder.list_files()
                if name.startswith("part_")
            ]
        )

        for part_name in part_names:
            encrypted_part: bytes = await self._folder.read_file(part_name)
            restored_part: bytes = await self._processor.decrypt_and_uncompress(
                encrypted_part
            )
            out_stream.write(restored_part)

    @staticmethod
    def _part_name(index: int) -> str:
        return f"part_{index:06d}.bin"
