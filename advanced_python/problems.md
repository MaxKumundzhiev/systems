Google: Индексатор распределенного лога (Log Indexer)
```
Контекст: Обработка петабайт поисковых логов для построения обратного индекса.

Входные данные: Поток текстовых строк из распределенной очереди (аналог Pub/Sub).

Ограничения: Память ограничена 512 MiB. Нужно считать частоту появления термов (слов), но нельзя хранить весь словарь в RAM.

Задача: Реализовать LogProcessor, который сбрасывает промежуточные результаты (shard) на диск, когда RAM заполняется на 80%, а затем объединяет их (External Merge Sort) для финальной выдачи.

Нюанс: Использование heapq.merge для эффективного слияния отсортированных чанков без загрузки их целиком.
```

Meta: Агрегатор графа друзей (Social Graph Aggregator)
```
Контекст: Сбор данных о друзьях пользователя из разных шардов базы данных.

Входные данные: Список ID пользователей.

Ограничения: Rate-limit на запросы к DB (не более 100 RPS). Время ответа всей функции ограничено (timeout).

Задача: Реализовать асинхронный метод fetch_connections, который использует asyncio.Semaphore для контроля нагрузки и asyncio.gather с ограничением конкурентности.

Нюанс: Нужно корректно обрабатывать частичные отказы (если один шард упал, вернуть данные по остальным).
```

Netflix: Адаптивный стриминг чанков (Video Chunk Streamer)
```
Контекст: Раздача видео-контента в зависимости от пропускной способности сети.

Входные данные: Бинарный поток видео.

Ограничения: Клиент запрашивает конкретные сегменты (по 2 сек). Сервер должен на лету определять, какой битрейт отдавать.

Задача: Реализовать StreamManager, который буферизует входящий поток, нарезает его на именованные сегменты chunk_001_low, chunk_001_high и сохраняет в кэш.

Нюанс: Реализация "Backpressure": если хранилище не успевает записывать чанки, нужно замедлять чтение из источника, чтобы не переполнить буфер.
```

Snapchat: Система эфемерных хранилищ (TTL Storage)
```
Контекст: Очистка медиа-данных сразу после истечения срока жизни (TTL).

Входные данные: Метаданные файлов с меткой времени удаления.

Ограничения: Нельзя блокировать основной поток записи новыми файлами ради удаления старых.

Задача: Реализовать CleanupWorker, который работает в фоне, сканирует реестр файлов и удаляет просроченные.

Нюанс: Использование asyncio.Queue для передачи задач на удаление и обработка исключений при попытке удалить файл, который уже удален или заблокирован.
```

DoorDash: Гео-фенсинг заказов (Order Geo-Fencing)
```
Контекст: Сопоставление координат курьеров и зон доставки ресторанов.

Входные данные: Поток координат (lat, lon) от тысяч курьеров.

Ограничения: Высокая частота обновлений. Нельзя делать запрос в БД на каждое движение курьера.

Задача: Реализовать LocationCache, который хранит последние позиции в памяти (LRU-кэш) и асинхронно "пачками" (batch) обновляет состояние в основной БД.

Нюанс: Атомарность обновлений. Что если два курьера обновились одновременно? (Использование asyncio.Lock).
```

DoorDash: Система обработки «всплесков» заказов (Order Throttling)
```
Контекст: В пятницу вечером количество заказов резко возрастает. Наша микросервисная архитектура начинает "захлебываться", и внешние API ресторанов отвечают 429 Too Many Requests.

Задача: Реализовать асинхронный контроллер DispatchManager, который принимает заказы из очереди и отправляет их в рестораны.

AsyncIO топики: asyncio.Queue (буферизация), asyncio.Semaphore (ограничение конкурентных запросов).

Реалистичный сценарий: Если очередь заказов превышает 1000 элементов, система должна начать отвечать пользователю "High Demand" (отказ по Backpressure), чтобы не уронить базу данных.

Нюанс: Реализовать механизм "Retry с экспоненциальной задержкой" (exponential backoff) для упавших запросов.
```

