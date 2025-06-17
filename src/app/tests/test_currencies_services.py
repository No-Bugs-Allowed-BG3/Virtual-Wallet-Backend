import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock
from app.api.exceptions import CurrencyNotFound
from app.services.currencies_service import _get_currency_code_by_currency_id, get_currency_id_by_code


@pytest.mark.asyncio
async def test_get_currency_id_by_code_found():
    currency_id = uuid4()

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = currency_id

    mock_db = MagicMock()
    mock_db.execute = AsyncMock(return_value=mock_result)

    result = await get_currency_id_by_code(mock_db, "USD")
    assert result == currency_id
    mock_db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_currency_id_by_code_not_found():
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None

    mock_db = MagicMock()
    mock_db.execute = AsyncMock(return_value=mock_result)

    result = await get_currency_id_by_code(mock_db, "EUR")

    assert result is None
    mock_db.execute.assert_awaited_once()

@pytest.mark.asyncio
async def test_get_currency_code_by_currency_id_found():
    currency_id = uuid4()

    mock_scalars = MagicMock()
    mock_scalars.first.return_value = "USD"

    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars

    mock_db = MagicMock()
    mock_db.execute = AsyncMock(return_value=mock_result)

    result = await _get_currency_code_by_currency_id(mock_db, currency_id)

    assert result == "USD"
    mock_db.execute.assert_awaited_once()

@pytest.mark.asyncio
async def test_get_currency_code_by_currency_id_not_found():
    currency_id = uuid4()

    mock_scalars = MagicMock()
    mock_scalars.first.return_value = None

    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars

    mock_db = MagicMock()
    mock_db.execute = AsyncMock(return_value=mock_result)

    with pytest.raises(CurrencyNotFound):
        await _get_currency_code_by_currency_id(mock_db, currency_id)

    mock_db.execute.assert_awaited_once()