"""
Есть 5 поисковых запросов в разные индексы.
Нужно запускать все сразу и печатать результаты по мере готовности.
"""

from asyncio import create_task, as_completed, Task
from collections.abc import Awaitable, Iterator


async def search_index(name: str, query: str) -> list[str]: ...


async def search_everywhere(query: str) -> list[list[str]]:
    tasks: list[Task[list[str]]] = [
        create_task(search_index(str(name), query)) for name in range(5)
    ]

    res: list[list[str]] = []

    future: Awaitable[list[str]]
    
    for future in as_completed(tasks):
        query_res = await future
        res.append(query_res)

    return res
