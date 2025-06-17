from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.persistence.db import get_session
from app.services.utils.token_functions import get_current_user
from app.persistence.db import get_session
from app.schemas.balance import BalanceCreate, BalanceResponse
from app.services.balances_service import _create_balance,get_balances_by_user_id
from app.schemas.user import UserResponse
from typing import Annotated,List
from app.api.exceptions import BalanceNotFound

router = APIRouter(prefix="/balances", tags=["balances"])

@router.post("/", response_model=BalanceResponse)
async def create_balance_endpoint(
    user_id: UUID,
    currency_id: UUID,
    balance_in: BalanceCreate,
    db: AsyncSession = Depends(get_session)
):
    return await _create_balance(db, user_id, currency_id, balance_in)

@router.get("/me/",response_model = List[BalanceResponse])
async def get_user_balances(current_user:Annotated[UserResponse,Depends(get_current_user)],
                            session:AsyncSession=Depends(get_session))->List[BalanceResponse]:
    balances = await get_balances_by_user_id(session=session,current_user=current_user)
    if not isinstance(balances,List):
        raise BalanceNotFound
    return balances