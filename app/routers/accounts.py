from .. import models, schemas, utils
from fastapi import APIRouter,  status, HTTPException, Depends
from ..database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from typing import List
from ..oauth2 import restrict_access_to, get_current_user
from datetime import datetime, date

router = APIRouter(
    prefix="/api/accounts", tags=["Accounts"]
)


@router.get("", response_model=List[schemas.Account])
async def getAllAccounts(
    limit: int = 30, page: int = 1,
    db: Session = Depends(get_db), user=Depends(restrict_access_to("admin"))
):
    accounts = db.query(models.Account).limit(
        limit).offset((page - 1) * limit).all()
    return accounts


@router.post("", response_model=schemas.Account)
async def createAccount(
    accountData: schemas.AccountCreate,
    db: Session = Depends(get_db), user=Depends(get_current_user)
):
    if user.clearance.lower() != 'admin':
        if len(user.accounts):
            raise HTTPException(
                status_code=403,
                detail='To have more than one Account please make a request to the admins'
            )
    new_account = models.Account(**accountData.dict())
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    return new_account


@router.get("/{account_no}", response_model=schemas.Account)
async def getAccount(account_no: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    data = db.query(models.Account).where(
        models.Account.account_no == account_no).first()
    if not data:
        raise HTTPException(
            status_code=404, detail=f"Account with account_no={account_no} is not found!")
    return data


@router.post("/{account_no}/deposit")
async def deposit(
        account_no: str, data: schemas.DepsWith, user=Depends(get_current_user), db: Session = Depends(get_db)):
    Account = models.Account
    account = utils.validateTransaction(
        account_no, data, user, "deposit", True)
    account.account_balance = float(account.account_balance) + data.amount
    db.query(Account).where(
        Account.account_no == account_no
    ).update({"account_balance": account.account_balance})
    history = models.Transaction(
        account_no=account_no, transaction_type="Cr",
        transaction_amount=data.amount, transaction_desc="Deposited By Me",
        transaction_status='successfull'
    )
    db.add(history)
    db.commit()
    db.refresh(history)
    return {"message": "Amount Deposited Successfully", "new_balance": account.account_balance,  "transaction": history}


@router.post("/{account_no}/withdraw")
async def withdraw(
        account_no: str, data: schemas.DepsWith, user=Depends(get_current_user), db: Session = Depends(get_db)):
    Account = models.Account
    account = utils.validateTransaction(
        account_no, data, user, "withdraw")
    account.account_balance = float(account.account_balance) - data.amount
    db.query(Account).where(
        Account.account_no == account_no
    ).update({"account_balance": account.account_balance})
    history = models.Transaction(
        account_no=account_no, transaction_type="Dr",
        transaction_amount=data.amount, transaction_desc="withdrawed By Me via bank",
        transaction_status='successfull'
    )
    db.add(history)
    db.commit()
    db.refresh(history)
    return {"message": "Amount Withdrawn Successfully", "new_balance": account.account_balance, "transaction": history}


@router.post("/{account_no}/transfer")
async def transfer(
    account_no: str, data: schemas.TransferData,
    user=Depends(get_current_user), db: Session = Depends(get_db)
):
    if account_no == data.account_to:
        raise HTTPException(
            status_code=400, detail="Invalid transfer arguments!"
        )
    Account = models.Account
    account = utils.validateTransaction(account_no, data, user, "transfer")
    from_qry = db.query(Account).where(Account.account_no == account_no)
    to_qry = db.query(Account).where(Account.account_no == data.account_to)
    account_to = to_qry.first()
    if not account_to:
        raise HTTPException(
            status_code=404,
            detail=f"Account with account_no: {account_no} is does not exist"
        )
    from_bal = float(account.account_balance) - data.amount
    to_bal = float(account_to.account_balance) + data.amount
    from_qry.update({"account_balance": from_bal})
    to_qry.update({"account_balance": to_bal})
    h1 = models.Transaction(
        account_no=account_no, transaction_type="Dr",
        transaction_amount=data.amount, transaction_desc=data.transaction_desc or f"Transferred to {account_to.account_name}",
        transaction_status='successfull', account_involved=data.account_to
    )
    db.add(h1)
    db.add(models.Transaction(
        account_no=data.account_to, transaction_type="Cr",
        transaction_amount=data.amount, transaction_desc=data.transaction_desc or f"Transfer from {account.account_name}",
        transaction_status='successfull', account_involved=account_no)
    )
    db.commit()
    db.refresh(h1)
    return {"message": "Transfer Successfull", "new_balance": from_bal, "transaction": h1}


@router.get("/{account_no}/transactions",  response_model=List[schemas.Transaction])
async def getAccountTransactions(
    account_no: str, limit: int = 30, page: int = 1, from_d: date = None, to_d: date = None,
    user=Depends(get_current_user), db: Session = Depends(get_db)
):
    if not user.getAccount(account_no):
        raise HTTPException(
            status_code=404,
            detail=f"Account with account_no: {account_no} is not found in your accounts"
        )
    transactions = db.query(models.Transaction).where(
        models.Transaction.account_no == account_no)
    if from_d and to_d:
        transactions = transactions.filter(
            models.Transaction.transaction_date.between(from_d, to_d))
    transactions = transactions.order_by(text("transaction_date DESC"))
    transactions = transactions.limit(limit).offset(
        (page - 1) * limit)
    return transactions.all()


# Only admin can access this route
@ router.get("/types/summary")
async def getAccountTypesSummary(db: Session = Depends(get_db), user=Depends(restrict_access_to("admin"))):
    summary = db.query(
        models.Account.account_type, func.count(
            models.Account.account_no).label("no_of_accounts"),
        func.sum(models.Account.account_balance).label("total_balance")
    ).group_by(models.Account.account_type).all()
    return summary
