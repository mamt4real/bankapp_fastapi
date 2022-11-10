from email.policy import default
from random import randint
from sqlalchemy import TIMESTAMP, Boolean, Column, ForeignKey, Integer, String, text, Sequence, CHAR, Numeric, CheckConstraint
from .database import Base
from sqlalchemy.orm import relationship
from app.utils import generateCvv


class Customer(Base):
    __tablename__ = 'customers'
    customer_id = Column(Integer, primary_key=True)
    customer_name = Column(String(150), nullable=False)
    customer_email = Column(String(150), nullable=False, unique=True)
    customer_address = Column(String(200))
    customer_phone = Column(String(20))
    customer_bvn = Column(CHAR(12), nullable=False)
    password = Column(String, nullable=False)
    clearance = Column(String(30), server_default='Customer')
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('Now()'))

    accounts = relationship("Account")

    def getAccount(self, account_no):
        for acc in self.accounts:
            if acc.account_no == account_no:
                return acc
        return None


class Account(Base):
    __tablename__ = 'accounts'
    account_no = Column(CHAR(10), Sequence(
        name='account_no_seq', start=5000000000, increment=1, minvalue=5000000000, maxvalue=5999999999), primary_key=True,  server_default=text(
        "nextval('account_no_seq'::regclass)"))
    account_name = Column(String(150), nullable=False)
    account_type = Column(String(50), nullable=False,
                          server_default=text('Savings'))
    account_balance = Column(Numeric, default=0.0, server_default="0.0")
    account_status = Column(String, server_default='active')
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('Now()'))
    customer_id = Column(Integer, ForeignKey(
        "customers.customer_id", ondelete="CASCADE"), nullable=False)
    CheckConstraint("account_balance >= 0", name="accoun_balance_check")

    cards = relationship("CreditCard")


class CreditCard(Base):
    __tablename__ = "credit_cards"
    id = Column(Integer, primary_key=True)
    card_no = Column(CHAR(16), Sequence(
        name='card_no_seq', start=5555000000000000, increment=1, minvalue=5555000000000000, maxvalue=5555999999999999), unique=True, nullable=False,
        server_default=text("nextval('card_no_seq'::regclass)"))
    card_cvv = Column(CHAR(3), nullable=False, default=generateCvv)
    card_pin = Column(CHAR(4), nullable=False)
    issued_date = Column(TIMESTAMP(timezone=True),
                         nullable=False, server_default=text('Now()'))
    expiry_date = Column(TIMESTAMP(timezone=True),
                         nullable=False, server_default=text("Now() + INTERVAL '4 years'"))
    account_no = Column(CHAR(10), ForeignKey(
        "accounts.account_no", ondelete="CASCADE"), nullable=False)


class Transaction(Base):
    __tablename__ = "transactions"
    transaction_id = Column(Integer, primary_key=True)
    transaction_type = Column(CHAR(2), nullable=False)
    transaction_amount = Column(Numeric)
    transaction_status = Column(String(20), server_default=text("successfull"))
    transaction_date = Column(TIMESTAMP(timezone=True),
                              nullable=False, server_default=text('Now()'))
    transaction_desc = Column(String(200))
    account_no = Column(CHAR(10), ForeignKey(
        "accounts.account_no", ondelete="CASCADE"), nullable=False)
    account_involved = Column(CHAR(10), ForeignKey(
        "accounts.account_no"))

    CheckConstraint("transaction_type IN ('CR', 'DR', 'Dr', 'Cr', 'cr', 'dr')",
                    name="transaction_type_check")
