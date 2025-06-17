from datetime import datetime
from decimal import Decimal
import pytest
from uuid import uuid4
from app.persistence.balances.balance import Balance
from app.persistence.transactions.transaction import Transaction
from app.persistence.users.users import User
from app.services.transactions_service import *
from fastapi import HTTPException
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

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

@pytest.mark.asyncio
async def test_view_all_transactions_basic():
    fake_transactions = [
        Transaction(
            id=uuid4(),
            sender_id=uuid4(),
            receiver_id=uuid4(),
            currency_id=uuid4(),
            amount=Decimal("10.0"),
            status="completed",
            created_date=datetime(2023, 1, 1)
        ),
        Transaction(
            id=uuid4(),
            sender_id=uuid4(),
            receiver_id=uuid4(),
            currency_id=uuid4(),
            amount=Decimal("20.0"),
            status="completed",
            created_date=datetime(2023, 1, 2)
        ),
    ]

    total_query_mock = MagicMock()
    total_query_mock.scalar_one = MagicMock(return_value=10)

    scalars_mock = MagicMock()
    scalars_mock.all = MagicMock(return_value=fake_transactions)

    result_mock = MagicMock()
    result_mock.scalars = MagicMock(return_value=scalars_mock)

    mock_db = MagicMock(spec=AsyncSession)
    mock_db.execute = AsyncMock(side_effect=[total_query_mock, result_mock])

    response = await view_all_transactions(mock_db, skip=0, limit=2, sort_by="date", sort_order="asc")

    assert response["transactions"] == fake_transactions
    assert response["total"] == 10
    assert response["has_next"] is True
    assert response["page"] == 1
    assert response["per_page"] == 2

    assert mock_db.execute.await_count == 2

@pytest.mark.asyncio
async def test_reject_transaction_success():
    fake_transaction = Transaction(
        id=uuid4(),
        status="pending"
    )

    # Мок на резултата от select
    result_mock = MagicMock()
    result_mock.scalar_one_or_none = MagicMock(return_value=fake_transaction)

    # Мок на AsyncSession
    mock_db = MagicMock()
    mock_db.execute = AsyncMock(return_value=result_mock)
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()

    # Извикваме функцията
    transaction = await reject_transaction(mock_db, fake_transaction.id)

    assert transaction.status == "rejected"
    mock_db.commit.assert_awaited_once()
    mock_db.refresh.assert_awaited_once_with(fake_transaction)

@pytest.mark.asyncio
async def test_reject_transaction_not_found():
    result_mock = MagicMock()
    result_mock.scalar_one_or_none = MagicMock(return_value=None)

    mock_db = MagicMock()
    mock_db.execute = AsyncMock(return_value=result_mock)

    with pytest.raises(HTTPException) as exc_info:
        await reject_transaction(mock_db, uuid4())

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Transaction not found"

@pytest.mark.asyncio
async def test_reject_transaction_already_processed():
    fake_transaction = Transaction(
        id=uuid4(),
        status="completed"
    )

    result_mock = MagicMock()
    result_mock.scalar_one_or_none = MagicMock(return_value=fake_transaction)

    mock_db = MagicMock()
    mock_db.execute = AsyncMock(return_value=result_mock)

    with pytest.raises(HTTPException) as exc_info:
        await reject_transaction(mock_db, fake_transaction.id)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Transaction already processed"

@pytest.mark.asyncio
async def test_get_receiver_found():
    fake_user = User(id=uuid4(), username="testuser")

    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=fake_user)

    mock_db = MagicMock()
    mock_db.execute = AsyncMock(return_value=mock_result)

    result = await get_receiver(mock_db, fake_user.id)

    assert result == fake_user
    mock_db.execute.assert_awaited_once()

@pytest.mark.asyncio
async def test_get_receiver_not_found():
    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=None)

    mock_db = MagicMock()
    mock_db.execute = AsyncMock(return_value=mock_result)

    with pytest.raises(HTTPException) as exc_info:
        await get_receiver(mock_db, uuid4())
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "User not found"
    mock_db.execute.assert_awaited_once()

@pytest.mark.asyncio
async def test_get_user_balance_not_found():
    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value= None)

    mock_db = MagicMock()
    mock_db.execute = AsyncMock(return_value = mock_result)

    with pytest.raises(HTTPException) as exc_info:
        await get_user_balance(mock_db, uuid4(), uuid4())
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Balance not found"
        mock_db.execute.assert_awaited_once()

@pytest.mark.asyncio
async def test_get_user_balance_found():
    fake_balnce = Balance(id=uuid4())

    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=fake_balnce)

    mock_db = MagicMock()
    mock_db.execute = AsyncMock(return_value=mock_result)
    user_id = uuid4()
    currency_id = uuid4()

    result = await get_user_balance(mock_db, user_id, currency_id)

    assert result == fake_balnce
    mock_db.execute.assert_awaited_once()

@pytest.mark.asyncio
async def test_ensure_sufficient_funds_success():
    balance = Balance(amount=Decimal("100.00"))
    await ensure_sufficient_funds(balance, Decimal("50.00"))

@pytest.mark.asyncio
async def test_ensure_sufficient_funds_insufficient():
    balance = Balance(amount=Decimal("30.00"))
    with pytest.raises(HTTPException) as exc_info:
        await ensure_sufficient_funds(balance, Decimal("50.00"))
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Insufficient funds"

@pytest.mark.asyncio
@patch("app.services.transactions_service.get_user_balance")
async def test_get_or_create_receiver_balance_existing(mock_get_user_balance):
    fake_balance = Balance(user_id=uuid4(), currency_id=uuid4(), amount=Decimal("100.0"))
    mock_get_user_balance.return_value = fake_balance

    mock_db = MagicMock()
    mock_db.add = MagicMock()
    mock_db.flush = AsyncMock()

    result = await get_or_create_receiver_balance(mock_db, fake_balance.user_id, fake_balance.currency_id)

    assert result == fake_balance
    mock_get_user_balance.assert_awaited_once_with(mock_db, fake_balance.user_id, fake_balance.currency_id)
    mock_db.add.assert_not_called()
    mock_db.flush.assert_not_called()

@pytest.mark.asyncio
@patch("app.services.transactions_service.get_user_balance")
async def test_get_or_create_receiver_balance_create_new(mock_get_user_balance):
    mock_get_user_balance.side_effect = HTTPException(status_code=404, detail="Balance not found")

    user_id = uuid4()
    currency_id = uuid4()

    mock_db = MagicMock()
    mock_db.add = MagicMock()
    mock_db.flush = AsyncMock()

    result = await get_or_create_receiver_balance(mock_db, user_id, currency_id)

    assert isinstance(result, Balance)
    assert result.user_id == user_id
    assert result.currency_id == currency_id
    assert result.amount == Decimal("0.0")
    mock_db.add.assert_called_once_with(result)
    mock_db.flush.assert_awaited_once()

@pytest.mark.asyncio
@patch("app.services.transactions_service.get_user_balance")
async def test_get_or_create_receiver_balance_raises_other_error(mock_get_user_balance):
    mock_get_user_balance.side_effect = HTTPException(status_code=500, detail="Database error")

    mock_db = MagicMock()

    with pytest.raises(HTTPException) as exc_info:
        await get_or_create_receiver_balance(mock_db, uuid4(), uuid4())
    assert exc_info.value.status_code == 500