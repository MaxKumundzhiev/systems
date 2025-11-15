# Алгоритм Дейкстры

**Алгоритм Дейкстры отвечает на вопрос: какой кратчайший путь до X в взвешенном графе.** (используется для поиска пути от начальной точки к конечной за кратчайшее возможное время.)
**Алгоритм Дейкстры не может использоваться при наличии ребер, имеющих отрицательный вес.** (алгоритмом Беллмана—Форда для взвешенных графов с отрицательными весами)

```text
Алгоритм Дейкстры состоит из четырех шагов:
1. Найти узел с наименьшей стоимостью (то есть узел, до которого можно
добраться за минимальное время).
2. Проверить, существует ли более дешевый путь к соседям этого узла,
и если существует, обновить их стоимости.
3. Повторять, пока это не будет сделано для всех узлов графа.
4. Вычислить итоговый путь (об этом в следующем разделе!).

Для вычисления кратчайшего пути в невзвешенном графе используется
поиск в ширину. Кратчайшие пути во взвешенном графе вычисляются по
алгоритму Дейкстры. В графах также могут присутствовать циклы
```


## Implementation
```python
infinity = float("inf")

# define graph
graph = {}
graph["start"]["a"] = 6
graph["start"]["b"] = 2
graph["a"] = {}
graph["a"]["end"] = 1
graph["b"] = {}
graph["b"]["a"] = 3
graph["b"]["end"] = 5
graph["end"] = {}

# define costs (how much it cost to reach key (node))
costs = {}
costs["a"] = 6
costs["b"] = 2
costs["end"] = infinity

# define parents (node: its parent)
parents = {}
parents["a"] = "start"
parents["b"] = "start"
parents["end"] = None


# define list of visited or processed nodes to avoid processing same node twice or more
processed = []

def find_lowest_cost_node(costs):
    lowest_cost = float("inf")
    lowest_cost_node = None
    for node in costs:              # Перебрать все узлы
        cost = costs[node]
        if cost < lowest_cost and node not in processed:
            lowest_cost = cost
            lowest_cost_node = node
    return lowest_cost_node

node = find_lowest_cost_node(costs)
while node is not None:                 # Если обработаны все узлы, цикл while завершен
    cost = costs[node]
    neighbors = graph[node]
    for n in neighbors.keys():          # Перебрать всех соседей текущего узла
        new_cost = cost + neighbors[n]
        if costs[n] > new_cost:
            costs[n] = new_cost         # …обновить стоимость для этого узла
            parents[n] = node           # Этот узел становится новым родителем для соседа
    processed.append(node)              # Узел помечается как обработанный
    node = find_lowest_cost_node(costs)
```