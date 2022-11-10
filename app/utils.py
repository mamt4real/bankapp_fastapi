from passlib.context import CryptContext
from fastapi import HTTPException

# password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash(password: str):
    return pwd_context.hash(password)


def verify(plain_pass: str, hashed_pass: str):
    return pwd_context.verify(plain_pass, hashed_pass)


def generateCvv():
    return randint(100, 999)


def validateTransaction(account_no, data, user, message="", isDeposit=False):
    if data.amount < 0:
        raise HTTPException(
            status_code=400,
            detail=f"You can't {message} a negative value"
        )
    account = user.getAccount(account_no)
    if not account:
        raise HTTPException(
            status_code=404,
            detail=f"Account with account_no: {account_no} is not found in your accounts"
        )
    if data.amount > account.account_balance and not isDeposit:
        raise HTTPException(
            status_code=400,
            detail="Insufficient Amount!"
        )
    return account


def currencyFormat(value):
    return "₦{:,.2f}".format(value)


def typeFormat(value):
    types = {
        "dr": "DEBIT", "cr": "CREDIT"
    }
    if value.lower() in types:
        return types[value.lower()]
    return value


def totalAmount(transactions: list):
    total = 0
    for tran in transactions:
        total += tran.transaction_amount
    return total


def cleanNulls(data: dict):
    for x in tuple(data.keys()):
        if data[x] is None:
            del data[x]
    return data
