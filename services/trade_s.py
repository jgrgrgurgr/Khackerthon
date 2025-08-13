from sqlalchemy.orm import Session
from models.models import User, Stock, S_Ownership, U_Wallet
from fastapi import HTTPException

class TradingService:
    @staticmethod
    def buy_stock(user_id: int, j_id: int, quantity: int, db: Session):
        # 사용자와 주식 존재 확인
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
        
        stock = db.query(Stock).filter(Stock.j_id == j_id).first()
        if not stock:
            raise HTTPException(status_code=404, detail="주식을 찾을 수 없습니다")
        
        # 지갑 확인
        wallet = db.query(U_Wallet).filter(U_Wallet.user_id == user_id).first()
        if not wallet:
            raise HTTPException(status_code=404, detail="사용자 지갑을 찾을 수 없습니다")
        
        total_cost = float(stock.price) * quantity
        if float(wallet.money) < total_cost:
            raise HTTPException(status_code=400, detail="잔액이 부족합니다")
        
        # 기존 보유 주식 확인
        ownership = db.query(S_Ownership).filter(
            S_Ownership.user_id == user_id,
            S_Ownership.j_id == j_id
        ).first()
        
        if ownership:
            # 기존 보유 주식이 있는 경우 평균 단가 계산
            total_shares = ownership.quantity + quantity
            total_value = float(ownership.price_at_time) * ownership.quantity + total_cost
            ownership.price_at_time = total_value / total_shares
            ownership.quantity = total_shares
        else:
            # 새로운 주식 매수
            ownership = S_Ownership(
                user_id=user_id,
                j_id=j_id,
                price_at_time=stock.price,
                quantity=quantity
            )
            db.add(ownership)
        
        # 지갑에서 돈 차감
        wallet.money = float(wallet.money) - total_cost
        
        db.commit()
        return {"message": f"{stock.name} {quantity}주 매수 성공"}