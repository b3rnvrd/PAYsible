from pydantic import BaseModel

class TransactionEntryBase(BaseModel):
    amount: float
    type: str
    description: str | None = None
    account_id: int

class TransactionEntryCreate(TransactionEntryBase):
    transaction_id: int

class TransactionEntry(TransactionEntryBase):
    id: int
    transaction_id: int

    class Config:
        from_attributes = True