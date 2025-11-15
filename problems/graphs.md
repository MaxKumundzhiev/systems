# Графы. Поиск в ширину (BFS)

**Алгоритм для решения задачи поиска кратчайшего пути называется поиском в ширину.**

## Общее
```text
Графы - структура данных, моделирующая набор связей.
Графы состоят из узлов и ребер.


Два вопроса, на которые может ответить алго-
ритм поиска в ширину:
 тип 1: существует ли путь от узла A к узлу B? (Есть ли продавец манго в вашей сети?)

 тип 2: как выглядит кратчайший путь от узла A к узлу B? (Кто из про-
давцов манго находится ближе всего к вам?)

Поиск в ширину позволяет найти кратчайшее расстояние между двумя обьктами в графе

Сам термин кратчайшее расстояние может иметь разные значения например: 
    - в игре в шашки найти кратчайшее расстояние до победы
    - реализовать проверку правописания (минимальное количество изменений, преобразующих ошибочно написанное слово в правильное, например АЛГОРИФМ -> АЛГОРИТМ — одно изменение);
    - найти ближайшего к вам врача
```

## Реализация графа
```text
Граф моделирует отношения. Структура данных позволяющая отображать отношения - это хэш таблица.

small graph:
--------------------------
graph = {}
graph["you"] = ["Bob", "Mike", "Alice"]  # who u are connected with
--------------------------

bigger graph:
--------------------------
graph = {}
graph["you"] = ["alice", "bob", "claire"]
graph["bob"] = ["anuj", "peggy"]
graph["alice"] = ["peggy"]
graph["claire"] = ["thom", "jonny"]
graph["anuj"] = []
graph["peggy"] = []
graph["thom"] = []
graph["jonny"] = []
--------------------------
```


```python
# bfs traversal without libs
from typing import List

class Node:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def bfs(root: List[Node]):
    queue = [root]
    seen = []

    while queue:
        level = len(queue)
        for _ in range(level):
            node = queue.pop(0)
            level.append(node.val)
            if node.left:
                queue.append(node.left)
            elif node.right:
                queue.append(node.right)
        seen.append(level)

# -----------------------
# bfs traversal with libs
from collections import deque

def bfs(root):
    queue = deque()
    queue.add(root)
    visited = []

    while queue:
        nodes = len(queue)
        while nodes:
            node = queue.popleft()
            visited.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
```

```python
# Exercises
0. Найти продавца манго среди друзей
from collections import deque

graph = {}
graph["you"] = ["alice", "bob", "claire"]
graph["bob"] = ["anuj", "peggy"]
graph["alice"] = ["peggy"]
graph["claire"] = ["thom", "jonny"]
graph["anuj"] = []
graph["peggy"] = []
graph["thom"] = []
graph["jonny"] = []


def is_seller(name: str) -> bool:
    return name[-1] == "m"

def search(graph):
    search_queue = deque()
    search_queue += graph["you"]
    searched = set()
    
    while search_queue:
        person = search_queue.popleft()
        if not person in searched:
            searched.add(person)
            if is_seller(person): return True, person
            search_queue += graph[person]
    return False, None


1. Найдите длину кратчайшего пути от начального до конечного узла.

def shortest_path(root):
    queue = [root]
    levels = 0

    while queue:
        nodes_at_level = len(queue)
        levels += 1
        for _ in range(nodes_at_level):
            node = queue.pop(0)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
            if not node.left and not node.right:
                return levels

2. Найдите длину кратчайшего пути от «cab» к «bat».

```
