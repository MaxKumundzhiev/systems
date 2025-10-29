"""
there is a list of registered users
we have to check if user is registered or not


Note
    - frequent read (array)
    - binary search for look ups
    - merge sort for sorting
"""


class Interface:
    def __init__(self) -> None:
        self.users = []
    
    def to_register(self, name: str) -> None:
        """Регистрация пользователя с сохранением порядка."""
        # Вставка нового имени сразу в правильное место (сохраняя сортировку)
        idx = 0
        while idx < len(self.users) and self.users[idx] < name:
            idx += 1
        self.users.insert(idx, name)
    
    def is_registered(self, name: str) -> bool:
        """Проверка наличия пользователя методом бинарного поиска."""
        left, right = 0, len(self.users)
        while right - left > 1:
            mid = (left + right) // 2
            curr_name = self.users[mid]
            if curr_name == name:
                return True
            elif curr_name < name:
                left = mid
            else:
                right = mid
        return self.users[left] == name

# Тестирование интерфейса
handler = Interface()
handler.to_register("Alex")
handler.to_register("Bob")
handler.to_register("Max")

print(handler.is_registered("Alex"))  # True
print(handler.is_registered("Bob"))   # True
print(handler.is_registered("Max"))   # True
print(handler.is_registered("Jane"))  # False