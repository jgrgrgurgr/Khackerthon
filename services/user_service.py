from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from models.models import Usr, UsrWallet, StkOwn, Stk
from schemas.schemas import UsrCrt
from fastapi import HTTPException

class UsrSvc:
    @staticmethod
    def crt_usr(usr_data: UsrCrt, db: Session):
        ex_usr = db.query(Usr).filter(Usr.id == usr_data.id).first()
        if ex_usr:
            raise HTTPException(status_code=400, detail="사용자 ID가 이미 존재합니다")
        
        new_usr = Usr(id=usr_data.id, pwd=usr_data.pwd)
        db.add(new_usr)
        db.flush()
        
        new_wallet = UsrWallet(uid=new_usr.uid, money=usr_data.init_money)
        db.add(new_wallet)
        db.commit()
        
        return new_usr

    @staticmethod
    def get_usr_profit_sold(uid: int, db: Session):
        res = db.query(
            func.coalesce(
                func.sum((Stk.price - StkOwn.price_at) * StkOwn.qty), 
                0
            ).label("profit_sold")
        ).select_from(Usr)\
         .outerjoin(StkOwn, Usr.uid == StkOwn.uid)\
         .outerjoin(Stk, StkOwn.jid == Stk.jid)\
         .filter(Usr.uid == uid)\
         .first()
        
        if res is None:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
        
        return float(res.profit_sold or 0)

    @staticmethod
    def get_all_usr_profit(db: Session):
        res = db.query(
            Usr.uid,
            Usr.id.label("uname"),
            func.coalesce(
                func.sum((Stk.price - StkOwn.price_at) * StkOwn.qty), 
                0
            ).label("profit_sold")
        ).outerjoin(StkOwn, Usr.uid == StkOwn.uid)\
         .outerjoin(Stk, StkOwn.jid == Stk.jid)\
         .group_by(Usr.uid)\
         .all()
        
        return res

    @staticmethod
    def get_usr_stks(uid: int, db: Session):
        usr_ex = db.query(Usr).filter(Usr.uid == uid).first()
        if not usr_ex:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")

        res = db.query(
            Stk.name,
            StkOwn.qty,
            StkOwn.price_at.label("buy_price"),
            Stk.price.label("cur_price"),
            ((Stk.price - StkOwn.price_at) * StkOwn.qty).label("pl")
        ).join(Stk, StkOwn.jid == Stk.jid)\
         .filter(StkOwn.uid == uid)\
         .all()
        
        return res