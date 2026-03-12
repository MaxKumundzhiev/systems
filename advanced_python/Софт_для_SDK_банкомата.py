"""
Ты разрабатываешь программное обеспечение для физического банкомата.
Это не клиент-серверное приложение, а код, который крутится непосредственно на «железе» (Embedded/IoT контекст).

Как устроен банкомат:
    Внутри находятся кассеты с купюрами
    Каждая кассета настроена на один номинал: 50, 100, 500, 1000, 5000 рублей
    Деньги выдаются через диспенсер (лоток выдачи)
    Управление механикой происходит через предоставленный SDK
    Необходимо реализовать класс ATM, который управляет процессом выдачи наличных.

Основные требования:
    При инициализации банкомат должен понять, сколько денег в нем сейчас находится.
    То есть может быть ситуация, что не хватает купюр для выдачи суммы

    Реализовать метод withdraw(amount), который
    Проверяет, можно ли выдать запрошенную сумму имеющимися купюрами
        Если можно — отсчитывает купюры, перемещает их в лоток и открывает его
        Если нельзя (нет нужных номиналов или недостаточно средств) — выбрасывает ошибку, не перемещая купюры

Имей в виду
    Метод sdk.count_banknotes(...) — это механическая операция. Банкомат физически пересчитывает купюры в кассете. Это занимает 1-2 минуты
    Метод withdraw должен работать быстро (пользователь не будет ждать 2 минуты у экрана)
    Нельзя вызывать count_banknotes при каждой выдаче денег. Нам нужно придумать, как хранить состояние (inventory) в памяти приложения и синхронизировать его с железом

Ход мыслей
    из улсовия, есть наминалы, есть сдк
    1. при инициализации нужно считать баланс по наминалам
    2. реализовать withdraw(amount) + диспенсер + обновлять баланс

    у нас может быть хэш мэпа для хранения состояния кассет + баланс
    внутри ATM имплементации

    при инициализации atm --> sdk.count_banknotes(...) --> hashmap по номиналам
    на каждое снятие
        нужно придумать алгоритм для рассчета есть ли запрашиваемая сумма в hashmap
        если да
            move_banknote_to_dispenser
            open_dispenser
"""

from abc import ABC, abstractmethod


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


# Решение пишем ниже
class HardwareError(Exception):
    """Исключение для ошибок аппаратного обеспечения банкомата."""

    pass


class FatalError(Exception):
    """Фатальная ошибка аппаратуры: банкомат заблокирован, требуется обслуживание."""

    pass


class InsufficientAmountError(Exception):
    """Исключение для ошибок недостатка средсв в ATM."""

    pass


class ATM:
    BANKNOUTS = [50, 100, 1000, 5000]

    def __init__(self, sdk: SDK) -> None:
        self._sdk = sdk
        self._inventory: dict[int, int] = {
            banknote: self._sdk.count_banknotes(banknote) for banknote in self.BANKNOUTS
        }
        self._balance: int = sum(
            self._sdk.count_banknotes(banknote) for banknote in self.BANKNOUTS
        )

    def withdraw(self, amount: int) -> None:
        is_sum_available = self._sum_available(amount)
        if not is_sum_available:
            raise InsufficientAmountError

        nominals: list[tuple[int, int]] = self._count_quantity_of_banknotes(amount)
        for banknote, count in nominals:
            self._sdk.move_banknote_to_dispenser(banknote, count)
            self._balance -= banknote * count
            self._inventory[banknote] -= count
        self._sdk.open_dispenser()
        return None

    def _sum_available(self, amount: int) -> bool:
        return self._balance >= amount

    def _count_quantity_of_banknotes(self, req_amount: int) -> list[tuple[int, int]]:
        to_desposal: list[tuple[int, int]] = []

        curr_amount = 0
        for banknote in reversed(self.BANKNOUTS):
            available_banknotes = self._inventory[banknote]
            used_banknotes = 0

            while curr_amount != req_amount and available_banknotes > 0:
                curr_amount += banknote
                available_banknotes -= 1
                used_banknotes += 1

            to_desposal.append((banknote, used_banknotes))

        return to_desposal


"""
from abc import ABC, abstractmethod
from typing import Optional

# Банкомат, который заряжается кассетами с купюрами, с нашим приложением на борту 
# должен уметь выдавать купюры для заданной суммы или отвечать отказом
# При выдаче купюры списываются с баланса банкомата.
# Допустимые номиналы: 50₽, 100₽, 500₽, 1000₽, 5000₽.
# Устройство банкомата:
# - деньги расположены в кассетах внутри банкомата, которые загружает инкассатор и перезагружает банкомат;
# - в каждой кассете лежат купюры своего номинала;
# - банкомат может подсчитать оставшиеся в кассетах банкноты, но эта операция занимает продолжительное время – её стоит вызывать как можно реже.

# API для взаимодействия с аппаратурой банкомата.
# интерфейс SDK может быть изменён/расширен по договорённости сторон, если это необходимо
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


# Решение пишем ниже
class HardwareError(Exception):
    """Исключение для ошибок аппаратного обеспечения банкомата."""
    pass


class FatalError(Exception):
    """Фатальная ошибка аппаратуры: банкомат заблокирован, требуется обслуживание."""
    pass


class ATM:
    DENOMINATIONS: list[int] = [5000, 1000, 500, 100, 50]

    def __init__(self, sdk: SDK):
        self._blocked = False
        self._sdk = sdk
        self._balance: dict[int, int] = {nominal:sdk.count_banknotes(nominal) for nominal in self.DENOMINATIONS}
    
    def withdraw(self, amount: int) -> bool:
        if amount <= 0:
            return False
        
        if self._blocked:
            raise FatalError
        
        requred: Optional[dict[int, int]] = self._count_banknotes(amount)
        if not required:
            return False
        
        try:
            for denomination, count in required.items():
                self._sdk.move_banknote_to_dispenser(denomination, count)
            
            self._sdk.open_dispenser()
            
            for denomination, count in required.items():
                self._balance[denomination] -= count

        except HardwareError:
            try:
                self._sdk.return_all_from_dispenser()
            except HardwareError:
                self._blocked = True
                raise FatalError
            return False

    
    def _count_banknotes(self, amount: int) -> Optional[dict[int, int]]:
        remaining: int = amount
        required: dict[int, int] = {}

        for denomination in self.DENOMINATIONS:
            needed: int = remaining // denomination
            available: int = self._balance[denomination]

            to_use = min(needed, available)
            if to_use > 0:
                remaining -= denomination * to_use
                required[denomination] = to_use
        
        if remaining > 0:
            return None
        return required
"""