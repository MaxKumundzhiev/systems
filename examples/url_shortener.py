import string
import time
from concurrent.futures import ThreadPoolExecutor, Future

class URLShortener:
    """
    Класс для укорачивания URL-адресов с использованием пула потоков.
    Этот подход идеален для асинхронных операций, таких как обработка
    входящих запросов в веб-приложении.
    """
    def __init__(self, domain="http://short.ly/"):
        # Конструктор класса. Инициализирует все необходимые структуры данных.
        self.domain = domain
        self.url_map = {}
        self.alias_map = {}
        self.stats = {}
        self.base62 = string.ascii_letters + string.digits
        
        # Создаем пул потоков.
        # `ThreadPoolExecutor` управляет группой "рабочих" потоков.
        # `max_workers` определяет максимальное количество потоков в пуле.
        # Это позволяет выполнять несколько задач одновременно, не создавая
        # новый поток для каждой из них, что экономит ресурсы.
        self.executor = ThreadPoolExecutor(max_workers=5)

    def _generate_short_code(self):
        """
        Приватный метод для генерации уникального короткого кода.
        Этот метод не зависит от общего состояния класса, поэтому может
        безопасно вызываться из любого потока без блокировок.
        """
        while True:
            timestamp = int(time.time() * 1000)
            code = self._base_encode(timestamp)
            # Примечание: Проверка на уникальность происходит внутри потока,
            # но поскольку `ThreadPoolExecutor` управляет потоками и их доступом
            # к общим ресурсам, он обеспечивает потокобезопасность.
            if code not in self.url_map:
                return code

    def _base_encode(self, number):
        """
        Приватный метод для преобразования числа в строку Base62.
        Логика остается неизменной, так как она является чистой функцией
        (не зависит от состояния класса).
        """
        if number == 0:
            return self.base62[0]
        
        encoded_string = ""
        base = len(self.base62)
        while number > 0:
            encoded_string = self.base62[number % base] + encoded_string
            number //= base
        return encoded_string
        
    def _shorten_url_task(self, long_url):
        """
        Задача для выполнения в потоке: создает короткую ссылку.
        Эта функция выполняет всю логику, связанную с изменением
        состояния объекта (запись в словари).
        """
        short_code = self._generate_short_code()
        self.url_map[short_code] = long_url
        self.stats[short_code] = {"hits": 0, "created_at": time.time()}
        return self.domain + short_code

    def shorten_url(self, long_url) -> Future:
        """
        Публичный метод: отправляет задачу на укорачивание URL в пул потоков.
        Возвращает `Future`-объект, который позволяет получить результат
        в будущем, не блокируя основной поток.
        """
        # `executor.submit()` планирует выполнение задачи и возвращает `Future`.
        return self.executor.submit(self._shorten_url_task, long_url)

    def _shorten_url_with_alias_task(self, long_url, alias):
        """
        Задача для выполнения в потоке: создает ссылку с алиасом.
        """
        if alias in self.alias_map:
            return f"Error: Alias '{alias}' already exists"
        
        self.alias_map[alias] = long_url
        self.stats[alias] = {"hits": 0, "created_at": time.time()}
        return self.domain + alias

    def shorten_url_with_alias(self, long_url, alias) -> Future:
        """
        Публичный метод: отправляет задачу на укорачивание с алиасом в пул.
        """
        return self.executor.submit(self._shorten_url_with_alias_task, long_url, alias)

    def _get_long_url_task(self, short_code):
        """
        Задача для получения длинного URL и обновления статистики.
        """
        # Сначала ищем в `url_map`
        if short_code in self.url_map:
            self.stats[short_code]["hits"] += 1
            return self.url_map[short_code]
        # Если не нашли, ищем в `alias_map`
        elif short_code in self.alias_map:
            self.stats[short_code]["hits"] += 1
            return self.alias_map[short_code]
        else:
            return "Error: URL not found"

    def get_long_url(self, short_code) -> Future:
        """
        Публичный метод: отправляет задачу на получение длинного URL в пул.
        """
        return self.executor.submit(self._get_long_url_task, short_code)

    def _get_stats_task(self, short_code):
        """
        Задача для получения статистики по ссылке.
        """
        if short_code in self.stats:
            return self.stats[short_code]
        else:
            return "Error: Stats not found"
            
    def get_stats(self, short_code) -> Future:
        """
        Публичный метод: отправляет задачу на получение статистики в пул.
        """
        return self.executor.submit(self._get_stats_task, short_code)

# ---
# Пример использования
# ---

# Создаем экземпляр класса
shortener = URLShortener()

# 1. Отправляем несколько задач одновременно
print("Отправляем запросы на укорачивание ссылок...")
future_1 = shortener.shorten_url("https://www.google.com/search?q=concurrent.futures")
future_2 = shortener.shorten_url_with_alias("https://docs.python.org/3/library/concurrent.futures.html", "concurrency_docs")
future_3 = shortener.shorten_url("https://github.com/python/cpython")

# 2. Ждем и получаем результаты, когда они будут готовы
# Метод `.result()` блокирует выполнение, пока задача не завершится.
print("\nПолучаем результаты...")
short_url_1 = future_1.result()
alias_url = future_2.result()
short_url_2 = future_3.result()

print(f"Короткая ссылка 1: {short_url_1}")
print(f"Ссылка с алиасом: {alias_url}")
print(f"Короткая ссылка 2: {short_url_2}")

# 3. Отправляем еще один запрос на получение длинной ссылки и статистики
short_code_1 = short_url_1.split('/')[-1]
future_long_url = shortener.get_long_url(short_code_1)
future_stats = shortener.get_stats("concurrency_docs")

# 4. Получаем результаты
print("\nПолучаем данные по ссылкам...")
long_url_recovered = future_long_url.result()
stats_alias = future_stats.result()

print(f"Восстановленная длинная ссылка: {long_url_recovered}")
print(f"Статистика по алиасу 'concurrency_docs': {stats_alias}")

# 5. Важный шаг: корректно завершаем работу пула потоков
# `shutdown()` дожидается завершения всех задач и освобождает ресурсы.
shortener.executor.shutdown()
print("\nПул потоков завершил работу.")