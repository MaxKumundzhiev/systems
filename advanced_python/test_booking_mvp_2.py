import pytest
import asyncio

from datetime import date, timedelta

from booking_mvp_v2 import (
    Room,
    Booking,
    Amenity,
    SearchRequest,
    SimpleRoomRepository,
    SearchRoomServiceImpl,
    BookServiceImpl,
    LockPoolManager,
)


# Фильтрация capacity
@pytest.mark.asyncio
async def test_filter_by_capacity():
    room_1 = Room(
        id=1, price=50, capacity=1, amenities={Amenity.wifi, Amenity.ac}, bookings=[]
    )
    repo = SimpleRoomRepository([room_1])
    search = SearchRoomServiceImpl(repo)

    result = await search.find_rooms_by_request(
        request=SearchRequest(
            from_date=date(2024, 1, 1),
            days=5,
            guests=3,
            budget=30_000,
            amenities={Amenity.wifi},
        )
    )

    assert (
        result == []
    ), "Комната должна отфильтроваться по вместимости (capacity < guests)."


# Доступность комнат
@pytest.mark.asyncio
async def test_rooms_availability():
    room_1 = Room(
        id=1,
        price=10_000,
        capacity=2,
        amenities={Amenity.wifi, Amenity.ac},
        bookings=[
            Booking(from_date=date(2024, 1, 1), to_date=date(2024, 2, 1)),
            Booking(from_date=date(2024, 2, 1), to_date=date(2024, 2, 15)),
            Booking(from_date=date(2024, 2, 20), to_date=date(2024, 2, 28)),
        ],
    )
    room_repository = SimpleRoomRepository([room_1])
    search_service = SearchRoomServiceImpl(room_repository)

    assert (
        await search_service.find_rooms_by_request(
            request=SearchRequest(
                from_date=date(2024, 2, 1),
                days=10,
                guests=2,
                budget=1_000_000,
                amenities={Amenity.wifi, Amenity.ac},
            )
        )
        == []
    ), "Ожидался пустой результат: на запрошенные даты нет доступных комнат."


# Конкурентное планирование двух комнат
@pytest.mark.asyncio
async def test_concurrent_booking_different_rooms():
    room_1 = Room(
        id=1,
        price=5_000,
        capacity=2,
        amenities={Amenity.wifi},
        bookings=[],
    )
    room_2 = Room(
        id=2,
        price=5_000,
        capacity=2,
        amenities={Amenity.wifi},
        bookings=[],
    )

    _BASE = date(2026, 3, 10) + timedelta(days=7)

    room_repository = SimpleRoomRepository([room_1, room_2])
    lock_manager = LockPoolManager()
    search_service = SearchRoomServiceImpl(room_repository)
    booking_service = BookServiceImpl(
        repo=room_repository,
        search_room_service=search_service,
        lock_pool_manager=lock_manager,
    )

    results = await asyncio.gather(
        booking_service.book_room(room_id=1, from_date=_BASE, days=5),
        booking_service.book_room(room_id=2, from_date=_BASE, days=5),
    )

    assert (
        len(results) == 2
    ), "Оба параллельных бронирования разных комнат должны завершиться успешно."
    assert (
        len(room_1.bookings) == 1
    ), "Для первой комнаты должна быть создана ровно одна бронь."
    assert (
        len(room_2.bookings) == 1
    ), "Для второй комнаты должна быть создана ровно одна бронь."


# overbooking (2 concurrent requests for 1 room)
@pytest.mark.asyncio
async def test_concurrent_room_booking_one_wins_one_fails():
    room_1 = Room(
        id=1,
        price=10_000,
        capacity=2,
        amenities={Amenity.wifi, Amenity.ac},
        bookings=[],
    )

    room_repository = SimpleRoomRepository([room_1])
    search_service = SearchRoomServiceImpl(room_repository)
    lock_manager = LockPoolManager()

    book_service = BookServiceImpl(
        repo=room_repository,
        search_room_service=search_service,
        lock_pool_manager=lock_manager,
    )

    # ✅ дата должна быть в будущем, иначе упадёт на validation
    from_date = date.today() + timedelta(days=7)

    requests = [
        book_service.book_room(1, from_date, 3),
        book_service.book_room(1, from_date, 4),
    ]

    results = await asyncio.gather(*requests, return_exceptions=True)

    # Должно быть 2 результата: один Booking, один ValueError
    assert len(results) == 2

    successes = [r for r in results if not isinstance(r, Exception)]
    failures = [r for r in results if isinstance(r, Exception)]

    assert len(successes) == 1, f"Expected 1 success, got {successes}"
    assert len(failures) == 1, f"Expected 1 failure, got {failures}"
    assert isinstance(failures[0], ValueError)
    assert "not available" in str(failures[0]).lower()


@pytest.mark.asyncio
async def test_pool_lock_manager_collision():
    """pool_size=1: все комнаты на одном локе, оба бронирования успешны (выполняются последовательно)."""
    _BASE = date(2026, 3, 10) + timedelta(days=7)

    room_1 = Room(id=1, price=5_000, capacity=2, amenities=set(), bookings=[])
    room_2 = Room(id=2, price=5_000, capacity=2, amenities=set(), bookings=[])
    room_repository = SimpleRoomRepository([room_1, room_2])

    search_service = SearchRoomServiceImpl(room_repository)
    lock_manager = LockPoolManager(pool_size=1)
    book_service = BookServiceImpl(
        repo=room_repository,
        search_room_service=search_service,
        lock_pool_manager=lock_manager,
    )

    results = await asyncio.gather(
        book_service.book_room(room_id=1, from_date=_BASE, days=5),
        book_service.book_room(room_id=2, from_date=_BASE, days=5),
    )
    assert (
        len(results) == 2
    ), "Даже при pool_size=1 оба бронирования разных комнат должны завершиться успешно."
    assert (
        len(room_1.bookings) == 1
    ), "Для первой комнаты при pool_size=1 должна появиться одна бронь."
    assert (
        len(room_2.bookings) == 1
    ), "Для второй комнаты при pool_size=1 должна появиться одна бронь."
