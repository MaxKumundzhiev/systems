import asyncio
from random import randint


async def worker(id: int, name: str) -> None:
    delay = randint(0, 3)
    print(f"Worker {id} --> {name} working for {delay}.")
    await asyncio.sleep(delay)
    return None


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


async def concurrent():
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


if __name__ == "__main__":
    # asyncio.run(sequential())
    asyncio.run(concurrent())
