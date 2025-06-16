import pytest
from uuid import uuid4, UUID
from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

import app.services.cards_service as cs

# A simple Query stub to swallow .where() and .options()
class QueryStub:
    def options(self, *args, **kwargs):
        return self
    def where(self, *args, **kwargs):
        return self

# Field stub to support .in_(), .is_(), and equality for where clauses
class FieldStub:
    def __eq__(self, other):
        return True
    def in_(self, vals):
        return True
    def is_(self, val):
        return True

# Load stub to support selectinload chaining
class LoadStub:
    def selectinload(self, *args, **kwargs):
        return self

# A fake Card model
class FakeCard:
    # class-level field stubs
    id = FieldStub()
    balance_id = FieldStub()
    is_deleted = FieldStub()
    card_number = None
    expiration_date = None

    def __init__(self, balance_id, card_number, expiration_date, cardholder_name, cvv):
        self.id = uuid4()
        self.balance_id = balance_id
        self.card_number = card_number
        self.expiration_date = expiration_date
        self.cardholder_name = cardholder_name
        self.cvv = cvv
        self.is_deleted = False

# Fake AsyncClient for httpx
class FakeAsyncClient:
    def __init__(self):
        self.post = AsyncMock()
    async def __aenter__(self): return self
    async def __aexit__(self, exc_type, exc, tb): pass

@pytest.fixture(autouse=True)
def patch_card_module(monkeypatch):
    # Patch Card model and select/selectinload
    monkeypatch.setattr(cs, 'Card', FakeCard)
    monkeypatch.setattr(cs, 'select', lambda *args, **kwargs: QueryStub())
    monkeypatch.setattr(cs, 'selectinload', lambda *args, **kwargs: LoadStub())
    # Patch dependencies
    monkeypatch.setattr(cs, '_get_balance_id_by_user_id_and_currency_code', AsyncMock())
    monkeypatch.setattr(cs, 'get_currency_id_by_code', AsyncMock())
    monkeypatch.setattr(cs, '_create_balance', AsyncMock())
    monkeypatch.setattr(cs, '_get_balance_ids_by_user_id', AsyncMock())
    monkeypatch.setattr(cs, 'update_user_balance', AsyncMock())
    # Patch CardResponse.create
    monkeypatch.setattr(cs, 'CardResponse', SimpleNamespace(create=Mock()))
    # Patch httpx AsyncClient
    monkeypatch.setattr(cs.httpx, 'AsyncClient', FakeAsyncClient)

@pytest.mark.asyncio
async def test_create_card_existing_balance():
    db = SimpleNamespace(add=Mock(), flush=AsyncMock(), refresh=AsyncMock(), commit=AsyncMock(), rollback=AsyncMock())
    user_id = uuid4()
    # balance exists
    cs._get_balance_id_by_user_id_and_currency_code.return_value = uuid4()
    cs.get_currency_id_by_code.return_value = uuid4()
    card_in = SimpleNamespace(
        card_number='1234', expiration_date=datetime(2030,1,1), 
        cardholder_name='John Doe', cvv='999', currency_code=SimpleNamespace(value='usd')
    )

    # call
    await cs.create_card(db, user_id, card_in)

    # should add card and commit
    db.add.assert_called_once()
    db.flush.assert_awaited_once()
    db.refresh.assert_awaited_once()
    db.commit.assert_awaited_once()
    cs.CardResponse.create.assert_called_once()

@pytest.mark.asyncio
async def test_create_card_no_currency():
    db = SimpleNamespace()
    user_id = uuid4()
    # currency missing
    cs._get_balance_id_by_user_id_and_currency_code.return_value = None
    cs.get_currency_id_by_code.return_value = None

    card_in = SimpleNamespace(currency_code=SimpleNamespace(value='xxx'), card_number='n', expiration_date=datetime(2025,1,1), cardholder_name='', cvv='')
    with pytest.raises(HTTPException) as exc:
        await cs.create_card(db, user_id, card_in)
    assert exc.value.status_code == 404

@pytest.mark.asyncio
async def test_create_card_creates_balance_then_card():
    db = SimpleNamespace(add=Mock(), flush=AsyncMock(), refresh=AsyncMock(), commit=AsyncMock(), rollback=AsyncMock())
    user_id = uuid4()
    # no existing balance, currency found
    cs._get_balance_id_by_user_id_and_currency_code.return_value = None
    new_bal = SimpleNamespace(id=uuid4())
    cs._create_balance.return_value = new_bal
    cs.get_currency_id_by_code.return_value = uuid4()

    card_in = SimpleNamespace(card_number='5555', expiration_date=datetime(2028,5,5), cardholder_name='Jane', cvv='123', currency_code=SimpleNamespace(value='eur'))
    await cs.create_card(db, user_id, card_in)

    # should have created balance then card
    cs._create_balance.assert_awaited_once()
    db.add.assert_called()
    db.commit.assert_awaited_once()