Netflix: УмныйPrefetch-механизм (Predictive Video Loader)
```
Контекст: Чтобы видео начиналось мгновенно, плеер должен заранее подгружать следующие 3 чанка, пока пользователь смотрит текущий.

Задача: Реализовать PlaybackBuffer, который управляет фоновыми загрузками.

AsyncIO топики: asyncio.create_task (фоновое выполнение), asyncio.Event (сигнализация о готовности данных).

Реалистичный сценарий: Если пользователь нажимает "перемотка" (seek), все текущие фоновые загрузки должны быть немедленно отменены, чтобы не тратить трафик и ресурсы CPU.

Нюанс: Использование task.cancel() и корректная обработка asyncio.CancelledError.
```

Meta: Агрегатор ленты новостей (Social Feed Fan-Out)
```
Контекст: Для сборки ленты нужно запросить данные из 5 сервисов: Посты, Реклама, Рекомендации, Друзья и Сторис.

Задача: Реализовать метод build_feed, который запрашивает все данные параллельно.

AsyncIO топики: asyncio.gather с параметром return_exceptions=True, asyncio.wait_for (таймауты).

Реалистичный сценарий: Рекламный сервис часто тормозит. Если он не ответил за 200мс, лента должна отобразиться без рекламы, а не выдать ошибку 500.

Нюанс: Использование asyncio.as_completed для того, чтобы начать рендерить части страницы, как только они приходят.
```

Snapchat: "Взрывное" удаление медиа (Mass Purge Worker)
```
Контекст: После завершения масштабного мероприятия (например, фестиваля) тысячи "публичных историй" истекают одновременно. Нам нужно очистить S3 и обновить индексы в БД.

Задача: Реализовать воркер, который обрабатывает пачки (batches) ID на удаление.

AsyncIO топики: asyncio.PriorityQueue (удаление платных аккаунтов — приоритет выше), asyncio.gather для батчинга.

Реалистичный сценарий: Нужно балансировать между скоростью удаления и нагрузкой на БД, чтобы не заблокировать таблицы для живых пользователей.

Нюанс: Группировка мелких запросов в один "Batch Delete" запрос к БД.
```

DoorDash: Агрегатор статусов курьеров (Real-time Courier Tracker)
```
Контекст: На карте клиента нужно отображать положение курьера. Координаты приходят в WebSocket со скоростью 10 обновлений в секунду от 50 000 курьеров.

Задача: Реализовать CoordinateBuffer. Он должен собирать координаты и раз в 1 секунду отправлять «батч» (пачку) последних позиций в Redis, чтобы не спамить базу данных.

AsyncIO топики: asyncio.gather для параллельной записи, asyncio.sleep в бесконечном цикле (ticker), dict как thread-safe хранилище в рамках одного Event Loop.

Реалистичность: Если запись в Redis тормозит, буфер не должен раздуваться до бесконечности (нужен лимит размера).

Нюанс: Как обработать ситуацию, когда курьер отключился? (Очистка старых данных из памяти).
```

Snapchat: Параллельный загрузчик медиа с «умным» таймаутом
```
Контекст: При открытии истории (Story) приложение скачивает 10 видео-фрагментов одновременно.

Задача: Реализовать MediaDownloader.download_all(urls).

AsyncIO топики: asyncio.as_completed или asyncio.wait.

Реалистичность: У пользователя плохой интернет. Если первые 2 видео загрузились быстро, а 3-е висит более 5 секунд — нужно отменить его загрузку и перейти к 4-му, чтобы пользователь не смотрел на "колесо загрузки".

Нюанс: Использование asyncio.wait(..., return_when=FIRST_COMPLETED) и task.cancel().
```

