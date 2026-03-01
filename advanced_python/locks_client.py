import asyncio
import httpx


async def check_booking_without_lock(client: httpx.AsyncClient):
    url = "http://127.0.0.1:8000/no-lock-booking/"  # <-- http + /booking/
    r = await client.get(url)
    return r.text


async def check_booking_with_lock(client: httpx.AsyncClient):
    url = "http://127.0.0.1:8000/lock-booking/"  # <-- http + /booking/
    r = await client.get(url)
    return r.text


async def main():
    async with httpx.AsyncClient() as client:
        # print("no lock")
        # results = await asyncio.gather(
        #     *(check_booking_without_lock(client) for _ in range(2))
        # )
        # print(results)

        print("lock")
        results = await asyncio.gather(
            *(check_booking_with_lock(client) for _ in range(2))
        )
        print(results)


if __name__ == "__main__":
    asyncio.run(main())
