import asyncio
from random import randint


"""
1. последовательно через await coro()
2. конкурентно через gather() с флагом return_exception=True|False
3. через create_task() одну задачу
4. через create_task() много задач
_______________________________________________________________________________________

asyncio.create_task()
    Запускает корутину как отдельную задачу в event loop.

asyncio.gather()
    Запускает несколько awaitable конкурентно и ждёт все.

asyncio.wait()
    Ждёт набор задач с более гибким контролем. (done, pending)

asyncio.as_completed()
    Позволяет обрабатывать результаты по мере завершения, а не по порядку запуска.

asyncio.TaskGroup()
    Современный структурированный способ управлять группой задач.

asyncio.wait_for()
    Ограничивает выполнение по времени.
"""


async def worker(id: int, name: str) -> str:
    delay = randint(0, 3)
    msg = f"Worker {id} --> {name} working for {delay}."
    print(msg)
    await asyncio.sleep(delay)
    return msg


async def worker_with_random_status(id: int, name: str) -> int:
    score = randint(0, 10)
    status = True if score >= 5 else False

    print(f"Worker {id} --> {name} got score {score}., staus: {status}")
    if not status:
        raise RuntimeError

    return score


async def sequential():
    """
    idea is that even though we have coros the way wa call them is sequential

    выполняется строго по очереди
    следующая начинается только после завершения предыдущей
    """

    await worker(id=1, name="sync")
    await worker(id=2, name="sync")


async def concurrent_with_gather():
    """
    запускает все корутины одновременно
    ждёт всех

    в данном случае, если одна из корутин упадет и никак не менеджить ошибку то решение упадет
    как лечить
        при помощи атрибута return_exception=True (по дефолту он False)

    Worker 1 --> worker-1 got score 10., staus: True
    Worker 2 --> worker-2 got score 4., staus: False
    Worker 3 --> worker-3 got score 8., staus: True

    дальше мы можем обрабатывать эти ошибки через использование isisntance()
    """

    coros = [
        worker_with_random_status(id=1, name="worker-1"),
        worker_with_random_status(id=2, name="worker-2"),
        worker_with_random_status(id=3, name="worker-3"),
    ]

    results = await asyncio.gather(*coros, return_exceptions=True)
    print(results)

    # простая обработка ошибок
    total = 0
    for result in results:
        if isinstance(result, int):
            total += result
        else:
            print(f"caught exception in coro exec: {type(result)} {result}")


async def single_create_task():
    """
    create_task - обварачивает корутину в Task обьект и внутри запустит как только ивент оуп даст это сделать
    """
    task = asyncio.create_task(worker(id=1, name="worker-1"))
    result = await task
    print(result)


async def multiple_create_task():
    tasks = [asyncio.create_task(worker(id=id, name=f"worker-{id}")) for id in range(5)]
    # tasks now sent to event loop
    # we need to fetch results
    """
    Можно ждать:
        все
        первую завершившуюся
        первую упавшую
    Через:
        ALL_COMPLETED
        FIRST_COMPLETED
        FIRST_EXCEPTION
    """

    done, pending = await asyncio.wait(tasks)


async def multiple_create_task_with_as_completed():
    tasks = [asyncio.create_task(worker(id=id, name=f"worker-{id}")) for id in range(5)]
    # tasks now sent to event loop
    # we need to fetch results

    for finished in asyncio.as_completed(tasks):
        result = await finished
        print(result)


if __name__ == "__main__":
    # asyncio.run(sequential())
    # asyncio.run(concurrent_with_gather())
    # asyncio.run(single_create_task())
    # asyncio.run(multiple_create_task())
    asyncio.run(multiple_create_task_with_as_completed())
