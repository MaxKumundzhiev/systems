# intro
idea behind the locks. as we remember, there are 2 types of locks
1. asyncio.Lock - locks on the level of courotine
2. threading.Lock - locks on the level OS
+ there is a processes Lock as well.


Lock is a mutex primitive which solves
    - race condition (2 concurrent whatever it is) trying to change a state
    - dead lock (incorrect way to acquire and release locks)


RWLock (read | write lock) - the intuition behind is this is type of lock which allows to concurrently with state of object when we need both read and write concurrently.

It usually has 2 modes:
    - read lock: many readers allowed together
    - write lock: only one writer, and no readers at the same time

Assume a situation, there is a Booking service,
where concurrent users who can
    - check availability
    - reserve a room

We want checking availability being concurrent as much as possible and reserve room being concurrent as well, but avoiding condition (overbooking problem). This might be achieved exactly be introducing RWLock for a booking service.

```
Imagine a hotel room availability board.

Many customers can look at availability at the same time
    → safe, nobody changes data
But when one customer books the last room, that operation changes state
    → writer must be alone

So:
    check_availability() → reader
    book_room() / cancel_booking() → writer
```

