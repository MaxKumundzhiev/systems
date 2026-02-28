from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, Tuple, Optional
from dataclasses import dataclass
from collections import deque

import asyncio

T = TypeVar("T")
CommitTag = TypeVar("CommitTag")


@dataclass
class Batch(Generic[T, CommitTag]):
    items: List[T]
    commit_tag: CommitTag


class Producer(ABC, Generic[T, CommitTag]):
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    async def next(self) -> Batch[T, CommitTag]:
        pass

    @abstractmethod
    async def commit(self, commit_tag: CommitTag) -> None:
        pass


class Consumer(ABC, Generic[T]):
    MAX_ITEMS: int = 1000

    @abstractmethod
    async def process(self, items: List[T]) -> None:
        pass


class PipeProcessorAdvanced(Generic[T, CommitTag]):
    """
    Обработчик пайплайна данных от Producer к Consumer с параллельной обработкой.

    Использует ограниченные очереди для предотвращения переполнения памяти при
    дисбалансе скоростей чтения и обработки данных.
    """

    def __init__(
        self,
        producer: Producer[T, CommitTag],
        consumer: Consumer[T],
        max_batch_queue_size: int = 1000,
        max_commit_queue_size: int = 10000,
    ):
        self.producer = producer
        self.consumer = consumer
        self.max_batch_queue_size = max_batch_queue_size
        self.max_commit_queue_size = max_commit_queue_size

    async def pipe(self) -> None:
        """
        Параллельная обработка: Read, Process и Commit работают одновременно.
        """
        buffer: deque[T] = deque()
        pending_commits: deque[Tuple[CommitTag, int]] = deque()
        # Очереди для передачи данных между тасками
        batch_queue: asyncio.Queue[Optional[Batch[T, CommitTag]]] = asyncio.Queue(
            maxsize=self.max_batch_queue_size
        )
        commit_queue: asyncio.Queue[Optional[CommitTag]] = asyncio.Queue(
            maxsize=self.max_commit_queue_size
        )

        async def read_task():
            """Читает данные из Producer и кладет в batch_queue."""
            try:
                while True:
                    batch = await self.producer.next()
                    if not batch.items:
                        break
                    await batch_queue.put(batch)
            finally:
                await batch_queue.put(None)

        async def process_task():
            """Обрабатывает данные из batch_queue, кладет теги в commit_queue."""
            nonlocal buffer, pending_commits

            try:
                while (batch := await batch_queue.get()) is not None:
                    buffer.extend(batch.items)
                    pending_commits.append((batch.commit_tag, len(batch.items)))

                    while len(buffer) >= self.consumer.MAX_ITEMS:
                        items = self._extract_items(buffer, self.consumer.MAX_ITEMS)
                        await self.consumer.process(items)
                        await self._send_ready_commits(
                            pending_commits, commit_queue, len(items)
                        )

                # Обработка остатков после завершения чтения
                if buffer:
                    items = list(buffer)
                    buffer.clear()
                    await self.consumer.process(items)

                    while pending_commits:
                        tag, _ = pending_commits.popleft()
                        await commit_queue.put(tag)
            finally:
                await commit_queue.put(None)  # Сигнал завершения для commit_task

        async def commit_task():
            """Читает теги из commit_queue и делает producer.commit()."""
            while (tag := await commit_queue.get()) is not None:
                await self.producer.commit(tag)

        tasks = [
            asyncio.create_task(read_task(), name="reader"),
            asyncio.create_task(process_task(), name="processor"),
            asyncio.create_task(commit_task(), name="committer"),
        ]

        await self._wait_with_cancellation(tasks)

    def _extract_items(self, buffer: deque, count: int) -> List:
        return [buffer.popleft() for _ in range(count)]

    async def _send_ready_commits(
        self, pending_commits: deque, commit_queue: asyncio.Queue, processed_count: int
    ) -> None:
        while pending_commits and processed_count > 0:
            tag, count = pending_commits[0]
            if count <= processed_count:
                await commit_queue.put(tag)
                pending_commits.popleft()
                processed_count -= count
            else:
                pending_commits[0] = (tag, count - processed_count)
                processed_count = 0

    async def _wait_with_cancellation(self, tasks: list) -> None:
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)

        for task in pending:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        for task in done:
            if task.exception():
                raise task.exception()
