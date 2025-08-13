from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from config.database import get_db
from services.trading_service import TrdSvc
from schemas.schemas import BuyReq

rt = APIRouter(prefix="/trd", tags=["trd"])

@rt.post("/buy/{uid}")
def b_stk(uid: int, buy_req: BuyReq, db: Session = Depends(get_db)):
    return TrdSvc.b_stk(uid, buy_req.jid, buy_req.qty, db)