from collections import OrderedDict


class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        # Перемещение последнего использованного элемента в начало очереди
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            # Если ключ уже существует, обновить значение и переместить в конец
            del self.cache[key]
        elif len(self.cache) >= self.capacity:
            # Если достигнута максимальная вместимость, удалить первый элемент (наиболее давно использовавшийся)
            self.cache.popitem(last=False)
        # Добавить или обновить элемент
        self.cache[key] = value
