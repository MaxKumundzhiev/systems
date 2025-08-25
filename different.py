# TASK 1
################################################################
# import asyncio
# import httpx

# async def fetch_url(client, url):
#     try:
#         response = await client.get(url)
#         response.raise_for_status()
#         return await response.json()
#     except httpx.HTTPStatusError as e:
#         print(f"❌ Error fetching {url}: {e}")
#         return {"error": str(e), "url": url}


# async def main():
#     urls = [
#         "https://jsonplaceholder.typicode.com/todos/1",
#         "https://jsonplaceholder.typicode.com/todos/2",
#         "https://jsonplaceholder.typicode.com/todos/3"
#     ]
    
#     async with httpx.AsyncClient() as client:
#         tasks = [asyncio.create_task(fetch_url(client, url)) for url in urls]
#         responses = await asyncio.gather(*tasks, return_exceptions=True)
    
#     print("✅ Results:")
#     for response in responses:
#         print(response)


# if __name__ == "__main__":
#     asyncio.run(main())

# TASK 2
################################################################
# import asyncio
# from asyncio import Queue
# from random import randint


# class Producer:
#     async def produce(self, queue: Queue) -> None:
#         try:
#             task = f"task #{randint(0, 100)}"
#             await queue.put(task)
#             print(f"[producer] pushed to queue: {task}")
#             await asyncio.sleep(0.1)
#         except Exception as e:
#             print(f"[producer] error: {e}")
#             raise


# class Consumer:
#     async def consume(self, queue: Queue) -> None:
#         while True:
#             task = await queue.get()

#             if task is None:
#                 print(f"[consumer] received stop signal")
#                 queue.task_done()
#                 break

#             try:
#                 print(f"[consumer] pulled from queue: {task}")
#                 await asyncio.sleep(0.3)
#                 print(f"[consumer] processed: {task}")
#             finally:
#                 queue.task_done()


# async def handle():
#     queue = Queue()
#     producer = Producer()
    
#     # 50 продюсеров = 50 задач
#     produce_tasks = [asyncio.create_task(producer.produce(queue)) for _ in range(50)]
#     await asyncio.gather(*produce_tasks)

#     # создаём 3 воркера
#     consumers = [Consumer() for _ in range(3)]
#     consumer_tasks = [asyncio.create_task(consumer.consume(queue)) for consumer in consumers]

#     # отправляем сигналы остановки по числу воркеров
#     for _ in consumers:
#         await queue.put(None)

#     # ждём завершения всех задач
#     await queue.join()
#     await asyncio.gather(*consumer_tasks)


# if __name__ == "__main__":
#     asyncio.run(handle())



# TASK 3
################################################################
import asyncio
import aiosqlite


class DBManager:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
    
    async def get_connection(self):
        try:
            async with aiosqlite.connect(self.db_path) as db:
                yield db
        finally:
            await db.close()


class UserRepository:
    def __init__(self, connection):
        self.connection = connection

    async def create_user_table(self):
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                balance INTEGER NOT NULL DEFAULT 0
            )
        """)
        await self.connection.commit()

    async def add_user(self, name: str, balance: int):
        await self.connection.execute("INSERT INTO users (name, balance) VALUES (?, ?)", (name, balance))
        await self.connection.commit()

    async def update_balance(self, user_id: int, amount: int):
        await self.connection.execute("UPDATE users SET balance = balance + ? WHERE id = ?", (amount, user_id))
        await self.connection.commit()


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def transfer_money(self, from_user_id: int, to_user_id: int, amount: int):
        await self.repo.update_balance(from_user_id, -amount)
        await self.repo.update_balance(to_user_id, amount)


async def main():
    db_manager = DBManager(db_path="test.db")
    
    repo = UserRepository(connection=db_manager.get_connection())
    service = UserService(repo)

    await repo.create_user_table()
    await repo.add_user("Alice", 100)
    await repo.add_user("Bob", 50)

    await service.transfer_money(1, 2, 30)
    print("✅ Transfer complete")


if __name__ == "__main__":
    asyncio.run(main())
