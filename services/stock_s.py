from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from models.models import Stock, S_Ownership
from schemas.schemas import S_Create

class StockService:
    @staticmethod
    def create_stock(stock_data: S_Create, db: Session):
        new_stock = Stock(
            name=stock_data.name, 
            explanation=stock_data.explanation, 
            price=stock_data.price
        )
        db.add(new_stock)
        db.commit()
        db.refresh(new_stock)
        return new_stock

    @staticmethod
    def get_top_stocks(limit: int, db: Session):
        results = db.query(
            Stock.name,
            func.sum(S_Ownership.quantity).label("total_quantity")
        ).join(Stock, S_Ownership.j_id == Stock.j_id)\
         .group_by(Stock.j_id)\
         .order_by(func.sum(S_Ownership.quantity).desc())\
         .limit(limit)\
         .all()
        
        return results

    @staticmethod
    def get_stock_by_id(j_id: int, db: Session):
        return db.query(Stock).filter(Stock.j_id == j_id).first()

    @staticmethod
    def get_all_stocks(db: Session):
        return db.query(Stock).all()