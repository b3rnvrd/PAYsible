from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from pydantic import BaseModel, field_validator
from typing import Optional
import re

# --- 1. Modèle DB (SQLAlchemy) ---
class BeneficiaryDB(Base):
    __tablename__ = "beneficiaries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    iban = Column(String)
    
    account_id = Column(Integer, ForeignKey("accounts.id"))
    account = relationship("AccountDB", back_populates="beneficiaries")

# --- 2. Schémas Pydantic (API) ---

# Fonction de validation réutilisable
def validate_french_iban(v: str | None) -> str | None:
    if v is None:
        return v
        
    # 1. Nettoyage : on enlève les espaces et on met en majuscules
    clean_iban = v.replace(" ", "").upper()
    
    # 2. Vérification Regex : Commence par FR suivi de 25 chiffres
    # (Total = 27 caractères pour un IBAN français)
    if not re.match(r"^FR\d{25}$", clean_iban):
        raise ValueError("L'IBAN doit être un IBAN français valide (FR + 25 chiffres).")
    
    return clean_iban

class BeneficiaryBase(BaseModel):
    name: str
    iban: str

    @field_validator('iban')
    @classmethod
    def check_iban(cls, v):
        return validate_french_iban(v)

class BeneficiaryCreate(BeneficiaryBase):
    # On retire account_id ici car le Frontend ne l'envoie pas
    pass 

class BeneficiaryUpdate(BaseModel):
    name: Optional[str] = None
    iban: Optional[str] = None

    @field_validator('iban')
    @classmethod
    def check_iban(cls, v):
        return validate_french_iban(v)

class BeneficiaryResponse(BeneficiaryBase):
    id: int
    account_id: int 
    
    class Config:
        from_attributes = True