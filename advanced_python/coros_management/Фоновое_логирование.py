"""
asyncio create_task()

Есть:
    process_request(request_id)
    write_audit_log(request_id)

Нужно сделать так, чтобы:
    основной запрос обработался как обычно
    аудит-лог ушел в фоне
    ответ не ждал завершения логирования
"""

import asyncio


async def process_request(request_id: str) -> dict: ...


async def write_audit_log(request_id: str) -> None: ...


async def handle_request(request_id: str) -> dict:
    res = await process_request(request_id)  # wait for res
    asyncio.create_task(
        write_audit_log(request_id)
    )  # once res obtained, send to event loop a task to be executed
    return res
