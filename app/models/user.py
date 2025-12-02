from datetime import datetime
from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    name: str
    last_name: str
    phone_number: str | None = None
    adresse: str | None = None
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    creation_date: datetime
    is_active: bool = True

    class Config:
        from_attributes = True