Netflix: Система «Warm-up» кэша (Thundering Herd Protection)
```
Контекст: Выходит новая серия «Очень странных дел». Миллион человек одновременно запрашивают метаданные серии. Кэш пуст. Если все запросы полетят в БД — она упадет.

Задача: Реализовать CoalescingCache. Если 1000 корутин запрашивают один и тот же key, только одна должна пойти в БД, а остальные — ждать её результата.

AsyncIO топики: asyncio.Future, asyncio.Lock или словарь фьючерсов.

Реалистичность: Это классическая проблема "Thundering Herd" (грохочущее стадо).

Нюанс: Что если запрос, который пошел в БД, упал с ошибкой? Все остальные 999 тоже должны получить ошибку или попробовать снова?
```


Instgram
```
1. Instagram Stories: Параллельный публикатор (Uploader Pipeline)
Контекст: Когда вы публикуете Story, приложение делает три вещи: сохраняет оригинал, создает превью (thumbnail) и нарезает видео на чанки для адаптивного стриминга.

Задача: Реализовать StoryPublisher. Он должен принимать видеопоток и параллельно запускать три задачи.

AsyncIO топики: asyncio.gather, asyncio.create_task, работа с BytesIO.

Реалистичность: Если создание превью упало, основная загрузка видео не должна прерываться. Однако, если упала загрузка оригинала, вся публикация считается провальной.

Нюанс: Реализовать «прогресс-бар», который агрегирует статус всех трех подзадач и сообщает об общем проценте завершения.

2. Live Broadcast: Агрегатор комментариев (Comment Buffer)
Контекст: На популярном стриме (например, 1 млн зрителей) комментарии летят со скоростью 5000 в секунду. Если обновлять UI на каждый чих, телефон пользователя сгорит.

Задача: Реализовать Commentshub, который собирает комментарии из асинхронного источника и отдает их «пачками» раз в 300 мс.

AsyncIO топики: asyncio.Queue, asyncio.wait_for.

Реалистичность: Нужно реализовать «вытеснение» (dropping). Если за 300 мс пришло более 50 комментариев, мы берем только 50 последних, а остальные отбрасываем, чтобы не перегружать сеть и экран.

Нюанс: Использование asyncio.TaskGroup (для Python 3.11+) для управления жизненным циклом фоновых обработчиков.

3. Feed: Умный "ViewPort" подгрузчик (Infinite Scroll Prefetcher)
Контекст: Пользователь быстро скроллит ленту. Нам нужно подгружать посты заранее (prefetch), но если пользователь проскочил пост очень быстро, загрузку его тяжелых медиа нужно отменить.

Задача: Реализовать FeedManager, который отслеживает "индекс" текущего просмотра.

AsyncIO топики: asyncio.Task.cancel, dict для хранения активных задач загрузки.

Реалистичность: При переходе на индекс N, система должна начинать загрузку постов N+1, N+2, N+3. Если пользователь резко скрольнул к индексу N+100, задачи для N+1..N+3 должны быть немедленно убиты.

Нюанс: Обработка asyncio.CancelledError для очистки частично скачанных временных файлов.
```



Concurrent Feature Flag Service
```text
Ты разрабатываешь сервис фич-флагов (как LaunchDarkly), который используется тысячами потоков.

Реализуй класс:
class FeatureStore:
    ...

Он хранит фичи и их значения:
"new_ui" → True
"beta_mode" → False

Требования
1. Чтение (очень частое)
def is_enabled(self, key: str) -> bool:

Возвращает значение флага
Если флаг не существует → KeyError
Должен поддерживать параллельные чтения

2. Запись (редкая)
def set_feature(self, key: str, value: bool) -> None:

Устанавливает значение
Должна быть эксклюзивной

3. Удаление
def delete_feature(self, key: str) -> None:

Удаляет флаг
Если нет → KeyError

Конкурентные требования
Одновременно может быть:
    много читателей ✅
    только один писатель ❗
    Пока идёт запись:
        чтение запрещено
    Пока есть читатели:
        запись ждёт
    Используй RWLock

❓ Что будет, если читатели идут бесконечно?
    (writer starvation)
❓ Как добавить приоритет писателей?
❓ Как сделать lock-free версию?
    (copy-on-write / immutable dict)
❓ Что быстрее:
    RWLock
    или просто Lock?
❓ Как масштабировать на несколько процессов?
```