@pytest.mark.asyncio
async def test_create_card_duplicate_raises():
    db = SimpleNamespace(add=Mock(), flush=AsyncMock(side_effect=IntegrityError('d', None, None)), refresh=AsyncMock(), commit=AsyncMock(), rollback=AsyncMock())
    user_id = uuid4()
    cs._get_balance_id_by_user_id_and_currency_code.return_value = uuid4()
    cs.get_currency_id_by_code.return_value = uuid4()

    card_in = SimpleNamespace(card_number='0000', expiration_date=datetime(2027,7,7), cardholder_name='Z', cvv='321', currency_code=SimpleNamespace(value='gbp'))
    with pytest.raises(cs.CardAlreadyExists):
        await cs.create_card(db, user_id, card_in)

@pytest.mark.asyncio
async def test_delete_card_success():
    db = SimpleNamespace(execute=AsyncMock(), commit=AsyncMock())
    user_id, card_id = uuid4(), uuid4()
    cs._get_balance_ids_by_user_id.return_value = [uuid4()]
    fake_card = FakeCard(user_id, '1', datetime(2025,1,1), 'n', 'c')
    fake_card.is_deleted = False
    db.execute.return_value = SimpleNamespace(scalar_one=Mock(return_value=fake_card))

    res = await cs.delete_card(db, user_id, card_id)
    assert fake_card.is_deleted is True
    db.commit.assert_awaited_once()
    assert isinstance(res, cs.CardDeleted)

@pytest.mark.asyncio
async def test_read_cards_success_and_no_cards():
    db = SimpleNamespace(execute=AsyncMock())
    user_id = uuid4()
    cs._get_balance_ids_by_user_id.return_value = [uuid4(), uuid4()]
    c1 = FakeCard(user_id, '1', datetime(2025,1,1), 'A', 'x')
    c2 = FakeCard(user_id, '2', datetime(2026,1,1), 'B', 'y')
    # first for success
    db.execute.return_value = SimpleNamespace(scalars=Mock(return_value=SimpleNamespace(all=Mock(return_value=[c1, c2]))))
    cs.CardResponse.create.reset_mock()

    got = await cs.read_cards(db, user_id)
    assert cs.CardResponse.create.call_count == 2
    # then for no cards
    db.execute.return_value = SimpleNamespace(scalars=Mock(return_value=SimpleNamespace(all=Mock(return_value=[]))))
    with pytest.raises(cs.NoCards):
        await cs.read_cards(db, user_id)

@pytest.mark.asyncio
async def test_card_belongs_and_is_not():
    db = SimpleNamespace(execute=AsyncMock())
    user_id, card_id = uuid4(), uuid4()
    cs._get_balance_ids_by_user_id.return_value = [uuid4()]
    db.execute.return_value = SimpleNamespace(scalar_one_or_none=Mock(return_value=FakeCard(user_id, '1', datetime(2025,1,1), 'A', 'x')))
    assert await cs._card_belongs_to_user(db, user_id, card_id) is True
    db.execute.return_value = SimpleNamespace(scalar_one_or_none=Mock(return_value=None))
    assert await cs._card_belongs_to_user(db, user_id, card_id) is False


@pytest.mark.asyncio
async def test_load_balance_from_card(monkeypatch):
    db = SimpleNamespace()
    user_id = uuid4()
    fake_resp = SimpleNamespace(status_code=200, json=Mock(return_value=True))
    client = FakeAsyncClient()
    client.post.return_value = fake_resp
    monkeypatch.setattr(cs.httpx, 'AsyncClient', lambda: client)
    cs.update_user_balance.return_value = AsyncMock()
    ok = await cs.load_balance_from_card(db, user_id, 'cardn', '12.34', 'usd')
    assert ok is True
    fake_resp.status_code = 500
    assert await cs.load_balance_from_card(db, user_id, 'cardn', '1', 'usd') is False
    fake_resp.status_code = 200
    fake_resp.json.return_value = False
    assert await cs.load_balance_from_card(db, user_id, 'cardn', '1', 'usd') is False

