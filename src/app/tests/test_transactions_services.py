import pytest
from uuid import uuid4
from app.persistence.users.users import User
from app.services.transactions_service import get_receiver_by_username
from fastapi import HTTPException
from unittest.mock import AsyncMock, MagicMock

@pytest.mark.asyncio
async def test_get_receiver_by_username_found():
    fake_user = User(id=uuid4(), username="user_userov")

    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=fake_user)

    mock_db = MagicMock()
    mock_db.execute = AsyncMock(return_value=mock_result)

    result = await get_receiver_by_username(mock_db, "user_userov")

    assert result == fake_user
    mock_db.execute.assert_awaited_once()