🧩 1. High-Throughput Log Ingestion (Google / Netflix style)
Условие

Сервис принимает миллионы логов в секунду от распределённых клиентов.
Нужно агрегировать и писать в storage батчами, чтобы минимизировать I/O.

Требования:

Принимать данные через API

Гарантировать order-preserving batching

Flush батчей по таймеру или при достижении размера

Code Backbone
from collections import deque
from threading import Lock, Thread
import time

class LogBatcher:
    def __init__(self, batch_size: int, flush_interval: float):
        self.queue = deque()
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.lock = Lock()

    def add_log(self, log: str):
        """Добавляет лог в очередь"""
        ...

    def _flush(self, logs: list[str]):
        """Записывает батч в storage"""
        ...

    def run_flusher(self):
        """Запуск потока для периодической отправки батчей"""
        ...

Follow-up:

Сделать потокобезопасным

Добавить backpressure

Асинхронная версия с asyncio

Поддержка C10K / high-throughput

🧩 2. Streaming Analytics (LinkedIn / Kafka style)
Условие

Поток событий (например, клики пользователей) приходит в реальном времени.
Нужно скользящее окно по времени (5 минут) для подсчёта уникальных пользователей.

Требования:

Поддерживать real-time подсчёт

Асинхронная обработка

Window slide каждые 10 секунд

Code Backbone
from collections import deque
from datetime import datetime, timedelta
import asyncio

class SlidingWindowCounter:
    def __init__(self, window_seconds: int):
        self.window = deque()  # (timestamp, user_id)
        self.window_seconds = window_seconds

    async def add_event(self, user_id: str):
        now = datetime.now()
        self.window.append((now, user_id))
        await self._evict_old(now)

    async def _evict_old(self, now: datetime):
        """Удаляем события старше окна"""
        ...

    def count_unique(self) -> int:
        """Возвращает количество уникальных пользователей"""
        ...

Follow-up:

Поддержка миллионы событий/сек

Использовать HyperLogLog для экономии памяти

Асинхронная обработка через asyncio.gather

🧩 3. Batch Email Sender (Amazon style)
Условие

Сервис собирает email-запросы и отправляет их батчами каждые 1 секунду или когда набирается 100 писем.

Требования:

Thread-safe

Минимизировать количество сетевых запросов

Логирование успеха/ошибок

Code Backbone
from threading import Lock, Thread
import time

class EmailBatcher:
    def __init__(self, batch_size: int, flush_interval: float):
        self.queue = []
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.lock = Lock()

    def add_email(self, email: str):
        ...

    def _send_batch(self, batch: list[str]):
        ...

    def run_flusher(self):
        ...

Follow-up:

Поддержка priority email

Retry failed emails

Распараллеливание отправки для ускорения

🧩 4. Video Stream Chunking (Netflix / YouTube style)
Условие

Видео поток приходит по сети. Нужно нарезать его на чанки фиксированного размера и отправлять в CDN асинхронно, не блокируя основной поток.

Требования:

Минимизировать задержку

Thread-safe + asyncio-friendly

Поддержка backpressure

Code Backbone
import asyncio
from collections import deque

class VideoStreamer:
    def __init__(self, chunk_size: int):
        self.chunk_size = chunk_size
        self.buffer = bytearray()
        self.queue = deque()

    async def add_data(self, data: bytes):
        self.buffer.extend(data)
        while len(self.buffer) >= self.chunk_size:
            chunk = self.buffer[:self.chunk_size]
            self.buffer = self.buffer[self.chunk_size:]
            self.queue.append(chunk)
            await self._send_chunk(chunk)

    async def _send_chunk(self, chunk: bytes):
        """Асинхронная отправка чанка"""
        ...

Follow-up:

Поддержка нескольких пользователей (fan-out)

Adaptive chunking по скорости сети

