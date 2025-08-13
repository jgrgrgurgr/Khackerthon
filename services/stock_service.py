from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from models.models import Stk, StkOwn
from schemas.schemas import StkCrt

class StkSvc:
    @staticmethod
    def crt_stk(stk_data: StkCrt, db: Session):
        new_stk = Stk(
            name=stk_data.name, 
            exp=stk_data.exp, 
            price=stk_data.price
        )
        db.add(new_stk)
        db.commit()
        db.refresh(new_stk)
        return new_stk

    @staticmethod
    def get_top_stks(lmt: int, db: Session):
        res = db.query(
            Stk.name,
            func.sum(StkOwn.qty).label("tot_qty")
        ).join(Stk, StkOwn.jid == Stk.jid)\
         .group_by(Stk.jid)\
         .order_by(func.sum(StkOwn.qty).desc())\
         .limit(lmt)\
         .all()
        
        return res

    @staticmethod
    def get_stk_by_id(jid: int, db: Session):
        return db.query(Stk).filter(Stk.jid == jid).first()

    @staticmethod
    def get_all_stks(db: Session):
        return db.query(Stk).all()