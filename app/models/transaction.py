from datetime import datetime
from pydantic import BaseModel

class TransactionBase(BaseModel):
    type: str
    amount: float
    description: str | None = None

class TransactionCreate(TransactionBase):
    pass

class Transaction(TransactionBase):
    id: int
    date: datetime

    class Config:
        from_attributes = True