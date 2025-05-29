from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.persistence.db import get_session

from app.persistence.balances.balance import Balance
from app.schemas.balance import BalanceCreate, BalanceResponse
from app.services.balances_service import *

router = APIRouter(prefix="/balances", tags=["balances"])

@router.post("/", response_model=BalanceResponse)
async def create_balance_endpoint(
    user_id: UUID,
    currency_id: UUID,
    balance_in: BalanceCreate,
    db: AsyncSession = Depends(get_session)
):
    return await create_balance(db, user_id, currency_id, balance_in)