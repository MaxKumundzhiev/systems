"""
Есть async-функция transcribe_audio_chunk().
Для real-time voice system нельзя ждать дольше 300 мс на chunk.
"""

import asyncio


class ChunkTimeoutError(Exception):
    pass


async def transcribe_audio_chunk(chunk: bytes) -> str: ...


async def cleanup(task: asyncio.Task[str]) -> None:
    if not task.done():
        task.cancel()
    await asyncio.gather(task, return_exceptions=True)
    return None


async def process_chunk(chunk: bytes) -> str:
    task: asyncio.Task[str] = asyncio.create_task(transcribe_audio_chunk(chunk))

    try:
        return await asyncio.wait_for(task, timeout=0.3)
    except asyncio.TimeoutError as e:
        await cleanup(task)
        raise ChunkTimeoutError("transcription exceeded 300 ms") from e
