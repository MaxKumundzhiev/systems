"""
Assume we working with a service which showcase an add to the user.
The system store a set of adds (from our customers), which should be shown to the user.
Each add has its own weight (assume the more customer paid for the add the more weight is).

At the same time we want to add some randomicy.

Design and implement a system to show adds encountering adds weights.
"""

import random
from abc import abstractmethod, ABC
from dataclasses import dataclass


## interfaces ##
@dataclass
class Adverisment:
    id: str
    weight: int


class AdverismentRepo(ABC):
    @abstractmethod
    def pick(self) -> tuple[int, str]:
        raise NotImplementedError


class AdverismentService(ABC):
    @abstractmethod
    def get_advertisment(self) -> tuple[int, str]:
        raise NotImplementedError


## implementation ##
class SimpleAdverismentRepo(AdverismentRepo):
    def __init__(self, adverisments: list[Adverisment]) -> None:
        self._prefix: list[tuple[int, str]] = [(0, "")]

        total = 0
        for a in adverisments:
            total += a.weight
            self._prefix.append((total, a.id))

        self._total_weight = total

    def pick(self) -> tuple[int, str]:
        target = random.random() * self._total_weight
        l, r = 0, len(self._prefix)

        while r - l > 1:
            m = (l + r) // 2
            w, _ = self._prefix[m]
            if w <= target:
                l = m
            else:
                r = m
        return self._prefix[l]

    def add_new_add(self, ad: Adverisment) -> None:
        self._total_weight += ad.weight
        self._prefix.append((self._total_weight, ad.id))

    def get_prefix(self):
        return self._prefix


class AdverismentServiceImpl(AdverismentService):
    def __init__(self, repo: AdverismentRepo) -> None:
        self._repo = repo

    def get_advertisment(self):
        return self._repo.pick()


if __name__ == "__main__":
    ads = [
        Adverisment(id="A", weight=1),
        Adverisment(id="B", weight=2),
        Adverisment(id="C", weight=3),
    ]

    repo = SimpleAdverismentRepo(adverisments=ads)
    service = AdverismentServiceImpl(repo)
    print(repo.get_prefix())
    for _ in range(5):
        weight, id = service.get_advertisment()
        print(weight, id)

    repo.add_new_add(Adverisment(id="D", weight=10))
    print(repo.get_prefix())
    for _ in range(5):
        weight, id = service.get_advertisment()
        print(weight, id)


"""
import bisect
import random
from typing import Generic, TypeVar, Callable

T = TypeVar('T')
RandomGenerator = Callable[[], float]


class DiscreteDistributionSampler(Generic[T]):
    def __init__(
        self, 
        objects_with_weights: list[tuple[T, float]],
        random_generator: RandomGenerator = random.random
    ) -> None:
        self._objects: list[T] = []
        self._prefix: list[float] = []

        total: float = 0.0
        for obj, w in objects_with_weights:
            if w <= 0:
                raise ValueError("weight must be > 0")
            total += w
            self._objects.append(obj)
            self._prefix.append(total)
        
        self._total_weight = total
        self._random_generator = random_generator

    def add(self, obj: T, weight: float) -> None:
        if weight <= 0:
            raise ValueError("weight must be > 0")

        self._objects.append(obj)
        self._total_weight += float(weight)
        self._prefix.append(self._total_weight)
        
    def sample(self) -> T:
        if not self._objects:
            raise ValueError("No objects to sample")

        x = self._random_generator() * self._total_weight
        i = bisect.bisect_right(self._prefix, x)
        return self._objects[i]
"""