Поддержка resume / retry

🧩 5. Sensor Data Streaming (Tesla / IoT style)
Условие

Ты получаешь поток данных с IoT-сенсоров.
Нужно:

Буферизовать данные по батчам 1000 значений или каждые 0.5 сек

Отправлять в аналитическую систему

Не терять данные при перегрузке

Требования:

Асинхронная обработка

Thread-safe

Sliding window + alerting

Code Backbone
import asyncio
from collections import deque

class SensorBatcher:
    def __init__(self, batch_size: int, flush_interval: float):
        self.queue = deque()
        self.batch_size = batch_size
        self.flush_interval = flush_interval

    async def add_sensor_data(self, data: dict):
        self.queue.append(data)
        if len(self.queue) >= self.batch_size:
            await self._flush()

    async def _flush(self):
        batch = [self.queue.popleft() for _ in range(min(self.batch_size, len(self.queue)))]
        await self._send_batch(batch)

    async def _send_batch(self, batch: list[dict]):
        ...

Follow-up:

Асинхронная обработка

Поддержка backpressure

Sliding window статистика + alerting



🧩 1. Service Isolation with Bulkheads (Amazon style)
Условие

Сервис обрабатывает несколько типов запросов: payments, search, recommendations.

Нужно гарантировать, что перегрузка одного типа не влияет на другие (Bulkhead pattern).

Требования:

Разделить ресурсы (threads / connection pools) на «отсеки» по типу запроса

Если один сегмент перегружен → запросы в этом сегменте отклоняются или ставятся в очередь

Thread-safe / asyncio-friendly

Code Backbone
from threading import Lock, Semaphore, Thread
import time

class BulkheadService:
    def __init__(self, payment_limit: int, search_limit: int, rec_limit: int):
        self.payment_sem = Semaphore(payment_limit)
        self.search_sem = Semaphore(search_limit)
        self.rec_sem = Semaphore(rec_limit)

    def handle_payment(self, task):
        with self.payment_sem:
            self._process(task)

    def handle_search(self, task):
        with self.search_sem:
            self._process(task)

    def handle_recommendation(self, task):
        with self.rec_sem:
            self._process(task)

    def _process(self, task):
        """Симуляция обработки запроса"""
        time.sleep(0.1)

Follow-up:

Асинхронная версия (asyncio.Semaphore)

Добавить metrics/alerting, когда сегмент перегружен

Поддержка dynamic resizing bulkhead

🧩 2. Hedging / Speculative Requests (Google style)
Условие

Сервис делает внешний API-запрос. Иногда ответы приходят медленно.
Чтобы уменьшить latency, нужно отправлять hedged request (второй запрос после таймаута).

Требования:

Отправить основной запрос

Если timeout > X мс → отправить второй (hedge) запрос

Вернуть первый успешный ответ

Отменить остальные запросы, когда ответ получен

Code Backbone
import asyncio

async def fetch_from_service(service_id: int) -> str:
    """Симуляция внешнего запроса"""
    await asyncio.sleep(0.1 * service_id)
    return f"response_from_{service_id}"

async def hedged_request(timeout: float):
    task1 = asyncio.create_task(fetch_from_service(1))
    try:
        return await asyncio.wait_for(task1, timeout)
    except asyncio.TimeoutError:
        task2 = asyncio.create_task(fetch_from_service(2))
        done, pending = await asyncio.wait([task1, task2], return_when=asyncio.FIRST_COMPLETED)
        for p in pending:
            p.cancel()
        return list(done)[0].result()

Follow-up:

Настроить dynamic hedge delay

Поддержка bulkhead + hedge

Метрики: latency p50/p95/p99

🧩 3. Bulkhead + Queue Overflow Handling (Netflix style)
Условие

Сервис обрабатывает video transcoding jobs.
Каждый сегмент (HD, 4K, Mobile) имеет отдельный пул рабочих потоков (Bulkhead).

Если пул перегружен → jobs ставятся в очередь до limit

Если очередь заполнена → job отклоняется с ошибкой

