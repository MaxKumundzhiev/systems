"""
У нас есть сервер, обрабатывающий запросы, на вход которому поступает уже сформированный список сетевых соединений connects.
Текущий код наивно и последовательно обходит этот список: дожидается готовности соединения, вычитывает данные, генерирует thumbnail и отправляет её обратно.

Проблема:
Код работает слишком медленно.
Известно, что скачивание изображения по сети занимает в среднем 0.1 секунды,
в то время как тяжелая CPU-bound операция генерации миниатюры занимает около 1 секунды

Ситуация:
Прод горит, поэтому сейчас нужно получить максимальное ускорение минимальными усилиями.

Не трогай оптимизацию сетевого ввода-вывода (IO) — сфокусируйся исключительно на вычислительной части
Реализуй параллельную генерацию миниатюр с помощью пула процессов
Используй батчинг, чтобы ускорить процесс

Flow:
    currently the processing happening sequentially and in blocking manner since both connectors and generation of thumbnail are blocking.
    since we are required to implement pharallel CPU execution
        first we need to collect a batch (connect, image)
        the we need ProcessPoolExecutor where we gonna run a batch

"""

import time
from abc import abstractmethod, ABC
from typing import Callable, List
from concurrent.futures import ProcessPoolExecutor, Future, as_completed


## interfaces ##
class Connect(ABC):
    """interface, can not be changed."""

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


def generate_thumbnail(data: bytes) -> bytes:
    """library function. mimics CPU processing of data and returns thumbnail."""
    time.sleep(1)
    return data[:4] if len(data) > 4 else data


def process(
    connects: List[Connect],
    max_workers: int = 4,
    batch_size: int = 10,
    thumbnail_fn: Callable[[bytes], bytes] | None = None,
):
    fn = thumbnail_fn or generate_thumbnail
    jitter = 0.01

    remaining = connects.copy()

    with ProcessPoolExecutor(max_workers=max_workers) as pool:

        while remaining:
            batch: list[tuple[Connect, bytes]] = []
            still_remaining: list[Connect] = []

            # ---- 1. Form batch from ready connections ----
            for connection in remaining:
                if connection.is_ready_to_read():
                    try:
                        data = connection.read()
                        batch.append((connection, data))
                    except Exception:
                        continue
                else:
                    still_remaining.append(connection)

                # stop early if batch is full
                if len(batch) >= batch_size:
                    # оставшиеся тоже сохраняем
                    still_remaining.extend(
                        c
                        for c in remaining
                        if c not in batch and c not in still_remaining
                    )
                    break

            # если ничего не набрали — подождём и повторим
            if not batch:
                time.sleep(jitter)
                remaining = still_remaining
                continue

            # ---- 2. Submit CPU tasks ----
            future_map: dict[Future, Connect] = {
                pool.submit(fn, data): connection for (connection, data) in batch
            }

            # ---- 3. Handle results ----
            for future in as_completed(future_map):
                connection = future_map[future]

                try:
                    thumbnail = future.result()
                except Exception:
                    continue

                while not connection.is_ready_to_write():
                    time.sleep(jitter)

                try:
                    connection.write(thumbnail)
                except Exception:
                    continue

            # ---- 4. Update remaining ----
            remaining = still_remaining
