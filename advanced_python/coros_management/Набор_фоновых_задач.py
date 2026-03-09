"""
Есть 5 задач обработки файлов.

Нужно:
    запустить все
    дождаться завершения через asyncio.wait
    отдельно обработать done и pending
"""

from asyncio import Task, create_task, wait, ALL_COMPLETED


async def process_file(file_id: int) -> str: ...


async def run_batch(
    file_ids: list[int],
) -> tuple[set[Task[str]], set[Task[str]]]:
    tasks: set[Task[str]] = {create_task(process_file(id)) for id in file_ids}

    done: set[Task[str]]
    pending: set[Task[str]]

    # expect pending being empty set, cause return_when=ALL_COMPLETED
    """
    if one of tasks will fail, wait() wont raise eception, instead store it inside of res
    thus common approach to catch it is as follows:
    done, pending = await wait(tasks, return_when=ALL_COMPLETED)
    
    for task in done:
        try:
            res = task.result()
        except Exception:
            // now in res there is exception -> so to do something with it
            print("failed")
        // gonna be here when task.result() did not raise exception 
        else:
            print("success")
            
    """
    done, pending = await wait(tasks, return_when=ALL_COMPLETED)
    return done, pending
