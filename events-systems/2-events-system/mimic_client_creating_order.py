import asyncio
import random
import string

import httpx


API_URL = "http://0.0.0.0:8000"


def random_name() -> str:
    return "user_" + "".join(random.choices(string.ascii_lowercase, k=5))


def random_items() -> list[str]:
    catalog = ["pizza", "cola", "burger", "coffee", "cake"]
    return random.sample(catalog, k=random.randint(1, 3))


def total_price(items: list[str]) -> float:
    prices = {
        "pizza": 12.5,
        "cola": 2.5,
        "burger": 10.0,
        "coffee": 3.0,
        "cake": 4.5,
    }
    return round(sum(prices[i] for i in items), 2)


async def create_order(client: httpx.AsyncClient):
    items = random_items()
    payload = {
        "name": random_name(),
        "items": items,
        "total_price": total_price(items),
    }

    endpoint = f"{API_URL}/orders/"
    r = await client.post(endpoint, json=payload)
    r.raise_for_status()

    print("Order created:", r.json())
    return r.json()


async def create_notification(client: httpx.AsyncClient, id, created_at):
    payload = {
        "event_name": "new_order_created",
        "id": id,
        "created_at": created_at,
    }
    endpoint = f"{API_URL}/notifications/"
    r = await client.post(endpoint, json=payload)
    r.raise_for_status()
    print("Notification created:", r.json())


async def main():
    async with httpx.AsyncClient() as client:
        while True:
            try:
                order = await create_order(client)
                await create_notification(
                    client=client, id=order["id"], created_at=order["created_at"]
                )
            except Exception as e:
                print("Error:", e)

            # задержка от 5 до 60 секунд
            delay = random.randint(5, 60)
            print(f"Sleep {delay}s...\n")
            await asyncio.sleep(delay)


if __name__ == "__main__":
    asyncio.run(main())
