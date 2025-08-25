"""
concurrent.futures Thread and Process Executors
"""
# import time
# from concurrent.futures import ProcessPoolExecutor


# def count(count_to: int) -> int:
#     start = time.time()
    
#     counter = 0
#     while counter < count_to:
#         counter += 1
    
#     end = time.time()
#     print(f"Finished counting to {count_to} for time {end - start}")

#     return counter

# if __name__ == "__main__":
#     with ProcessPoolExecutor() as process_pool:
#         numbers = [1, 3, 5, 22, 10000000]
#         for result in process_pool.map(count, numbers):
#             print(result)
################################################################################



"""
Run concurrent.futures Executor with asyncio
"""
# import asyncio

# from typing import List
# from functools import partial
# from concurrent.futures import ProcessPoolExecutor

# def count(count_to: int) -> int:
#     cnt = 0
#     while cnt < count_to:
#         cnt += 1
#     return cnt


# async def main():
#     with ProcessPoolExecutor() as pool:
#         loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()
#         nums = [1, 2, 3, 5, 100000000]
#         calls: List[partial[int]] = [partial(count, num) for num in nums]
#         calls_coros = []

#         for call in calls:
#             calls_coros.append(loop.run_in_executor(pool, call))
        
#         results = await asyncio.gather(*calls_coros)
#         for result in results:
#             print(result)

# if __name__ == "__main__":
#     asyncio.run(main())
################################################################################


"""
asyncio gather with exceptions handling
"""
# import asyncio

# async def fetch_status(url: str) -> int:
#     from random import choice
#     choices = [200, 400, 404, 500]
#     return choice(choices)

# async def main():
#     tasks = [fetch_status(url=str(idx)) for idx in range(10000)]
#     # return_exceptions=True            - not failing, return all exceptions within results
#     # return_exceptions=False (default) - failing on first failed task
#     statuses = await asyncio.gather(*tasks, return_exceptions=True)

#     exceptions = [status for status in statuses if status != 200]
#     success = [status for status in statuses if status == 200]
    
#     print(f"exceptions: {len(exceptions)}")
#     print(f"success: {len(success)}")


# if __name__ == "__main__":
#     asyncio.run(main())


"""
asyncio as_complete with exceptions handling
"""
# import asyncio

# async def fetch_status(url: str) -> int:
#     from random import choice
#     choices = [200, 400, 404, 500]
#     return choice(choices)

# async def main():
#     tasks = [fetch_status(url=str(idx)) for idx in range(10000)]
#     for done in asyncio.as_completed(tasks):
#         try:
#             result = await done
#             print(done)
#         except Exception as e:
#             raise e

# if __name__ == "__main__":
#     asyncio.run(main())



"""
asyncio wait with exceptions handling
"""
import asyncio

async def fetch_status(url: str) -> int:
    from random import choice
    choices = [200, 400, 404, 500]
    return choice(choices)

async def main():
    tasks = [asyncio.create_task(fetch_status(url=str(idx))) for idx in range(10000)]
    done, pending = await asyncio.wait(tasks)
    
    for done_task in done:
        if done_task.exception() is None:
            print(done_task.result())
        else:
            raise Exception

if __name__ == "__main__":
    asyncio.run(main())