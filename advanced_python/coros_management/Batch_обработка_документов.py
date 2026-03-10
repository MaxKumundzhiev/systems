"""
Для одного batch-а нужно создать группу задач, каждая обрабатывает один документ.
Если одна падает критически — остальные тоже отменяются.

Ход мыслей
    первое что приходит в голову это TaskGroup
    но в данной задачи мы работаем с as_complete()
    as_complete() - механизм, в который передается группа задач уже запущенных через create_task()
    as_complete() будучи итератором отдает Future обьекты которые нужно await
    в данном механизме если задача упадет то она упадет на await
    поэтому неоюходимо отлавливать эту ошибку

    финальная логика такая
    запускаем через create_task() группу задач батча
    через as_completed() по одной обрабатываем результат
    если очередная задача упала, тогда отменям все задачи из батча (подход cancel-as-error (есть еще continue-as-error))
"""

from abc import ABC, abstractmethod
from collections.abc import Awaitable, Iterator

from asyncio import create_task, as_completed, gather, Task


### interfaces ###
class DocumentService(ABC):
    @abstractmethod
    async def process_document(self, doc_id: str) -> dict:
        raise NotImplementedError


class BatchPipeline(ABC):
    @abstractmethod
    async def process_batch(self, doc_ids: list[str]) -> list[dict]:
        raise NotImplementedError


### implementation ###
class BatchPipelineImpl(BatchPipeline):
    def __init__(self, doc_service: DocumentService) -> None:
        self._doc_service = doc_service

    async def process_batch(self, doc_ids: list[str]) -> list[dict]:
        tasks: list[Task[dict]] = []
        for doc_id in doc_ids:
            tasks.append(create_task(self._doc_service.process_document(doc_id)))

        response: list[dict] = []
        for ft in as_completed(tasks):
            try:
                result: dict = await ft
                response.append(result)
            except Exception:
                for task in tasks:
                    if not task.done():
                        # task.cancel() - only send "request" to cancel a task, not cancel it immediatly
                        task.cancel()

                """
                дождаться, пока все задачи либо завершатся, либо окончательно отменятся
                забрать их исключения и не дать им “утечь”
                
                !!! я отправил задачам сигнал отмены, 
                а gather нужен, чтобы дождаться их финального завершения и собрать все исключения
                """
                await gather(*tasks, return_exceptions=True)
                raise

        return response
