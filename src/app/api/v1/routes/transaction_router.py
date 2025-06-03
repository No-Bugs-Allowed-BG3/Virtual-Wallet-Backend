from uuid import UUID
from fastapi import APIRouter, Depends, status, Query
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

@router.post("/transactions/{transaction_id}/accept")
async def accept_transaction_endpoint(transaction_id: UUID, db: AsyncSession = Depends(get_session), current_user = Depends(get_current_user)):
    accepted_transaction = await accept_transaction(db, transaction_id)
    if not accepted_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    if current_user.id not in (accepted_transaction.sender_id, accepted_transaction.receiver_id):
        raise HTTPException(status_code=403, detail="Not authorized to accept this transaction")

    return {"message": "Transaction Accepted!"}

@router.get("/all_transactions")
async def get_all_transactions(
    db: AsyncSession = Depends(get_session),
    skip: int = Query(0, ge=0),
    limit: int = Query(5, ge=1, le=100)
):
    all_transactions = await view_all_transactions(db, skip=skip, limit=limit)
    if not all_transactions["transactions"]:
        raise HTTPException(status_code=404, detail="No available transactions")
    return all_transactions

@router.get("/all_recurring_transactions")
async def get_all_recurring_transactions(db: AsyncSession = Depends(get_session),
                                         skip: int = Query(0, ge=0),
                                         limit: int = Query(5, ge=1, le=100)):
    all_recurring_transactions = await view_all_recurring_transactions(db, skip=skip, limit=limit)
    if not all_recurring_transactions["recurring_transactions"]:
        raise HTTPException(status_code=404, detail="No available recurring transacations")
    return all_recurring_transactions