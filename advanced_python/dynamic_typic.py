from typing import TypeVar, Generic, List


"""
TypeVar - way to define 'abstract' (some) type, which gonna be defined while compilation
Generic - way to apply TypeVar within some object
"""

T = TypeVar("T")  # defined some type named T


class WareHouse(Generic[T]):
    def __init__(self) -> None:
        self._items: List[T] = []

    def add_item(self, item: T) -> None:
        if not isinstance(item, T):
            raise TypeError
        self._items.append(item)
        return

    def get_last_item(self) -> T | None:
        if not bool(self._items):
            return
        return self._items[-1]


tyres_warehouse = WareHouse[str]()
money_warehouse = WareHouse[int]()

tyres_warehouse.add_item("Michlen")
tyres_warehouse.get_last_item()
tyres_warehouse.add_item(10)  # static error
# assert tyres_warehouse.add_item(10) == TypeError
