from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.utils.token_functions import get_current_user
from app.persistence.db import get_session
from app.schemas.transaction import TransactionCreate, TransactionResponse
from app.services.transactions_service import *

router = APIRouter(prefix="/transactions", tags=["transactions"])

@router.post("/transactions/user-to-user", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def user_to_user_transaction(
    transaction_data: TransactionCreate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_session) 
):
    transaction = await create_user_to_user_transaction(db, current_user.id, transaction_data)
    return transaction

@router.patch("/recurring_transactions/{transaction_id}/deactivate")
async def deactivate_recurring(transaction_id: UUID, db: AsyncSession = Depends(get_session)):
    transaction = await deactivate_recurring_transaction(db, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return "Recurring transaction deactivated!"
