import pytest
import asyncio

from netflix_playback import (
    PlayRequest,
    SimpleSessionsPlaybackRepository,
    SessionPlaybackServiceImpl,
    SessionsLockManager,
)


@pytest.mark.asyncio
async def test_idempotency_same_request_concurrent():
    repo = SimpleSessionsPlaybackRepository()
    locks = SessionsLockManager(pool_size=64)
    service = SessionPlaybackServiceImpl(repo, locks)

    request = PlayRequest(user_id=1, title_id=100, client_request_id="req-1-100")

    res = await asyncio.gather(
        service.start_session(request),
        service.start_session(request),
        service.start_session(request),
    )

    assert len({s.id for s in res}) == 1
    assert all(s.client_request_id == "req-1-100" for s in res)
    assert all(s.user_id == 1 and s.title_id == 100 for s in res)


@pytest.mark.asyncio
async def test_idempotency_same_request_sequential():
    repo = SimpleSessionsPlaybackRepository()
    locks = SessionsLockManager(pool_size=64)
    service = SessionPlaybackServiceImpl(repo, locks)

    request = PlayRequest(user_id=2, title_id=200, client_request_id="req-2-200")

    s1 = await service.start_session(request)
    s2 = await service.start_session(request)
    s3 = await service.start_session(request)

    assert s1.id == s2.id == s3.id


@pytest.mark.asyncio
async def test_different_request_ids_create_different_sessions():
    repo = SimpleSessionsPlaybackRepository()
    locks = SessionsLockManager(pool_size=64)
    service = SessionPlaybackServiceImpl(repo, locks)

    r1 = PlayRequest(user_id=1, title_id=100, client_request_id="req-A")
    r2 = PlayRequest(user_id=1, title_id=100, client_request_id="req-B")
    r3 = PlayRequest(user_id=1, title_id=100, client_request_id="req-C")

    res = await asyncio.gather(
        service.start_session(r1),
        service.start_session(r2),
        service.start_session(r3),
    )

    assert len({s.id for s in res}) == 3
    assert len({s.client_request_id for s in res}) == 3


@pytest.mark.asyncio
async def test_same_request_id_ignores_changed_payload():
    """
    В реальном мире payload для одного request_id должен быть одинаковый.
    Этот тест фиксирует поведение: idempotency ключ решает всё.
    Если пришёл тот же client_request_id, вернём уже созданную сессию.
    """
    repo = SimpleSessionsPlaybackRepository()
    locks = SessionsLockManager(pool_size=64)
    service = SessionPlaybackServiceImpl(repo, locks)

    req1 = PlayRequest(user_id=1, title_id=100, client_request_id="same-id")
    req2 = PlayRequest(
        user_id=999, title_id=777, client_request_id="same-id"
    )  # другой payload

    s1 = await service.start_session(req1)
    s2 = await service.start_session(req2)

    assert s1.id == s2.id
    # и при этом данные останутся от первой сессии (как создали изначально)
    assert s2.user_id == 1
    assert s2.title_id == 100


@pytest.mark.asyncio
async def test_repository_contains_only_one_entry_after_retries():
    repo = SimpleSessionsPlaybackRepository()
    locks = SessionsLockManager(pool_size=64)
    service = SessionPlaybackServiceImpl(repo, locks)

    request = PlayRequest(user_id=3, title_id=300, client_request_id="req-3-300")

    await asyncio.gather(*(service.start_session(request) for _ in range(20)))

    all_sessions = await repo.get_all_sessions()
    assert len(all_sessions) == 1
    assert "req-3-300" in all_sessions


@pytest.mark.asyncio
async def test_many_users_many_requests_no_collisions_in_correctness():
    """
    Даже если lock pool даёт коллизии, корректность не должна ломаться:
    каждый request_id создаёт ровно одну сессию.
    """
    repo = SimpleSessionsPlaybackRepository()
    locks = SessionsLockManager(
        pool_size=8
    )  # маленький pool, чтобы коллизий было много
    service = SessionPlaybackServiceImpl(repo, locks)

    requests = [
        PlayRequest(user_id=i, title_id=100 + i, client_request_id=f"req-{i}")
        for i in range(50)
    ]

    res = await asyncio.gather(*(service.start_session(r) for r in requests))

    assert len({s.client_request_id for s in res}) == 50
    assert len({s.id for s in res}) == 50

    all_sessions = await repo.get_all_sessions()
    assert len(all_sessions) == 50


@pytest.mark.asyncio
async def test_mixed_same_and_unique_request_ids():
    repo = SimpleSessionsPlaybackRepository()
    locks = SessionsLockManager(pool_size=16)
    service = SessionPlaybackServiceImpl(repo, locks)

    same = PlayRequest(user_id=1, title_id=100, client_request_id="dup")
    uniques = [
        PlayRequest(user_id=i, title_id=100, client_request_id=f"u-{i}")
        for i in range(10)
    ]

    coros = [service.start_session(same) for _ in range(10)] + [
        service.start_session(r) for r in uniques
    ]

    res = await asyncio.gather(*coros)

    # для "dup" должна быть одна сессия
    dup_sessions = [s for s in res if s.client_request_id == "dup"]
    assert len({s.id for s in dup_sessions}) == 1

    # уникальные request_id — уникальные сессии
    unique_sessions = [s for s in res if s.client_request_id != "dup"]
    assert len({s.client_request_id for s in unique_sessions}) == 10
    assert len({s.id for s in unique_sessions}) == 10
