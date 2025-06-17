from uuid import UUID
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.utils.token_functions import get_current_user
from app.persistence.db import get_session
from app.persistence.users.users import User
from app.schemas.transaction import TransactionCreate, TransactionResponse
from app.services.transactions_service import *

router = APIRouter(prefix="/transactions", tags=["transactions"])

@router.post("/user-to-user/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def user_to_user_transaction(
    transaction_data: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session) 
):
    transaction = await create_user_to_user_transaction(db, current_user.id, transaction_data)
    return transaction

@router.delete("/recurring/{transaction_id}")
async def deactivate_recurring(transaction_id: UUID, db: AsyncSession = Depends(get_session)):
    transaction = await deactivate_recurring_transaction(db, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return "Recurring transaction deactivated!"

@router.post("/{transaction_id}/accept")
async def accept_transaction_endpoint(transaction_id: UUID, db: AsyncSession = Depends(get_session), current_user = Depends(get_current_user)):
    accepted_transaction = await accept_transaction(db, transaction_id)
    if not accepted_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    if current_user.id not in (accepted_transaction.sender_id, accepted_transaction.receiver_id):
        raise HTTPException(status_code=403, detail="Not authorized to accept this transaction")

    return {"message": "Transaction accepted"}

@router.post("/{transaction_id}/reject")
async def reject_transaction_endpoint(transaction_id: UUID, db: AsyncSession = Depends(get_session), current_user = Depends(get_current_user)):
    rejected_transaction = await reject_transaction(db, transaction_id)
    if not reject_transaction:
        raise HTTPException(status_code=404, detail= "Transaction not found")
    
    if current_user.id not in (rejected_transaction.sender_id,rejected_transaction.receiver_id):
        raise HTTPException(status_code=403, detail="Not authorized to reject this transaction")
    
    return {"message": "Transaction rejected"}


@router.get("/")
async def get_all_transactions(
    db: AsyncSession = Depends(get_session),
    skip: int = Query(0, ge=0),
    limit: int = Query(5, ge=1, le=100),
    sort_by: str = Query("date", pattern="^(date|amount)$"),
    sort_order: str = Query("asc", pattern="^(asc|desc)$")
):
    all_transactions = await view_all_transactions(db, skip=skip, limit=limit,sort_by=sort_by, sort_order=sort_order)
    if not all_transactions["transactions"]:
        raise HTTPException(status_code=404, detail="No available transactions")
    return all_transactions

@router.get("/recurring")
async def get_all_recurring_transactions(db: AsyncSession = Depends(get_session),
                                         skip: int = Query(0, ge=0),
                                         limit: int = Query(5, ge=1, le=100)):
    all_recurring_transactions = await view_all_recurring_transactions(db, skip=skip, limit=limit)
    if not all_recurring_transactions["recurring_transactions"]:
        raise HTTPException(status_code=404, detail="No available recurring transacations")
    return all_recurring_transactions