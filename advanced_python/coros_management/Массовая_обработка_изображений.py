"""
Есть список изображений. Для каждого вызывается process_image(path).
Нужно сохранять результаты в БД по мере готовности.
"""

from asyncio import create_task, as_completed, Task, gather
from collections.abc import Awaitable


async def process_image(path: str) -> dict: ...


async def save_result(result: dict) -> None: ...


async def process_images(paths: list[str]) -> None:
    tasks: list[Task[dict]] = [create_task(process_image(path)) for path in paths]

    future: Awaitable[dict]

    # case when we continue-on-error
    for future in as_completed(tasks):
        try:
            res: dict = await future
        except Exception:
            print(f"failed {res}")
            continue
        await save_result(res)

    # case when we cancel-on-error
    for future in as_completed(tasks):
        try:
            res: dict = await future
            await save_result(res)
        except Exception:
            for task in tasks:
                if not task.done():
                    task.cancel()

            await gather(*tasks, return_exceptions=True)
            raise
