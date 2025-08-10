from time import perf_counter
from random import randint

from concurrent.futures import ProcessPoolExecutor

from fastapi import FastAPI
from asyncio import get_event_loop


app = FastAPI()
executor = ProcessPoolExecutor(max_workers=4)


def generate_buffer():
    start = perf_counter()
    buffer = [randint(0, 10**6) for _ in range(10**6)]
    end = perf_counter()
    elapsed = end - start
    return elapsed, len(buffer)


@app.post("/")
async def post():
    loop = get_event_loop()
    time, len = await loop.run_in_executor(executor, generate_buffer)
    
    return {
        "time": time,
        "size": len
    }
