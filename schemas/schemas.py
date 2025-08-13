from pydantic import BaseModel
from typing import List, Optional

class U_Create(BaseModel):
    id: str
    password: str
    initial_money: Optional[float] = 10000.0

class U_Response(BaseModel):
    user_id: int
    id: str
    
    class Config:
        from_attributes = True

class S_Create(BaseModel):
    name: str
    explanation: Optional[str] = None
    price: float

class S_Response(BaseModel):
    j_id: int
    name: str
    explanation: Optional[str]
    price: float
    
    class Config:
        from_attributes = True

class S_Info(BaseModel):
    name: str
    quantity: int
    bought_price: float
    current_price: float
    profit_loss: float

class U_ProfInfo(BaseModel):
    user_id: int
    username: str
    profit_if_sold: float

class Top_S_Info(BaseModel):
    name: str
    total_quantity: int

class Buy_S_Request(BaseModel):
    j_id: int
    quantity: int