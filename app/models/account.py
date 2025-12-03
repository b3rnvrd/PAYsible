from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from pydantic import BaseModel

# --- 1. Modèle DB (SQLAlchemy) ---
class AccountDB(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)  # Ex: Courant, Epargne
    iban = Column(String, unique=True, index=True)
    
    # Clé étrangère vers User
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Relations
    owner = relationship("UserDB", back_populates="accounts")
    beneficiaries = relationship("BeneficiaryDB", back_populates="account")
    # Pour les transactions
    transaction_entries = relationship("TransactionEntryDB", back_populates="account")

# --- 2. Schémas Pydantic (API) ---
class AccountBase(BaseModel):
    type: str
    iban: str

class AccountCreate(AccountBase):
    user_id: int

class AccountResponse(AccountBase):
    id: int
    user_id: int
    # balance: float = 0.0 # On pourra le calculer plus tard
    
    class Config:
        from_attributes = True