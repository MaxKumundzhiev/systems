"""
При старте сервиса нужно:
    - поднять API
    - параллельно начать прогрев кэша через warm_up_cache()
"""

import asyncio


async def warm_up_cache() -> None: ...


async def start_http_server() -> None: ...


async def start_service() -> None:
    """
    Idea is that we have to ensure and wait start_http_server()
    Afterwards, create_task() sends coro wrapped in Task to event loop and returns management immideatly
    """
    await start_http_server()
    asyncio.create_task(warm_up_cache())
