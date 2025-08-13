from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from config.database import get_db
from services.stock_service import StockService
from schemas.schemas import S_Create, S_Response, Top_S_Info

router = APIRouter(prefix="/stocks", tags=["stocks"])

@router.post("/", response_model=dict, summary="주식 생성")
def create_stock(stock: S_Create, db: Session = Depends(get_db)):
    new_stock = StockService.create_stock(stock, db)
    return {"message": "주식 생성 완료", "j_id": new_stock.j_id}

@router.get("/top", response_model=List[Top_S_Info], summary="가장 많이 보유한 주식 TOP N")
def get_top_stocks(limit: int = 3, db: Session = Depends(get_db)):
    results = StockService.get_top_stocks(limit, db)
    
    return [
        Top_S_Info(
            name=result.name,
            total_quantity=result.total_quantity
        )
        for result in results
    ]

@router.get("/", response_model=List[S_Response], summary="모든 주식 조회")
def get_all_stocks(db: Session = Depends(get_db)):
    stocks = StockService.get_all_stocks(db)
    return stocks

@router.get("/{j_id}", response_model=S_Response, summary="특정 주식 조회")
def get_stock(j_id: int, db: Session = Depends(get_db)):
    stock = StockService.get_stock_by_id(j_id, db)
    if not stock:
        raise HTTPException(status_code=404, detail="주식을 찾을 수 없습니다")
    return stock