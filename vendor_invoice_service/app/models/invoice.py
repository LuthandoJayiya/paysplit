from pydantic import BaseModel
from typing import Optional, List

class InvoiceItem(BaseModel):
    description: str
    quantity: int
    price: float

class Invoice(BaseModel):
    supplier_name: str
    total_amount: float
    items: Optional[List[InvoiceItem]] = []
    status: str = "pending"
