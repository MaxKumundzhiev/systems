"""
Locks - блокировки

Это синхранизационный примитив (механизм), который позволяет избегать race condition и deadlocks.
Он позволяет контролировать доступ к ресурсам в конкурентной среде.

Есть 2 типа
    - блокировки в потоках - поток блокирует ресурс, другой поток не имеет доступа, программа блокируется потоком.
    - блокировки в async - корутина блокирует ресурс, другая корутина не имеет доступа, программа НЕ блокируется корутинами.


Race condition Гонка без Lock: “последний номер” (овербукинг)
Идея: остался 1 номер на дату. Два человека жмут “Забронировать” одновременно.

Deadlock - нельзя брать lock-и в разном порядке
Ситуация: ты хочешь “поменять бронь” — снять с комнаты A и поставить в комнату B.
    Если в одном месте ты берёшь lock(A) потом lock(B), а в другом — lock(B) потом lock(A), можно зависнуть навсегда:
        таска1 держит A и ждёт B
        таска2 держит B и ждёт A
Решение: единый порядок взятия lock-ов (например, сортировать ключи).
"""

import asyncio
from fastapi import FastAPI


app = FastAPI()


available = 1
lock = asyncio.Lock()


@app.get("/no-lock-booking/")
async def no_lock_booking():
    """
    Идея: остался 1 номер на дату. Два человека жмут “Забронировать” одновременно.
    Почему ломается:
        A проверил available > 0 ✅
        переключение на B
        B проверил available > 0 ✅
        оба дошли до available -= 1 → станет -1 → две брони на один номер
        Ключ: между check и write был await.
    """

    global available
    print(available)

    if available > 0:
        await asyncio.sleep(0.3)
        available -= 1
        return True
    return False


@app.get("/lock-booking/")
async def lock_booking():
    """
    Идея: остался 1 номер на дату. Два человека жмут “Забронировать” одновременно.
    Почему ломается:
        A проверил available > 0 ✅
        переключение на B
        B проверил available > 0 ✅
        оба дошли до available -= 1 → станет -1 → две брони на один номер
        Ключ: между check и write был await.
    """

    global available, lock

    async with lock:
        print(available)
        if available > 0:
            await asyncio.sleep(0.3)
            available -= 1
            return True
        return False


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
