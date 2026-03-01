import asyncio
import httpx
import time


async def book(room_id):
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"http://127.0.0.1:8000/book/{room_id}")
        return resp.json()


async def test_same_room():
    start = time.perf_counter()

    results = await asyncio.gather(
        book(42),
        book(42),
        book(100),
        book(200),
        book(1),
        book(513),  # 513 % 512 == 1
    )

    duration = time.perf_counter() - start

    print("Results:", results)
    print("Time:", duration)


asyncio.run(test_same_room())
