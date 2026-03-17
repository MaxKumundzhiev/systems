import asyncio
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import uuid4
import random

"""
model a situation:
    the system produces start session event and send to the pending hashtable (by key)
    session_id: {"start_at": ..., "end_at": ...,}
    once system produces end session event, we pop that entity from hashtable and push it to the pending queue
    consumer consumes event from pending queue and put to "db"
"""


@dataclass
class Session:
    started_at: Optional[str] = field(default_factory=lambda: str(datetime.now()))
    ended_at: Optional[str] = None


condition = asyncio.Condition()

sessions: dict[str, Session] = {}
pending_events: list[tuple[str, Session]] = []
db: dict[str, Session] = {}


async def start_session():
    while True:
        delay = random.uniform(1, 2)
        id, session = uuid4().hex, Session()

        sessions[id] = session  # no condition needed here
        print(f"session started: {id, session}")
        await asyncio.sleep(delay)


async def end_session():
    while True:
        if not sessions:
            await asyncio.sleep(0.1)
            continue

        id = random.choice(list(sessions.keys()))
        session = sessions.pop(id, None)

        if session is None:
            continue

        session.ended_at = str(datetime.now())
        print(f"session ended: {id, session}")
        async with condition:
            pending_events.append((id, session))
            condition.notify_all()  # 🔑 notify consumer


async def consumer():
    while True:
        async with condition:
            await condition.wait_for(lambda: len(pending_events) >= 10)

            batch = pending_events[:10]
            del pending_events[:10]

        # process outside lock
        for sid, session in batch:
            db[sid] = session

        print(f"Processed batch of {len(batch)} sessions")


if __name__ == "__main__":

    async def main():
        tasks = [
            asyncio.create_task(start_session()),
            asyncio.create_task(end_session()),
            asyncio.create_task(consumer()),
        ]

        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)

        # handle exception
        for task in done:
            if task.exception():
                print(f"Task failed: {task.exception()}")

        # cancel remaining tasks
        for task in pending:
            task.cancel()
        await asyncio.gather(*pending, return_exceptions=True)

    asyncio.run(main())
