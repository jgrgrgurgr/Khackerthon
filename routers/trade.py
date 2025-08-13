from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from config.database import get_db
from services.trading_service import TradeService
from schemas.schemas import Buy_S_Request

router = APIRouter(prefix="/trading", tags=["trading"])

@router.post("/buy/{user_id}", summary="주식 매수")
def buy_stock(user_id: int, buy_request: Buy_S_Request, db: Session = Depends(get_db)):
    return TradeService.buy_stock(user_id, buy_request.j_id, buy_request.quantity, db)