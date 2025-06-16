import pytest
from uuid import uuid4, UUID
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import app.services.balances_service as bs
from app.schemas.balance import BalanceResponse, BalanceCreate
from app.api.exceptions import BalanceAlreadyExists, BalanceNotFound
from sqlalchemy.exc import IntegrityError

# A fake Balance class to stand in for the real ORM model.
class FakeBalance:
    # class-level attrs so select(Balance.id/user_id/currency_id) won't error
    id = None
    user_id = None
    currency_id = None

    def __init__(self, user_id, currency_id, amount):
        self.id = uuid4()
        self.user_id = user_id
        self.currency_id = currency_id
        self.amount = amount
        self.currency = None

@pytest.fixture(autouse=True)
def patch_balance_and_currency(monkeypatch):
    # Replace the Balance model in the service module
    monkeypatch.setattr(bs, "Balance", FakeBalance)
    # Replace currency lookup in the service module
    dummy_currency_id = uuid4()
    monkeypatch.setattr(
        bs,
        "_get_currency_id_by_currency_code",
        AsyncMock(return_value=dummy_currency_id),
    )
    # Stub out SQLAlchemy select to ignore model internals
    monkeypatch.setattr(
        bs,
        "select",
        lambda *args, **kwargs: SimpleNamespace(where=lambda *a, **k: "_ignored_"),
    )
    # Simplify BalanceResponse so it only handles id, amount, currency_code
    class DummyResp:
        def __init__(self, id, amount, currency_code):
            self.id = id
            self.amount = amount
            self.currency_code = currency_code
    monkeypatch.setattr(bs, "BalanceResponse", DummyResp)

    return dummy_currency_id

@pytest.mark.asyncio
async def test__create_balance_success(monkeypatch, patch_balance_and_currency):
    user_id = uuid4()
    currency_id = patch_balance_and_currency
    db = SimpleNamespace(
        add=Mock(),
        flush=AsyncMock(),
        refresh=AsyncMock(side_effect=lambda inst, attribute_names: setattr(inst, "currency", SimpleNamespace(code="USD"))),
        commit=AsyncMock(),
        rollback=AsyncMock(),
    )

    bal_in = BalanceCreate(amount=Decimal("123.45"))
    got = await bs._create_balance(db, user_id, currency_id, bal_in)

    assert isinstance(got, bs.BalanceResponse)
    assert got.amount == Decimal("123.45")
    assert got.currency_code == "USD"
    assert isinstance(got.id, UUID)

    db.add.assert_called_once()
    db.flush.assert_awaited_once()
    db.refresh.assert_awaited_once()
    db.commit.assert_awaited_once()
    db.rollback.assert_not_called()

@pytest.mark.asyncio
async def test__create_balance_duplicate(monkeypatch, patch_balance_and_currency):
    user_id = uuid4()
    currency_id = patch_balance_and_currency
    db = SimpleNamespace(
        add=Mock(),
        flush=AsyncMock(side_effect=IntegrityError("dup", None, None)),
        refresh=AsyncMock(),
        commit=AsyncMock(),
        rollback=AsyncMock(),
    )

    with pytest.raises(BalanceAlreadyExists):
        await bs._create_balance(db, user_id, currency_id, BalanceCreate(amount=Decimal("0")))
    db.flush.assert_awaited_once()
    db.rollback.assert_awaited_once()
    db.commit.assert_not_called()

@pytest.mark.asyncio
async def test__get_balance_ids_by_user_id_found():
    user_id = uuid4()
    ids = [uuid4(), uuid4()]
    result = SimpleNamespace(scalars=Mock(return_value=SimpleNamespace(all=Mock(return_value=ids))))
    db = SimpleNamespace(execute=AsyncMock(return_value=result))

    got = await bs._get_balance_ids_by_user_id(db, user_id)
    assert got == ids

@pytest.mark.asyncio
async def test__get_balance_ids_by_user_id_not_found():
    user_id = uuid4()
    result = SimpleNamespace(scalars=Mock(return_value=SimpleNamespace(all=Mock(return_value=[]))))
    db = SimpleNamespace(execute=AsyncMock(return_value=result))

    with pytest.raises(BalanceNotFound):
        await bs._get_balance_ids_by_user_id(db, user_id)

@pytest.mark.asyncio
async def test__get_balance_id_by_user_and_currency(monkeypatch, patch_balance_and_currency):
    user_id = uuid4()
    want_id = uuid4()
    scalar = SimpleNamespace(first=Mock(return_value=want_id))
    result = SimpleNamespace(scalars=Mock(return_value=scalar))
    db = SimpleNamespace(execute=AsyncMock(return_value=result))

    got = await bs._get_balance_id_by_user_id_and_currency_code(db, user_id, "EUR")
    assert got == want_id

@pytest.mark.asyncio
async def test__get_balance_id_by_user_and_currency_none(monkeypatch, patch_balance_and_currency):
    user_id = uuid4()
    scalar = SimpleNamespace(first=Mock(return_value=None))
    result = SimpleNamespace(scalars=Mock(return_value=scalar))
    db = SimpleNamespace(execute=AsyncMock(return_value=result))

    got = await bs._get_balance_id_by_user_id_and_currency_code(db, user_id, "EUR")
    assert got is None

@pytest.mark.asyncio
async def test_get_balance_by_user_and_currency_found(monkeypatch, patch_balance_and_currency):
    user_id = uuid4()
    fake_bal = FakeBalance(user_id, patch_balance_and_currency, Decimal("50"))
    result = SimpleNamespace(scalars=Mock(return_value=SimpleNamespace(first=Mock(return_value=fake_bal))))
    db = SimpleNamespace(execute=AsyncMock(return_value=result))

    got = await bs.get_balance_by_user_and_currency(db, user_id, "GBP")
    assert got is fake_bal

@pytest.mark.asyncio
async def test_get_balance_by_user_and_currency_not_found(monkeypatch, patch_balance_and_currency):
    user_id = uuid4()
    result = SimpleNamespace(scalars=Mock(return_value=SimpleNamespace(first=Mock(return_value=None))))
    db = SimpleNamespace(execute=AsyncMock(return_value=result))

    got = await bs.get_balance_by_user_and_currency(db, user_id, "GBP")
    assert got is None

@pytest.mark.asyncio
async def test_update_user_balance_existing(monkeypatch, patch_balance_and_currency):
    user_id = uuid4()
    existing = FakeBalance(user_id, patch_balance_and_currency, Decimal("10"))
    monkeypatch.setattr(bs, "get_balance_by_user_and_currency", AsyncMock(return_value=existing))
    db = SimpleNamespace(add=Mock(), commit=AsyncMock())

    got = await bs.update_user_balance(db, user_id, Decimal("5"), "USD")
    assert got.amount == Decimal("15")
    db.commit.assert_awaited_once()
    db.add.assert_not_called()

@pytest.mark.asyncio
async def test_update_user_balance_new(monkeypatch, patch_balance_and_currency):
    user_id = uuid4()
    monkeypatch.setattr(bs, "get_balance_by_user_and_currency", AsyncMock(return_value=None))
    db = SimpleNamespace(add=Mock(), commit=AsyncMock())

    got = await bs.update_user_balance(db, user_id, Decimal("7"), "JPY")
    assert isinstance(got, FakeBalance)
    assert got.user_id == user_id
    assert got.amount == Decimal("7")
    db.add.assert_called_once_with(got)
    db.commit.assert_awaited_once()
