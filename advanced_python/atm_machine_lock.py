"""
Представь у нас есть банкомат (ATM)
ATM умеет рабоать с физическими операциями и операциями по сети

Сейчас у нас есть 2 оперции
    - физически снять деньги (withdraw)
    - зарезервировать сумму денег (reserve)

Нам необходимо реализовать интерфейсы этих 2 операций
"""

from enum import StrEnum
from dataclasses import dataclass
from abc import ABC, abstractmethod
from datetime import date

from collections import defaultdict
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import asyncio


class OperationType(StrEnum):
    withdraw = "withdraw"
    reserve = "reserve"


@dataclass
class Request:
    opr_type: OperationType
    banknote: str
    quantity: int


## interfaces ##
class ATMRepository(ABC):
    @abstractmethod
    async def withdraw(self, banknote: str, quantity: int) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def reserve(self, banknote: str, quantity: int) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def get_storage_state(self) -> dict[str, int]:
        raise NotImplementedError

    @abstractmethod
    async def get_reserved_state(self) -> dict[date, tuple[str, int]]:
        raise NotImplementedError


class ATM(ABC):
    @abstractmethod
    async def handle_request(self, request: Request) -> bool:
        raise NotImplementedError


## implementation ##
class SimpleATMRepository(ATMRepository):
    def __init__(
        self, banknotes: list[str] = ["5000"], quantities: list[int] = [5]
    ) -> None:
        self._storage: dict[str, int] = {
            banknote: quantity for banknote, quantity in zip(banknotes, quantities)
        }
        self._reserved: dict[date, tuple[str, int]] = {}

    async def withdraw(self, banknote: str, quantity: int) -> bool:
        if banknote in self._storage and quantity <= self._storage.get(banknote, 0):
            self._storage[banknote] -= quantity
            return True
        return False

    async def reserve(self, banknote: str, quantity: int) -> bool:
        if banknote in self._storage and quantity <= self._storage.get(banknote, 0):
            self._storage[banknote] -= quantity
            self._reserved[date.today()] = (banknote, quantity)
            return True
        return False

    async def get_storage_state(self) -> dict[str, int]:
        return self._storage

    async def get_reserved_state(self) -> dict[date, tuple[str, int]]:
        return self._reserved


class LocksPoolManager:
    DEFAULT_POOL_SIZE: int = 512

    def __init__(self, pool_size: int = DEFAULT_POOL_SIZE) -> None:
        self._locks = [asyncio.Lock() for _ in range(pool_size)]
        self._pool_size = pool_size

    def _index(self, banknout: str) -> int:
        return hash(banknout) % self._pool_size

    @asynccontextmanager
    async def get_lock(self, banknout: str) -> AsyncIterator[None]:
        idx = self._index(banknout)
        lock = self._locks[idx]

        async with lock:
            yield


class ATMImpl(ATM):
    """
    1. глобальный лок на всю машину
        self._lock: asyncio.Lock = asyncio.Lock()
        проблема
            конкурентные запросы будут работать последовательно

    2. лок на тип опреации
        self._storage_lock: asyncio.Lock = asyncio.Lock()
        self._reserved_lock: asyncio.Lock = asyncio.Lock()
        Значит эти две операции теперь могут идти параллельно, потому что используют разные локи.
        проблема
            как раз в том, что они работают с связанным состоянием (storage & reserved).

    3. лок на номинал
        можно создать словарь где ключом будет номинал а значением будет лок
        self._locks: dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)

    4. лок менеджер
    """

    def __init__(
        self, repo: ATMRepository, locks_pool_manager: LocksPoolManager
    ) -> None:
        self._repo = repo
        self._locks = locks_pool_manager

    async def handle_request(self, request: Request) -> bool:
        async with self._locks.get_lock(request.banknote):
            if request.opr_type == OperationType.withdraw:
                return await self._repo.withdraw(request.banknote, request.quantity)
            else:
                return await self._repo.reserve(request.banknote, request.quantity)


async def scenario():
    locks_pool_manager = LocksPoolManager()
    repo = SimpleATMRepository(banknotes=["5000"], quantities=[1])
    atm = ATMImpl(repo, locks_pool_manager)

    req = Request(opr_type=OperationType.withdraw, banknote="5000", quantity=1)
    start_event = asyncio.Event()

    tasks = [
        atm.handle_request(req),
        atm.handle_request(req),
    ]

    await asyncio.sleep(0)
    start_event.set()

    res = await asyncio.gather(*tasks, return_exceptions=True)
    print(res)


if __name__ == "__main__":
    asyncio.run(scenario())
