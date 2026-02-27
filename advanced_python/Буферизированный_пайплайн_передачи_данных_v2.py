from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List
from dataclasses import dataclass


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


class PipeProcessor(Generic[T, CommitTag]):
    def __init__(
        self,
        producer: Producer[T, CommitTag],
        consumer: Consumer[T],
        max_queue_size: int = 1000,
        max_commit_queue_size: int = 1000,
    ) -> None:
        self.producer = producer
        self.consumer = consumer
        self.max_queue_size = max_queue_size
        self.max_commit_queue_size = max_commit_queue_size

    async def pipe(self): ...
