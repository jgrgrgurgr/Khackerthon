from pydantic import BaseModel
from typing import List, Optional

class UsrCrt(BaseModel):
    id: str
    pwd: str
    init_money: Optional[float] = 10000.0

class UsrResp(BaseModel):
    uid: int
    id: str
    
    class Config:
        from_attributes = True

class StkCrt(BaseModel):
    name: str
    exp: Optional[str] = None
    price: float

class StkResp(BaseModel):
    jid: int
    name: str
    exp: Optional[str]
    price: float
    
    class Config:
        from_attributes = True

class StkInfo(BaseModel):
    name: str
    qty: int
    buy_price: float
    cur_price: float
    pl: float

class UsrProfitInfo(BaseModel):
    uid: int
    uname: str
    profit_sold: float

class TopStkInfo(BaseModel):
    name: str
    tot_qty: int

class BuyReq(BaseModel):
    jid: int
    qty: int