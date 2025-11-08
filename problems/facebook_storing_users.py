from string import ascii_lowercase

class Node:
    def __init__(self, val) -> None:
        self.val = val
        self.next = None
        self.prev = None


class LinkedList:
    def __init__(self) -> None:
        self.head = None
        self.tail = None

    def append(self, val) -> None:
        new = Node(val=val)
        if not self.head:
            self.head = self.tail = new
        else:
            old = self.tail
            old.next = new # type: ignore
            new.prev = old # type: ignore
            self.tail = new
        return
    
    def display(self):
        elements = []
        current = self.head
        while current:
            elements.append(current.val)
            current = current.next
        return elements

class Users:
    def __init__(self) -> None:
        self.alphabet = ascii_lowercase
        self.users = [LinkedList() for _ in range(len(self.alphabet))]
    
    def char_to_idx(self, char: str) -> int:
        return ord(char.lower()) - ord("a")  # нормализуем регистр перед преобразованием
    
    def idx_to_char(self, idx: int) -> str:
        return chr(idx + ord("a"))

    def add_user(self, username: str) -> None:
        idx = self.char_to_idx(username[0])  # определяем первую букву имени
        self.users[idx].append(username)
        return
    
    def show_users(self) -> None:
        for idx in range(len(self.alphabet)):
            char = self.idx_to_char(idx)
            print(f"{char}: ", end=" ")
            users = self.users[idx].display()
            print(users)
        return


container = Users()
container.add_user(username="Alex")
container.add_user(username="Alfred")
container.add_user(username="Bob")
container.add_user(username="Cris")
container.add_user(username="Conrad")
container.add_user(username="Viki")
container.add_user(username="Lucas")
container.add_user(username="Fisherman Alfred")

container.show_users()