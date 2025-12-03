from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
from pydantic import BaseModel
from typing import List, Optional

# --- 1. Modèle DB (SQLAlchemy) ---
class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    last_name = Column(String)
    phone_number = Column(String)
    address = Column(String)
    email = Column(String, unique=True, index=True)
    creation_date = Column(DateTime, default=datetime.utcnow)

    # Relation avec Account
    accounts = relationship("AccountDB", back_populates="owner")

# --- 2. Schémas Pydantic (API) ---
class UserBase(BaseModel):
    name: str
    last_name: str
    email: str

class UserCreate(UserBase):
    phone_number: str
    address: str

class UserResponse(UserBase):
    id: int
    creation_date: datetime
    class Config:
        from_attributes = True