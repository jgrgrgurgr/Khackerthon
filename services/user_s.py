from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from models.models import User, U_Wallet, S_Ownership, Stock
from schemas.schemas import U_Create
from fastapi import HTTPException

class UserService:
    @staticmethod
    def create_user(user_data: U_Create, db: Session):
        # 중복 ID 확인
        existing_user = db.query(User).filter(User.id == user_data.id).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="동일 ID 존재")
        
        # 사용자 생성
        new_user = User(id=user_data.id, password=user_data.password)
        db.add(new_user)
        db.flush()
        
        # 지갑 생성
        new_wallet = U_Wallet(user_id=new_user.user_id, money=user_data.initial_money)
        db.add(new_wallet)
        db.commit()
        
        return new_user

    @staticmethod
    def get_user_profit_if_sold(user_id: int, db: Session):
        result = db.query(
            func.coalesce(
                func.sum((Stock.price - S_Ownership.price_at_time) * S_Ownership.quantity), 
                0
            ).label("profit_if_sold")
        ).select_from(User)\
         .outerjoin(S_Ownership, User.user_id == S_Ownership.user_id)\
         .outerjoin(Stock, S_Ownership.j_id == Stock.j_id)\
         .filter(User.user_id == user_id)\
         .first()
        
        if result is None:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
        
        return float(result.profit_if_sold or 0)

    @staticmethod
    def get_all_users_profit(db: Session):
        results = db.query(
            User.user_id,
            User.id.label("username"),
            func.coalesce(
                func.sum((Stock.price - S_Ownership.price_at_time) * S_Ownership.quantity), 
                0
            ).label("profit_if_sold")
        ).outerjoin(S_Ownership, User.user_id == S_Ownership.user_id)\
         .outerjoin(Stock, S_Ownership.j_id == Stock.j_id)\
         .group_by(User.user_id)\
         .all()
        
        return results

    @staticmethod
    def get_user_stocks(user_id: int, db: Session):
        # 사용자 존재 확인
        user_exists = db.query(User).filter(User.user_id == user_id).first()
        if not user_exists:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없음")

        results = db.query(
            Stock.name,
            S_Ownership.quantity,
            S_Ownership.price_at_time.label("bought_price"),
            Stock.price.label("current_price"),
            ((Stock.price - S_Ownership.price_at_time) * S_Ownership.quantity).label("profit_loss")
        ).join(Stock, S_Ownership.j_id == Stock.j_id)\
         .filter(S_Ownership.user_id == user_id)\
         .all()
        
        return results