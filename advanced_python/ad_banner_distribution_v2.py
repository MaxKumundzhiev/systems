# https://algocode.io/problem/python-ac-discrete-distribution-2?courseId=yandex-advanced-code-python&roadmapId=yandex


import bisect
import random
import threading
from collections.abc import Callable
from contextlib import contextmanager
from typing import Generic, TypeVar

T = TypeVar("T")
RandomGenerator = Callable[[], float]


class RWLock:
    """Read-Write Lock: много читателей одновременно, писатель один в момент времени"""

    def __init__(self) -> None:
        self._ready = threading.Condition()
        self._readers = 0
        self._writers = 0

    @contextmanager
    def read_access(self):
        with self._ready:
            while self._writers:
                self._ready.wait()
            self._readers += 1
        try:
            yield
        finally:
            with self._ready:
                self._readers -= 1
                if not self._readers:
                    self._ready.notify_all()

    @contextmanager
    def write_access(self):
        with self._ready:
            while self._writers or self._readers:
                self._ready.wait()
            self._writers = 1
        try:
            yield
        finally:
            with self._ready:
                self._writers = 0
                self._ready.notify_all()


class DiscreteDistributionSamplerConcurrent(Generic[T]):
    """Потокобезопасная версия DiscreteDistributionSampler.

    Использует RWLock: множество потоков могут вызывать sample() параллельно,
    add() получает эксклюзивный доступ.
    """

    def __init__(
        self,
        objects_with_weights: list[tuple[T, float]],
        random_generator: RandomGenerator = random.random,
    ) -> None:
        self._lock = RWLock()
        self._random_generator = random_generator
        self._objects: list[T] = []
        self._prefix: list[float] = []
        self._total_weight = 0.0

        for obj, weight in objects_with_weights:
            self._add(obj, weight)

    def _add(self, obj: T, weight: float) -> None:
        if weight <= 0:
            raise ValueError("weight must be > 0")
        self._objects.append(obj)
        self._total_weight += float(weight)
        self._prefix.append(self._total_weight)

    def add(self, obj: T, weight: float) -> None:
        with self._lock.write_access():
            self._add(obj, weight)

    def sample(self) -> T:
        with self._lock.read_access():
            if not self._objects:
                raise ValueError("No objects to sample")
            x = self._random_generator() * self._total_weight
            i = bisect.bisect_right(self._prefix, x)
            return self._objects[i]
