from pydantic import BaseModel

class AccountBase(BaseModel):
    type: str

class AccountCreate(AccountBase):
    user_id: int
    type: str

class Account(AccountBase):
    id: int
    user_id: int
    IBAN: str
    balance: float = 0.0

    class Config:
        from_attributes = True