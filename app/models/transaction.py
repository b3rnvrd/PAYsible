from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
from pydantic import BaseModel
from typing import List, Optional

# --- 1. Modèles DB (SQLAlchemy) ---

class TransactionDB(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)
    amount = Column(Float)
    date = Column(DateTime, default=datetime.utcnow)
    description = Column(String)

    entries = relationship("TransactionEntryDB", back_populates="transaction")

class TransactionEntryDB(Base):
    __tablename__ = "transaction_entries"
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float)
    type = Column(String) # Debit ou Credit
    description = Column(String)
    
    account_id = Column(Integer, ForeignKey("accounts.id"))
    transaction_id = Column(Integer, ForeignKey("transactions.id"))

    account = relationship("AccountDB", back_populates="transaction_entries")
    transaction = relationship("TransactionDB", back_populates="entries")


# --- 2. Schémas Pydantic (API) ---

class TransactionBase(BaseModel):
    type: str
    amount: float
    description: str | None = None

class TransactionCreate(TransactionBase):
    # Pour créer une transaction, il faudra surement dire quel compte est débité/crédité
    account_id: int 

class TransactionResponse(TransactionBase):
    id: int
    date: datetime
    
    class Config:
        from_attributes = True