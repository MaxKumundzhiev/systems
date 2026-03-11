# gather()

# create_task()

# wait()
wait это механизм ожидания задач с 3 разными режимами
- закончилась первая (FIRST_COMPLETE)
- все закончились (ALL_COMPLETE)
- первая ошибка (FIRST_EXCEPTION)

при этом рещультаты раскидываются по 2 множествам, done & pending
в wait нужно передавать set[Task]
```python
async def job():
    print("job")
    return

tasks = {
    asyncio.create_task(job()) for _ in range(3)
}

done, pending = asyncio.wait(tasks, return_when=<flag>)
```

Пример, есть 3 задачи
t1 = 1 sec
t2 = 3 sec
t3 = 5 sec

FIRST_COMPLETE
done = {t1}
pending = {t2, t3}

FIRST_EXCEPTION
Сценарий 1 — одна задача падает
t1 -> success
t2 -> exception
t3 -> still running

Как только t2 падает:
done = {t1, t2}
pending = {t3}

Сценарий 2 — никто не падает
t1 success
t2 success
t3 success

Тогда wait ведёт себя как ALL_COMPLETED.
done = {t1, t2, t3}
pending = set()

Наглядная временная линия

Задачи:
t1 -> success after 1s
t2 -> exception after 2s
t3 -> success after 3s

FIRST_COMPLETED
t=1
done = {t1}
pending = {t2, t3}

FIRST_EXCEPTION
t=2
done = {t1, t2}
pending = {t3}

ALL_COMPLETED
t=3
done = {t1, t2, t3}
pending = {}

```text
Когда что использовать
режим	                когда применять
FIRST_COMPLETED	    race / fastest response
FIRST_EXCEPTION	    остановить batch при первой ошибке
ALL_COMPLETED	    дождаться всех задач
```

# as_completed()
механизм получать результаты задач по мере их завершения, а не в порядке запуска.
сам обварачивает корутины в Таски (но можно и передавать уже Таски)

самый похожий подход это gather()
gather() ждет исполнения всех и потом возврашает в том же порядке результаты что корутины были переданы
as_complete() отдает первую future которую ты должен await

```
async def job():
    await asyncio.sleep(1)
    return

tasks = [job() for _ in range(3)]

for future in asyncio.as_complete(tasks):
    res = await future
    // если после получения первого результата не нужны остальные
    // просто отменям их
```

Как работает внутри as_completed():
1️⃣ принимает iterable awaitables
2️⃣ превращает их в Task
3️⃣ подписывается на завершение
4️⃣ возвращает итератор futures
Каждый элемент итератора — это future, который можно await.

Существует 2 общих подхода (policies): `cancel-on-error`, `continue-on-error`

```python
`cancel-on-error`

for ft in as_complete(tasks):
    try:
        result = await ft
    except Exception:
        for task in tasks:
            if not task.done():
                task.cancel()
        await gather(*tasks, return_exceptions=True)
        raise
```

```python
`continue-on-error`

for ft in as_complete(tasks):
    try:
        result = await ft
    except Exception:
        continue
```

# wait_for()
wait_for() - механизм, который позволяет добавить timeout на awaitable. по факту это как обычный await только с ограничением по времени.

```python
res = await asyncio.wait_for(coro(), timeout=<>)
```

Типы ошибок
1. TimeoutError
2. RuntimeError (inside coroutine itself)

```python
import asyncio

class ChunkTimeoutError(Exception):
    pass

async def transcribe_audio_chunk(chunk: bytes) -> str: ...

async def cleanup(task: asyncio.Task[str]) -> None:
    if not task.done():
        task.cancel()
    await asyncio.gather(task, return_exceptions=True)


async def process_chunk(chunk: bytes) -> str:
    task: asyncio.Task[str] = asyncio.create_task(transcribe_audio_chunk(chunk))

    try:
        return await asyncio.wait_for(task, timeout=0.3)
    except asyncio.TimeoutError as e:
        await cleanup(task)
        raise ChunkTimeoutError("transcription exceeded 300 ms") from e
    except Exception as e:
        await cleanup(task)
        raise
```


# TaskGroup()
это контекст-менеджер для запуска и управления группой async-задач
Он реализует structured concurrency.

Гарантии:
- все созданные задачи будут завершены
- если одна задача падает, остальные автоматически отменяются
- после выхода из блока async with все задачи уже завершены

```python
async with asyncio.TaskGroup() as tg:
    tg.create_task(job())
    tg.create_task(job())
-----------

try:
    async with asyncio.TaskGroup() as tg:
        tg.create_task(job1())
        tg.create_task(job2())
except* RuntimeError:
    print("runtime error happened")
```
