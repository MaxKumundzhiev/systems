from collections import deque
from typing import TypeVar, Generic, List, Tuple
from dataclasses import dataclass

from abc import ABC, abstractmethod


T = TypeVar("T")
CommitTag = TypeVar("CommitTag")


"""
producer.next()
--> Batch([1, 2, 3], 1)
--> Batch([4, 5, 6], 2)


by fact a generic with TypeVar is a contract for the ancestors (or interfaces which will implement a logic)
"""


@dataclass
class Batch(Generic[T, CommitTag]):
    items: List[T]
    commit_tag: CommitTag


class Producer(ABC, Generic[T, CommitTag]):
    @abstractmethod
    async def next(self) -> Batch[T, CommitTag]:
        """Returns batch of items"""
        pass

    async def commit(self, commit_tag: CommitTag) -> None:
        """Confirms batch was sent to consumer."""
        pass


class Consumer(ABC, Generic[T]):
    MAX_ITEMS: int = 1000

    async def process(self, items: List[T]) -> None:
        pass


import asyncio
from abc import ABC, abstractmethod
from typing import List, TypeVar, Generic, Tuple, Optional
from dataclasses import dataclass
from collections import deque

# --- КОНТРАКТЫ (INTERFACES) ---
# Не меняй этот блок кода. Используй эти классы как контракт.

T = TypeVar("T")
CommitTag = TypeVar("CommitTag")


@dataclass
class Batch(Generic[T, CommitTag]):
    """Батч данных с тегом для коммита"""

    items: List[T]
    commit_tag: CommitTag


class Producer(ABC, Generic[T, CommitTag]):
    """Источник данных. Гарантирует, что batch.items <= Consumer.MAX_ITEMS"""

    @abstractmethod
    async def next(self) -> Batch[T, CommitTag]:
        """Возвращает следующий батч. Если items пустой — данные закончились."""
        pass

    @abstractmethod
    async def commit(self, commit_tag: CommitTag) -> None:
        """Подтверждает обработку батча."""
        pass


class Consumer(ABC, Generic[T]):
    """Потребитель данных."""

    # Максимальный размер пачки, которую может принять process
    MAX_ITEMS = 1000

    @abstractmethod
    async def process(self, items: List[T]) -> None:
        """Обрабатывает список элементов."""
        pass


# ------

"""
-->  queue  <--
prov        cons

while True:
deque.add(chunk)

chunk = provider.next() (<= Consumer.MAX_ITEMS)
"""


class PipeProcessor(Generic[T, CommitTag]):
    """
    Sequential processing of batches.
    """

    def __init__(self, producer: Producer[T, CommitTag], consumer: Consumer[T]) -> None:
        self.producer = producer
        self.consumer = consumer
        self.max_batch_size = self.consumer.MAX_ITEMS

    async def pipe(self):
        buffer: deque[T] = deque()
        pending_commits: deque[Tuple[CommitTag, int]] = deque()

        while True:
            batch: Batch = await self.producer.next()
            if not batch.items:
                break

            buffer.extend(batch.items)
            pending_commits.append((batch.commit_tag, len(batch.items)))

            # Обрабатываем буфер порциями по MAX_ITEMS
            while len(buffer) >= self.max_batch_size:
                items = self._extract_items_from_buffer(buffer, self.max_batch_size)
                await self.consumer.process(items)
                await self._commit_ready(pending_commits, len(items))

        # Обрабатываем остатки
        if buffer:
            """
            items = list(buffer)
            buffer.clear()
            """
            items = self._extract_items_from_buffer(buffer, len(buffer))
            await self.consumer.process(items)

            # Коммитим все оставшиеся теги
            while pending_commits:
                tag, _ = pending_commits.popleft()
                await self.producer.commit(tag)

    def _extract_items_from_buffer(self, buffer: deque[T], cnt: int) -> List[T]:
        return [buffer.popleft() for _ in range(cnt)]

    async def _commit_ready(
        self, pending_commits: deque[Tuple[CommitTag, int]], processed_count: int
    ) -> None:
        while pending_commits and processed_count > 0:
            tag, cnt = pending_commits[0]
            if cnt <= processed_count:
                await self.producer.commit(tag)
                pending_commits.popleft()
                processed_count -= cnt
            else:
                pending_commits[0] = (tag, cnt - processed_count)
                processed_count = 0
        return
