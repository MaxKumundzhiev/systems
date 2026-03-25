import asyncio
import time
from abc import ABC, abstractmethod
from typing import List
from concurrent.futures import ProcessPoolExecutor, Future


def generate_thumbnail(data: bytes) -> bytes:
    """
    Библиотечная функция генерации миниатюры. Трогать не нужно[cite: 10].
    """
    time.sleep(1)
    return data[:4] if len(data) > 4 else data


class Connect(ABC):
    """Это интерфейс, его нельзя изменять[cite: 15]."""

    @abstractmethod
    def is_ready_to_read(self) -> bool:
        pass

    @abstractmethod
    def is_ready_to_write(self) -> bool:
        pass

    @abstractmethod
    def read(self) -> bytes:
        pass

    @abstractmethod
    def write(self, data: bytes) -> int:
        pass


###############################
## Код выше изменять нельзя [cite: 29]
###############################

# Постановка задачи (Усложнение):
# Теперь требуется ускорить весь процесс обработки подключений целиком, включая ожидание сети (IO)[cite: 74].
# В каждое подключение данные разных размеров поступают в разное время[cite: 74].
# Ключевая метрика для улучшения — latency (задержки)[cite: 76].
#
# Твои цели:
# 1. Перейти от батчинга к потоковому пайплайну (Streaming Pipeline)[cite: 75].
# 2. Учесть "Проблему 10к соединений": использовать корутины (asyncio) для работы с сетью.
# 3. Избежать простоя потенциально готовых соединений из-за ожидания неготовых[cite: 82, 92].
# 4. Решить проблему высокого latency: сделать так, чтобы несколько "толстых" запросов (больших картинок) не забили вычислительный пул и не заблокировали маленькие быстрые задачи.


async def process(connects: List[Connect]):
    """
    Реализуй асинхронный потоковый пайплайн обработки здесь.
    Подумай над тем, как эффективно разделить IO-bound и CPU-bound операции[cite: 94],
    и как управлять размерами пулов для вычислений[cite: 95].
    """
    asyncio.run(_process_async(connects))


"""
TODO: Реализовать _process_async, который будет использовать asyncio для управления IO и multiprocessing для CPU-bound задач.

producer reads connects
put connect, data which is ready to pending queue
consumer which gonna read from queue connect and data
according to data size put either to HeavyImagesPool or LightImagePool
wait for the results and write those to the "connection"


read -> 0.1s
process -> 1.0s
10k connections = ~1mb image 10k connections = 100000 mb = 100 gb --> usually RAM 16GB <-- 6 times less connections (images) = 100 gb / 

10k - 100 gb
 x  - 5   gb 

x = 500 connections / images
"""


import asyncio
from concurrent.futures import ProcessPoolExecutor
from typing import List


async def process(connects: List[Connect]):
    await _process_async(connects)


async def _process_async(
    connects: List[Connect],
    cpu_workers: int | None = None,
    io_workers: int | None = None,
    queue_size: int | None = None,
    cpu_load_distribution: float | None = None,
):
    loop = asyncio.get_running_loop()

    # --- настройки ---
    cpu_workers = cpu_workers or 4
    io_workers = io_workers or 20
    queue_size = queue_size or 500
    cpu_load = cpu_load_distribution or 0.7

    heavy_image_threshold = 1_000_000  # 1 MB

    # --- делим CPU пулы ---
    light_workers = max(1, int(cpu_workers * cpu_load))
    heavy_workers = max(1, cpu_workers - light_workers)

    light_pool = ProcessPoolExecutor(max_workers=light_workers)
    heavy_pool = ProcessPoolExecutor(max_workers=heavy_workers)

    pending: asyncio.Queue = asyncio.Queue(maxsize=queue_size)

    # --- producer ---
    async def producer():
        for conn in connects:
            # ждём готовности к чтению
            while not conn.is_ready_to_read():
                await asyncio.sleep(0.01)

            data = conn.read()
            await pending.put((conn, data))

        # сигнал завершения для всех consumer'ов
        for _ in range(io_workers):
            await pending.put(None)

    # --- consumer ---
    async def consumer():
        while True:
            item = await pending.get()

            if item is None:
                break

            conn, data = item

            # выбираем пул
            pool = heavy_pool if len(data) >= heavy_image_threshold else light_pool

            # CPU-bound → в process pool
            thumbnail = await loop.run_in_executor(
                pool,
                generate_thumbnail,
                data,
            )

            # ждём готовности к записи
            while not conn.is_ready_to_write():
                await asyncio.sleep(0.01)

            conn.write(thumbnail)

    # --- запускаем ---
    consumers = [asyncio.create_task(consumer()) for _ in range(io_workers)]

    await asyncio.gather(producer(), *consumers)

    # --- корректное завершение пулов ---
    light_pool.shutdown(wait=True)
    heavy_pool.shutdown(wait=True)


