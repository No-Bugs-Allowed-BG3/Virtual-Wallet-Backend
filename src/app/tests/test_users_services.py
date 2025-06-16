import pytest
from uuid import uuid4, UUID
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock
from sqlalchemy.exc import IntegrityError

from app.api.exceptions import UserNotFound
from app.services.users_service import (
    verify_user,
    _get_user_by_id,
    _get_user_id_by_username,
    _get_user_id_by_phone,
    _get_user_id_by_email,
)
from app.services.errors import ServiceError
from app.schemas.service_result import ServiceResult



@pytest.mark.asyncio
async def test__get_user_by_id_found_and_not_found():
    fake = object()
    mock_db = SimpleNamespace(
        execute=AsyncMock(
            return_value=SimpleNamespace(scalar_one_or_none=Mock(return_value=fake))
        )
    )
    # found
    got = await _get_user_by_id(mock_db, UUID(int=0))
    assert got is fake

    # not found
    mock_db.execute.return_value.scalar_one_or_none.return_value = None
    with pytest.raises(UserNotFound):
        await _get_user_by_id(mock_db, UUID(int=0))


@pytest.mark.asyncio
async def test__get_user_id_by_field_found_and_not_found():
    for fn in [_get_user_id_by_username, _get_user_id_by_phone, _get_user_id_by_email]:
        fake_id = uuid4()
        mock_db = SimpleNamespace(
            execute=AsyncMock(
                return_value=SimpleNamespace(scalar_one_or_none=Mock(return_value=fake_id))
            )
        )
        # found
        got = await fn(mock_db, "foo")
        assert got == fake_id

        # not found
        mock_db.execute.return_value.scalar_one_or_none.return_value = None
        with pytest.raises(UserNotFound):
            await fn(mock_db, "foo")

@pytest.mark.asyncio
async def test_verify_user(monkeypatch):
    # stub requests.post
    class FakeResp:
        def __bool__(self): return self._flag
        def __init__(self, flag): self._flag = flag
    monkeypatch.setenv("VERIFICATION_API_URL", "http://x")
    monkeypatch.setattr(
        "app.services.users_service.requests.post",
        lambda url, files: FakeResp(True),
    )
    # DB returns rowcount=1
    fake_session = SimpleNamespace(
        execute=AsyncMock(return_value=SimpleNamespace(rowcount=1)),
        commit=AsyncMock(),
    )
    ok = await verify_user(SimpleNamespace(id=uuid4()), b"id", b"selfie", fake_session)
    assert isinstance(ok, ServiceResult) and ok.result is True

    # verified but rowcount=0
    monkeypatch.setattr(
        "app.services.users_service.requests.post",
        lambda url, files: FakeResp(True),
    )
    fake_session.execute.return_value = SimpleNamespace(rowcount=0)
    err = await verify_user(SimpleNamespace(id=uuid4()), b"id", b"s", fake_session)
    assert err == ServiceError.ERROR_USER_NOT_FOUND

    # not verified at all
    monkeypatch.setattr(
        "app.services.users_service.requests.post",
        lambda url, files: FakeResp(False),
    )
    res = await verify_user(SimpleNamespace(id=uuid4()), b"id", b"selfie", fake_session)
    assert isinstance(res, ServiceResult) and res.result is False