Требования:

Thread-safe queue + semaphore

Batch processing (по 5 jobs)

Метрики отказов

Code Backbone
from threading import Semaphore, Lock, Thread
from queue import Queue, Full
import time

class TranscodingBulkhead:
    def __init__(self, hd_limit: int, hd_queue_size: int):
        self.hd_sem = Semaphore(hd_limit)
        self.hd_queue = Queue(maxsize=hd_queue_size)
        self.lock = Lock()

    def submit_hd_job(self, job):
        try:
            self.hd_queue.put_nowait(job)
        except Full:
            print("HD queue full! Rejecting job")
            return

        Thread(target=self._process_hd).start()

    def _process_hd(self):
        with self.hd_sem:
            job = self.hd_queue.get()
            time.sleep(0.1)  # simulate processing

Follow-up:

Асинхронная версия с asyncio.Queue

Dynamic pool resizing

Метрики: average queue length, reject rate

🧩 4. HOL + Retry Strategy (Microsoft style)
Условие

API иногда возвращает 5xx ошибки. Нужно:

Отправить запрос

Retry с hedge для медленных или ошибочных ответов

Максимум N retries

Требования:

Async-friendly

Backoff strategy (exponential / jitter)

Отмена параллельных задач при успехе

Code Backbone
import asyncio
import random

async def unreliable_service():
    await asyncio.sleep(random.uniform(0.05, 0.2))
    if random.random() < 0.3:
        raise Exception("5xx")
    return "ok"

async def hedged_retry(max_retries: int):
    for attempt in range(max_retries):
        task = asyncio.create_task(unreliable_service())
        try:
            return await asyncio.wait_for(task, 0.1)
        except Exception:
            task.cancel()
            await asyncio.sleep(0.05 * (2 ** attempt))
    raise Exception("All retries failed")

Follow-up:

Combine Bulkhead + HOL

Track latency percentiles

Dynamic hedging for slow endpoints

🧩 5. Bulkhead with Multi-tenancy Isolation (Uber style)
Условие

Много клиентов используют сервис одновременно.
Нужно изолировать ресурсы по клиентам (bulkhead per tenant), чтобы перегрузка одного клиента не блокировала остальных.

Требования:

Thread-safe / async-safe per tenant

Отклонение запросов, если пул или очередь клиента заполнены

Метрики per-tenant

Code Backbone
from threading import Semaphore, Lock
from collections import defaultdict
import time

class MultiTenantBulkhead:
    def __init__(self, tenant_limit: int):
        self.tenant_sems = defaultdict(lambda: Semaphore(tenant_limit))
        self.lock = Lock()

    def handle_request(self, tenant_id: str, task):
        sem = self.tenant_sems[tenant_id]
        with sem:
            self._process(task)

    def _process(self, task):
        time.sleep(0.1)

Follow-up:

Asyncio version per tenant

Dynamic tenant limits

Metrics per tenant: queue length, rejects, latency


🧩 1. Rate-Limited API Gateway (Amazon style)
Условие

API Gateway принимает запросы от клиентов.
Сервис имеет лимит одновременных запросов, чтобы не перегрузить бэкенд.

Нужно реализовать backpressure: новые запросы ждут или отклоняются, если лимит достигнут.

Требования:

Ограничение количества параллельных запросов через Semaphore

Thread-safe или async-friendly

Метрики: dropped requests, queue length

Code Backbone
from threading import Semaphore, Thread
import time
import random

class RateLimitedGateway:
    def __init__(self, max_concurrent: int):
        self.sem = Semaphore(max_concurrent)

    def handle_request(self, request_id: int):
        if not self.sem.acquire(blocking=False):
            print(f"Request {request_id} rejected due to backpressure")
            return
        try:
            self._process(request_id)
        finally:
            self.sem.release()

    def _process(self, request_id: int):
        time.sleep(random.uniform(0.05, 0.2))
        print(f"Request {request_id} processed")

Follow-up:

