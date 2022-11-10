from .. import models, schemas, utils
from fastapi import APIRouter,  status, HTTPException, Depends
from ..database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from typing import List, Optional
from ..oauth2 import restrict_access_to, get_current_user
from datetime import datetime, date
from app.routers import handlers

router = APIRouter(
    prefix="/api/transactions", tags=["Transactions"]
)


@router.get("")
async def getAccountTransactions(
    user=Depends(restrict_access_to("admin")), db: Session = Depends(get_db),
    limit: int = 30, page: int = 1, from_d: date = None, to_d: date = None
):
    transactions = db.query(models.Transaction)
    if from_d and to_d:
        transactions = transactions.filter(
            models.Transaction.transaction_date.between(from_d, to_d))
    transactions = transactions.order_by(text("transaction_date DESC"))
    transactions = transactions.limit(limit).offset(
        (page - 1) * limit)
    return transactions.all()
