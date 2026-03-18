# semaphore
Semaphore (семафор) — это счётчик, который ограничивает количество одновременно выполняющихся операций.
По факту, ограничивает количество одновременно работающих потоков;

```
есть N "разрешений" (permits)
каждый поток берёт 1
если разрешения закончились → ждём
```

# Чем Semaphore отличается от Lock
- lock - работает для 1 потока
- semaphore - работает для разных потоков

# Semaphore vs BoundedSemaphore
- обычный Semaphore   → можно сделать release() больше, чем acquire() ❌
- BoundedSemaphore    → кинет ошибку ✅

# Semaphore vs Condition
- Condition - ждать, пока выполнится условие
- Semaphore - ограничить количество параллельных операций

# Semaphore vs Queue
- Semaphore - просто ограничивает доступ: "сколько одновременно можно"
- Queue - уже встроенный backpressure, если очередь заполнена → put() блокируется

# Semaphore vs RWLock
- Semaphore - ограничение ресурсов (N)
- RWLock - много читателей / один писатель

# Где используется Semaphore
- Backpressure
- Connection pool
- Rate limiting
- Bulkhead
