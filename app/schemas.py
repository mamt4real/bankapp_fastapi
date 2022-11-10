from datetime import datetime
from pydantic import BaseModel, EmailStr, conint
from typing import Optional, List


class CardCreate(BaseModel):
    card_pin: int
    account_no: str


class Card(BaseModel):
    card_no: str
    card_cvv: str
    issued_date: datetime
    expiry_date: datetime

    class Config:
        orm_mode = True


class AccountCreate(BaseModel):
    account_name: str
    account_type: str
    customer_id: int


class Account(AccountCreate):
    account_no: str
    account_balance: Optional[float] = 0.0
    cards: List[Card]

    class Config:
        orm_mode = True


class CustomerCreate(BaseModel):
    customer_name: str
    customer_email: EmailStr
    customer_bvn: str
    password: str
    customer_address: Optional[str]
    customer_phone: Optional[str]


class CustomerUpdate(BaseModel):
    customer_bvn: Optional[str]
    customer_address: Optional[str]
    customer_phone: Optional[str]


class Customer(BaseModel):
    customer_id: int
    customer_name: str
    customer_email: EmailStr
    customer_bvn: str
    created_at: datetime
    customer_address: Optional[str]
    customer_phone: Optional[str]
    accounts: List[Account]

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str
    message: Optional[str]


class TokenData(BaseModel):
    id: Optional[str] = None


class TransactionCreate(BaseModel):
    account_no: str
    transaction_type: str
    transaction_amount: float
    transaction_desc: Optional[str]
    acount_involved: Optional[str]


class Transaction(TransactionCreate):
    transaction_id: int
    transaction_status: str
    transaction_date: datetime

    class Config:
        orm_mode = True


class DepsWith(BaseModel):
    amount: float


class TransferData(DepsWith):
    account_to: str
    transaction_desc: Optional[str]


class PasswordUpdate(BaseModel):
    oldpass: str
    password: str
    confirmpass: str
