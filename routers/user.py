from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from config.database import get_db
from services.user_service import UserService
from schemas.schemas import U_Create, U_Response, U_ProfInfo, S_Info

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=dict, summary="사용자 생성")
def create_user(user: U_Create, db: Session = Depends(get_db)):
    new_user = UserService.create_user(user, db)
    return {"message": "사용자 생성 완료", "user_id": new_user.user_id}

@router.get("/{user_id}/profit", response_model=float, summary="주식 판매 시 예상 수익")
def get_user_profit_if_sold(user_id: int, db: Session = Depends(get_db)):
    return UserService.get_user_profit_if_sold(user_id, db)

@router.get("/{user_id}/stocks", response_model=List[S_Info], summary="특정 사용자의 보유 주식 목록")
def get_user_stocks(user_id: int, db: Session = Depends(get_db)):
    results = UserService.get_user_stocks(user_id, db)
    
    return [
        S_Info(
            name=result.name,
            quantity=result.quantity,
            bought_price=float(result.bought_price),
            current_price=float(result.current_price),
            profit_loss=float(result.profit_loss)
        )
        for result in results
    ]

@router.get("/profit/all", response_model=List[U_ProfInfo], summary="모든 사용자의 예상 수익")
def get_all_users_profit(db: Session = Depends(get_db)):
    results = UserService.get_all_users_profit(db)
    
    return [
        U_ProfInfo(
            user_id=result.user_id,
            username=result.username,
            profit_if_sold=float(result.profit_if_sold or 0)
        )
        for result in results
    ]