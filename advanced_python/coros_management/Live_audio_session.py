"""
Во время live session нужно одновременно держать:
    - чтение аудио
    - транскрибацию
    - отправку partial results
    - heartbeat
Как только одна критичная часть ломается, вся session завершается.
"""

import asyncio


async def receive_audio() -> None: ...


async def transcribe_stream() -> None: ...


async def send_partial_results() -> None: ...


async def session_heartbeat() -> None: ...


async def run_live_session() -> None:
    tasks = [
        asyncio.create_task(receive_audio()),
        asyncio.create_task(transcribe_stream()),
        asyncio.create_task(send_partial_results()),
        asyncio.create_task(session_heartbeat()),
    ]

    error_occurred = False
    for future in asyncio.as_completed(tasks):
        try:
            await future
        except Exception:
            error_occurred = True
            break

    if error_occurred:
        for task in tasks:
            if not task.done():
                task.cancel()

        await asyncio.gather(*tasks, return_exceptions=True)

    return
