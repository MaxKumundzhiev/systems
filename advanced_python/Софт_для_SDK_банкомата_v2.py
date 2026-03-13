from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from threading import Lock
import heapq
import uuid
from datetime import datetime, timedelta


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
    def __init__(self, sdk: SDK) -> None:
        self._sdk = sdk

    def withdraw(self): ...

    def reserve(self): ...