Асинхронная версия с asyncio.Semaphore

Настройка queue + drop strategy

Метрики: p50/p95 latency, reject rate

🧩 2. Bulk Data Ingestion with Backpressure (Google style)
Условие

Сервис получает поток данных от IoT устройств.
Если поток превышает скорость обработки, нужно замедлять входящие данные (backpressure) через семафор.

Требования:

Async-friendly ingestion

Semaphore для ограничения concurrency

Drop или throttle данные при перегрузке

Code Backbone
import asyncio
from asyncio import Semaphore
import random

class IoTIngestor:
    def __init__(self, max_workers: int):
        self.sem = Semaphore(max_workers)

    async def ingest(self, data):
        async with self.sem:
            await self._process(data)

    async def _process(self, data):
        await asyncio.sleep(random.uniform(0.01, 0.05))
        print(f"Ingested: {data}")

Follow-up:

Настроить dynamic semaphore (адаптивная скорость)

Метрики: queue length, dropped messages

Поддержка high-throughput C10k

🧩 3. Video Upload Service with Concurrency Limit (Netflix style)
Условие

Много пользователей загружают видео одновременно.
Сервис может обрабатывать только N видео одновременно.

Нужно:

Ограничить concurrency через Semaphore

Если лимит достигнут → показать пользователю “retry later” (backpressure)

Code Backbone
from threading import Semaphore, Thread
import time

class VideoUploader:
    def __init__(self, max_uploads: int):
        self.sem = Semaphore(max_uploads)

    def upload(self, video_id: str):
        if not self.sem.acquire(blocking=False):
            print(f"Video {video_id} rejected, try later")
            return
        try:
            self._process(video_id)
        finally:
            self.sem.release()

    def _process(self, video_id: str):
        time.sleep(0.2)  # simulate upload
        print(f"Video {video_id} uploaded")

Follow-up:

Асинхронная версия с asyncio

Метрики: reject rate, queue time

Support bulk uploads / batch processing

🧩 4. Streaming Chat Service (Slack-style)
Условие

Сервис обрабатывает реальное время чата.
Если слишком много сообщений одновременно → нужно замедлять поток через backpressure.

Требования:

Ограничить количество одновременно обрабатываемых сообщений

Drop или delay при перегрузке

Thread-safe / async-friendly

Code Backbone
import asyncio
from asyncio import Semaphore
import random

class ChatServer:
    def __init__(self, max_concurrent: int):
        self.sem = Semaphore(max_concurrent)

    async def handle_message(self, msg: str):
        if self.sem.locked():
            print(f"Backpressure: message '{msg}' delayed")
        async with self.sem:
            await self._process(msg)

    async def _process(self, msg: str):
        await asyncio.sleep(random.uniform(0.01, 0.05))
        print(f"Processed message: {msg}")

Follow-up:

Sliding window metrics: message latency, backpressure events

Adaptive concurrency (increase limit if CPU idle)

Batch messages for storage or analytics

🧩 5. Sensor Event Processing with Priority Queue (Tesla / IoT)
Условие

Сенсорные данные приходят с разных устройств.

Есть лимит на обработку одновременно

Высокоприоритетные события должны обрабатываться раньше низкоприоритетных

Backpressure для низкоприоритетных событий, если лимит достигнут

Code Backbone
import asyncio
from asyncio import Semaphore
from heapq import heappush, heappop
import random

class PrioritySensorProcessor:
    def __init__(self, max_workers: int):
        self.sem = Semaphore(max_workers)
        self.queue = []

    async def add_event(self, priority: int, event):
        heappush(self.queue, (priority, event))
        await self._process_next()

    async def _process_next(self):
        if not self.queue:
            return
        async with self.sem:
            priority, event = heappop(self.queue)
            await asyncio.sleep(random.uniform(0.01, 0.05))
            print(f"Processed event {event} with priority {priority}")

Follow-up:

Метрики: queue length, dropped low-priority events

Dynamic semaphore limits per device

Batch processing of low-priority events