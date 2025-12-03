from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from pydantic import BaseModel
from typing import Optional

# --- 1. Modèle DB (SQLAlchemy) ---
class BeneficiaryDB(Base):
    __tablename__ = "beneficiaries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    iban = Column(String)
    
    account_id = Column(Integer, ForeignKey("accounts.id"))
    account = relationship("AccountDB", back_populates="beneficiaries")

# --- 2. Schémas Pydantic (API) ---

class BeneficiaryBase(BaseModel):
    name: str
    iban: str

class BeneficiaryCreate(BeneficiaryBase):
    # On retire account_id ici car le Frontend ne l'envoie pas
    pass 

class BeneficiaryUpdate(BaseModel):
    name: Optional[str] = None
    iban: Optional[str] = None

class BeneficiaryResponse(BeneficiaryBase):
    id: int
    account_id: int 
    
    class Config:
        from_attributes = True