from sqlalchemy import Column, Integer, String, ForeignKey, Date, BigInteger
from sqlalchemy.orm import relationship
from app.database import Base

class UserORM(Base):
    __tablename__ = "user_"  # Respect strict de votre SQL
    
    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(50))
    last_name = Column(String(50))
    phone_number = Column(BigInteger)
    adresse = Column(String(50))
    email = Column(String(50), unique=True, index=True)
    creation_date = Column(Date)

    accounts = relationship("AccountORM", back_populates="owner")

class AccountORM(Base):
    __tablename__ = "account"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(50))
    IBAN = Column(String(34))
    # Mapping de votre colonne SQL 'id_1' vers l'attribut python 'user_id'
    user_id = Column("id_1", String(50), ForeignKey("user_.id"))

    owner = relationship("UserORM", back_populates="accounts")
    entries = relationship("TransactionEntryORM", back_populates="account")

class TransactionORM(Base):
    __tablename__ = "Transaction"

    id_transaction = Column(Integer, primary_key=True, index=True)
    type = Column(String(50))
    amount = Column(BigInteger)
    date_ = Column(Date)
    description = Column("Description", String(500))

    entries = relationship("TransactionEntryORM", back_populates="transaction")

class TransactionEntryORM(Base):
    __tablename__ = "transaction_entries"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Integer)
    type = Column(String(100))
    description = Column(String(500))
    
    transaction_id = Column("id_transaction", Integer, ForeignKey("Transaction.id_transaction"))
    account_id = Column("id_1", Integer, ForeignKey("account.id"))

    transaction = relationship("TransactionORM", back_populates="entries")
    account = relationship("AccountORM", back_populates="entries")