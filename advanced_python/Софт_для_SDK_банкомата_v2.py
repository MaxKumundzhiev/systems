from abc import ABC, abstractmethod
from dataclasses import dataclass
from threading import Lock
import heapq
import uuid
import time


class HardwareError(Exception):
    pass


class RetriableError(Exception):
    pass


class FatalError(Exception):
    pass


@dataclass
class Reservation:
    id: str
    amount: int
    banknotes: dict[int, int]
    expires_at: float


class SDK(ABC):
    @abstractmethod
    def count_banknotes(self, banknote: int) -> int:
        pass

    @abstractmethod
    def move_banknote_to_dispenser(self, banknote: int, count: int) -> None:
        pass

    @abstractmethod
    def open_dispenser(self) -> None:
        pass

    @abstractmethod
    def return_all_from_dispenser(self) -> None:
        pass


class ATM:
    DENOMINATIONS = (5000, 1000, 500, 100, 50)
    RESERVATION_TTL_MINUTES = 15

    def __init__(self, sdk: SDK):
        self.sdk = sdk
        self.balance = {d: sdk.count_banknotes(d) for d in self.DENOMINATIONS}
        self.reserved = {d: 0 for d in self.DENOMINATIONS}
        self.reservations: dict[str, Reservation] = {}
        self._exp_heap: list[tuple[float, str]] = []
        self._lock = Lock()
        self._blocked = False

    def _cancel_unlocked(self, rid: str) -> bool:
        """Приватный метод для отмены резерва. Вызывается ТОЛЬКО под блокировкой."""
        if res := self.reservations.pop(rid, None):
            for den, count in res.banknotes.items():
                self.reserved[den] -= count
            return True
        return False

    def _clean_expired(self):
        now = time.time()
        while self._exp_heap and self._exp_heap[0][0] < now:
            _, rid = heapq.heappop(self._exp_heap)
            self._cancel_unlocked(rid)

    def _calc_banknotes(self, amount: int) -> dict[int, int] | None:
        req = {}
        for den in self.DENOMINATIONS:
            if amount == 0:
                break
            if to_use := min(amount // den, self.balance[den] - self.reserved[den]):
                req[den] = to_use
                amount -= to_use * den
        return req if amount == 0 else None

    def reserve(self, amount: int) -> str | None:
        if amount <= 0:
            return None
        with self._lock:
            if self._blocked:
                raise FatalError("ATM blocked")
            self._clean_expired()
            if not (req_bn := self._calc_banknotes(amount)):
                return None

            rid = uuid.uuid4().hex
            exp = time.time() + (self.RESERVATION_TTL_MINUTES * 60)
            res = Reservation(rid, amount, req_bn, exp)

            for den, count in req_bn.items():
                self.reserved[den] += count
            self.reservations[rid] = res
            heapq.heappush(self._exp_heap, (exp, rid))
            return rid

    def cancel_reservation(self, rid: str) -> bool:
        with self._lock:
            return self._cancel_unlocked(rid)

    def withdraw_reserved(self, rid: str) -> tuple[bool, int | None]:
        with self._lock:
            if self._blocked:
                raise FatalError("ATM blocked")
            if not (res := self.reservations.get(rid)):
                return False, None

            if time.time() > res.expires_at:
                self._cancel_unlocked(rid)  # Вызываем безопасный метод без лока
                return False, None

            req_bn = res.banknotes
            for den, count in req_bn.items():
                self.reserved[den] -= count
                self.balance[den] -= count
            del self.reservations[rid]

        # Обращение к железу происходит ВНЕ блокировки, чтобы не стопорить резервы
        try:
            self._dispense(req_bn)
        except RetriableError:
            self._rollback(req_bn, res)
            return False, None
        return True, res.amount

    def withdraw(self, amount: int) -> tuple[bool, int | None]:
        if amount <= 0:
            return False, None
        with self._lock:
            if self._blocked:
                raise FatalError("ATM blocked")
            self._clean_expired()
            if not (req_bn := self._calc_banknotes(amount)):
                return False, None

            for den, count in req_bn.items():
                self.balance[den] -= count

        try:
            self._dispense(req_bn)
        except RetriableError:
            self._rollback(req_bn)
            return False, None
        return True, amount

    def _dispense(self, banknotes: dict[int, int]):
        try:
            for den, count in banknotes.items():
                if count > 0:
                    self.sdk.move_banknote_to_dispenser(den, count)
            self.sdk.open_dispenser()
        except HardwareError as err:
            try:
                self.sdk.return_all_from_dispenser()
            except HardwareError:
                with self._lock:
                    self._blocked = True
                raise FatalError("Fatal rollback failure") from err
            raise RetriableError("Dispense failed") from err

    def _rollback(self, banknotes: dict[int, int], res: Reservation | None = None):
        with self._lock:
            for den, count in banknotes.items():
                self.balance[den] += count
                if res:
                    self.reserved[den] += count
            if res:
                self.reservations[res.id] = res
                heapq.heappush(self._exp_heap, (res.expires_at, res.id))

    def get_balance(self) -> dict[int, int]:
        with self._lock:
            return self.balance.copy()

    def get_reserved(self) -> dict[int, int]:
        with self._lock:
            return self.reserved.copy()

    def get_available_balance(self) -> dict[int, int]:
        with self._lock:
            return {d: self.balance[d] - self.reserved[d] for d in self.DENOMINATIONS}
