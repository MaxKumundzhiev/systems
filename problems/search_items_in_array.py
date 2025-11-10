"""
assume we have the catalog of products with their name and price (per one) accordingly.
we have to create an interface to compile following API:


- get_price(item_name) -> float | int | None
- add_item(item_name, item_price) -> None * if product already exists it will rewrite the record

Requirements
- the data structure where we have to store items should be array of tuples
- search of items should work for log(n)
"""

from typing import List, Tuple

from asyncpg import NoDataFoundError


from typing import List, Tuple, Optional


class Catalog:
    def __init__(self) -> None:
        self.items: List[Tuple[str, float]] = []

    def _search(self, lookup_item_name: str) -> Optional[int]:
        """Выполняет бинарный поиск и возвращает индекс элемента или None, если элемент отсутствует."""
        left, right = 0, len(self.items) - 1
        while left <= right:
            mid = (left + right) // 2
            current_name = self.items[mid][0]

            if current_name == lookup_item_name:
                return mid
            elif current_name < lookup_item_name:
                left = mid + 1
            else:
                right = mid - 1

        return None

    def get_price(self, item_name: str) -> Optional[float]:
        """Получает цену указанного товара, если он присутствует в каталоге."""
        index = self._search(item_name)
        if index is not None:
            return self.items[index][1]
        return None

    def add_item(self, item_name: str, item_price: float) -> None:
        """
        Метод добавляет новое наименование товара в каталог. Если товар уже есть,
        переписывает существующую запись новым значением цены.
        """
        index = self._search(item_name)
        if index is not None:
            # Обновляем цену существующего товара
            self.items[index] = (item_name, item_price)
        else:
            # Создаем новый элемент и добавляем его в конец списка
            new_item = (item_name, item_price)
            self.items.append(new_item)
            # После добавления сортируем весь список заново (неэффективно, но минимально нарушает вашу изначальную идею)
            self.items.sort()


catalog = Catalog()
catalog.add_item("Eggs", 2.49)
catalog.add_item("Milk", 1.4)
print(catalog.get_price("Milk"))
print(catalog.get_price("Eggs"))
print(catalog.get_price("Apple"))
catalog.add_item("Apple", 0.79)
print(catalog.get_price("Apple"))
