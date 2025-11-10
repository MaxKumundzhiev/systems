"""
хэш функция - функция которая получает на вход строку и возвращает число

хэш функция должна
    - Она должна быть последовательной. Допустим, вы передали ей стро-
    ку «апельсины» и получили 4. Это значит, что каждый раз в будущем,
    передавая ей строку «апельсины», вы будете получать 4. Без этого хеш-
    таблица бесполезна.

    - Разным словам в идеале должны соответствовать разные числа


Свяжите воедино хеш-функцию и мас-
сив, и вы получите структуру данных, которая называется хеш-таблицей.
Хеш-таблица станет первой изученной вами структурой данных, с которой
связана дополнительная логика. Массивы и списки напрямую отображают-
ся на адреса памяти, но хеш-таблицы устроены более умно. Они определяют
место хранения элементов при помощи хеш-функций.
"""

"""
assume we have the catalog of products with their name and price (per one) accordingly.
we have to create an interface to compile following API:


- get_price(item_name) -> float | int | None
- add_item(item_name, item_price) -> None * if product already exists it will rewrite the record

Requirements
- the data structure where we have to store items should be array (hashtable)
- search of items should work for O(1)
"""


class Catalog:
    def __init__(self) -> None:
        self.capacity = 10
        self.items = [None] * self.capacity

    def compose_position(self, name: str) -> int:
        return hash(name) % len(self.items)

    def add_item(self, name: str, price: float) -> None:
        pos = self.compose_position(name)
        self.items[pos] = price

    def get_price(self, name: str) -> float | None:
        pos = self.compose_position(name)
        return self.items[pos]


catalog = Catalog()
catalog.add_item("Eggs", 2.49)
catalog.add_item("Milk", 1.4)
print(catalog.get_price("Milk"))
print(catalog.get_price("Eggs"))
print(catalog.get_price("Apple"))
catalog.add_item("Apple", 0.79)
print(catalog.get_price("Apple"))
