"""
Представь у нас есть банкомат (ATM)
ATM умеет рабоать с физическими операциями и операциями по сети

Сейчас у нас есть 2 оперции
    - физически снять деньги (withdraw)
    - зарезервировать сумму денег (reserve)

Нам необходимо реализовать интерфейсы этих 2 операций

А теперь представим, что на уровне event loop нам не очень блокироваться
внешняя библиотека или SDK работает синхронно (как в случае с механикой банкомата),
мы не можем просто использовать asyncio — долгий вызов аппаратуры намертво заблокирует Event Loop.
Нам приходится использовать классические потоки ОС (threading).

То есть представим теперь что вместо нашего асинхроннго репозитория
мы должны использовать синхронный sdk
"""

from enum import StrEnum
from dataclasses import dataclass
from abc import ABC, abstractmethod
from datetime import date

from collections import defaultdict
from collections.abc import AsyncIterator, Iterator
from contextlib import asynccontextmanager, contextmanager
from concurrent.futures import ThreadPoolExecutor
import threading

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
class ATMSdk(ABC):
    @abstractmethod
    def withdraw(self, banknote: str, quantity: int) -> bool:
        raise NotImplementedError

    @abstractmethod
    def reserve(self, banknote: str, quantity: int) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_storage_state(self) -> dict[str, int]:
        raise NotImplementedError

    @abstractmethod
    def get_reserved_state(self) -> dict[date, tuple[str, int]]:
        raise NotImplementedError


class ATM(ABC):
    @abstractmethod
    def handle_request(self, request: Request) -> bool:
        raise NotImplementedError


## implementation ##
class SimpleATMSdk(ATMSdk):
    def __init__(
        self, banknotes: list[str] = ["5000"], quantities: list[int] = [5]
    ) -> None:
        self._storage: dict[str, int] = {
            banknote: quantity for banknote, quantity in zip(banknotes, quantities)
        }
        self._reserved: dict[date, tuple[str, int]] = {}

    def withdraw(self, banknote: str, quantity: int) -> bool:
        if banknote in self._storage and quantity <= self._storage.get(banknote, 0):
            self._storage[banknote] -= quantity
            return True
        return False

    def reserve(self, banknote: str, quantity: int) -> bool:
        if banknote in self._storage and quantity <= self._storage.get(banknote, 0):
            self._storage[banknote] -= quantity
            self._reserved[date.today()] = (banknote, quantity)
            return True
        return False

    def get_storage_state(self) -> dict[str, int]:
        return self._storage

    def get_reserved_state(self) -> dict[date, tuple[str, int]]:
        return self._reserved


class LocksPoolManager:
    DEFAULT_POOL_SIZE: int = 512

    def __init__(self, pool_size: int = DEFAULT_POOL_SIZE) -> None:
        self._locks = [threading.Lock() for _ in range(pool_size)]
        self._pool_size = pool_size

    def _index(self, banknout: str) -> int:
        return hash(banknout) % self._pool_size

    @contextmanager
    def get_lock(self, banknout: str) -> Iterator[None]:
        idx = self._index(banknout)
        lock = self._locks[idx]

        with lock:
            yield


class ATMImpl(ATM):
    DEFAULT_MAX_WORKERS: int = 8

    def __init__(
        self,
        sdk: ATMSdk,
        locks: LocksPoolManager,
        max_workers: int = DEFAULT_MAX_WORKERS,
    ) -> None:
        self._sdk = sdk
        self._locks = locks
        self._max_workers = max_workers
        self._workers = ThreadPoolExecutor(max_workers=max_workers)

    """
    идея 1
        изменить логику самого репозитория (sdk)
        и добавить туда threading.Lock() +
        запускать процессы в сервисе через asyncio.to_thread()
        не подходит у нас нет доступа к sdk
    идея 2
        добавить threading.Lock() в сервис
        зупускать в разных потоках
        добавить асинхронную обвертку на синхронные вызовы
    идея 3
        добавить масштабирования через ThreadPoolExecutor
        но лок остается так как sdk нет thread-safe
        и улучшим лок через его пул также
    """

    def _withdraw_sync(self, request: Request) -> bool:
        lock = self._locks.get_lock(request.banknote)
        with lock:
            return self._sdk.withdraw(request.banknote, request.quantity)

    def _reserve_sync(self, request: Request) -> bool:
        lock = self._locks.get_lock(request.banknote)
        with lock:
            return self._sdk.reserve(request.banknote, request.quantity)

    async def handle_request(self, request: Request) -> bool:
        loop = asyncio.get_running_loop()
        if request.opr_type == OperationType.withdraw:
            return await loop.run_in_executor(
                self._workers, self._withdraw_sync, request
            )
        else:
            return await loop.run_in_executor(
                self._workers, self._reserve_sync, request
            )


async def scenario():
    locks_pool_manager = LocksPoolManager()
    sdk = SimpleATMSdk(banknotes=["5000"], quantities=[1])
    atm = ATMImpl(sdk, locks_pool_manager)

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