"""
import asyncio
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from typing import Callable, List, Optional, Tuple

from abc import ABC, abstractmethod


# Интерфейсы 

def generate_thumbnail(data: bytes) -> bytes:
    """
    Библиотечная функция генерации миниатюры.
    Трогать не нужно.
    Реализована лучшим доступным способом.
    """
    # Имитация CPU-bound операции генерации миниатюры
    import time
    time.sleep(0.1)  # Примерно 1 секунда по заданию, но для тестов сделаем быстрее
    return data[:4] if len(data) > 4 else data


class Connect(ABC):
    """Это интерфейс, его нельзя изменять."""

    @abstractmethod
    def is_ready_to_read(self) -> bool:
        pass

    @abstractmethod
    def is_ready_to_write(self) -> bool:
        pass

    @abstractmethod
    def read(self) -> bytes:
        pass

    @abstractmethod
    def write(self, data: bytes) -> int:
        pass



# Порог размера (байты): выше — «большое» изображение, отдельный пул
LARGE_IMAGE_THRESHOLD = 1024 * 1024  # 1 MiB

POLL_INTERVAL = 0.01


def _make_executor(max_workers: int, use_processes: bool = True):
    if use_processes:
        try:
            return ProcessPoolExecutor(max_workers=max_workers)
        except (PermissionError, NotImplementedError, OSError):
            pass
    return ThreadPoolExecutor(max_workers=max_workers)


def process(connects: List[Connect],
            io_max_workers: int = 10,
            cpu_max_workers: int = 4,
            queue_maxsize: Optional[int] = None,
            large_image_threshold: int = LARGE_IMAGE_THRESHOLD,
            ready_timeout: Optional[float] = None,
            thumbnail_fn: Optional[Callable[[bytes], bytes]] = None):
    """
    Конкурентная реализация с потоковым пайплайном.
    """
    maxsize = queue_maxsize if queue_maxsize is not None else io_max_workers * 2
    asyncio.run(_process_async(
        connects, io_max_workers, cpu_max_workers, maxsize,
        large_image_threshold, ready_timeout, thumbnail_fn
    ))


async def _process_async(connects: List[Connect],
                         io_max_workers: int,
                         cpu_max_workers: int,
                         queue_maxsize: int,
                         large_image_threshold: int = LARGE_IMAGE_THRESHOLD,
                         ready_timeout: Optional[float] = None,
                         thumbnail_fn: Optional[Callable[[bytes], bytes]] = None):
    """Асинхронная реализация обработки."""
    thumb = thumbnail_fn if thumbnail_fn is not None else generate_thumbnail

    if not connects:
        return

    # Backpressure реализуется исключительно за счет maxsize в очередях
    read_queue: asyncio.Queue[Optional[Tuple[int, Optional[bytes]]]] = asyncio.Queue(maxsize=queue_maxsize)
    write_queue: asyncio.Queue[Optional[Tuple[int, Optional[bytes]]]] = asyncio.Queue(maxsize=queue_maxsize)

    # Семафор ограничивает только одновременные IO операции сети, но не пайплайн в целом
    read_semaphore = asyncio.Semaphore(io_max_workers)

    cpu_large_workers = max(1, cpu_max_workers // 2)
    small_executor = _make_executor(cpu_max_workers)
    large_executor = _make_executor(cpu_large_workers)

    # ============================================================
    # ЗАДАЧА 1: ЧТЕНИЕ (IO-bound)
    # ============================================================

    async def read_task(connect_idx: int, connect: Connect):
        async with read_semaphore:
            try:
                deadline = (asyncio.get_running_loop().time() + ready_timeout) if ready_timeout else None
                while not connect.is_ready_to_read():
                    if deadline is not None and asyncio.get_running_loop().time() >= deadline:
                        raise TimeoutError("Connection not ready within timeout")
                    await asyncio.sleep(POLL_INTERVAL)
                image = await asyncio.to_thread(connect.read)
            except Exception:
                image = None
                
            # Если очередь заполнена, корутина уснет здесь до появления свободного места
            await read_queue.put((connect_idx, image))

    async def read_all_task():
        tasks = [read_task(idx, conn) for idx, conn in enumerate(connects)]
        await asyncio.gather(*tasks)
        await read_queue.put(None)

    # ============================================================
    # ЗАДАЧА 2: ОБРАБОТКА (CPU-bound) — параллельно через create_task
    # ============================================================

    async def process_one_item(connect_idx: int, image_data: Optional[bytes]) -> None:
        if image_data is None:
            await write_queue.put((connect_idx, None))
            return
        loop = asyncio.get_event_loop()
        executor = small_executor if len(image_data) <= large_image_threshold else large_executor
        try:
            thumbnail = await loop.run_in_executor(executor, thumb, image_data)
        except Exception:
            thumbnail = None
            
        # Защита памяти: ждем, если воркеры записи не успевают отправлять готовые миниатюры
        await write_queue.put((connect_idx, thumbnail))

    async def process_task():
        process_tasks: list[asyncio.Task] = []
        while True:
            item = await read_queue.get()
            if item is None:
                break
            connect_idx, image_data = item
            t = asyncio.create_task(process_one_item(connect_idx, image_data))
            process_tasks.append(t)
        await asyncio.gather(*process_tasks)
        for _ in range(io_max_workers):
            await write_queue.put(None)

    # ============================================================
    # ЗАДАЧА 3: ЗАПИСЬ (IO-bound) — пул воркеров
    # ============================================================

    async def write_worker() -> None:
        while True:
            item = await write_queue.get()
            if item is None:
                break
            connect_idx, thumbnail = item
            if thumbnail is not None:
                connect = connects[connect_idx]
                deadline = (asyncio.get_running_loop().time() + ready_timeout) if ready_timeout else None
                while not connect.is_ready_to_write():
                    if deadline is not None and asyncio.get_running_loop().time() >= deadline:
                        break
                    await asyncio.sleep(POLL_INTERVAL)
                if connect.is_ready_to_write():
                    await asyncio.to_thread(connect.write, thumbnail)

    write_workers = [asyncio.create_task(write_worker()) for _ in range(io_max_workers)]

    # ============================================================
    # ЗАПУСК
    # ============================================================

    await asyncio.gather(
        read_all_task(),
        process_task(),
        *write_workers,
    )

    small_executor.shutdown(wait=True)
    large_executor.shutdown(wait=True)
"""