from sqlalchemy.orm import Session
from models.models import Usr, Stk, StkOwn, UsrWallet
from fastapi import HTTPException

class TrdSvc:
    @staticmethod
    def b_stk(uid: int, jid: int, qty: int, db: Session):
        usr = db.query(Usr).filter(Usr.uid == uid).first()
        if not usr:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
        
        stk = db.query(Stk).filter(Stk.jid == jid).first()
        if not stk:
            raise HTTPException(status_code=404, detail="주식을 찾을 수 없습니다")
        
        wallet = db.query(UsrWallet).filter(UsrWallet.uid == uid).first()
        if not wallet:
            raise HTTPException(status_code=404, detail="사용자 지갑을 찾을 수 없습니다")
        
        tot_cost = float(stk.price) * qty
        if float(wallet.money) < tot_cost:
            raise HTTPException(status_code=400, detail="잔액이 부족합니다")
        
        own = db.query(StkOwn).filter(
            StkOwn.uid == uid,
            StkOwn.jid == jid
        ).first()
        
        if own:
            tot_shares = own.qty + qty
            tot_val = float(own.price_at) * own.qty + tot_cost
            own.price_at = tot_val / tot_shares
            own.qty = tot_shares
        else:
            own = StkOwn(
                uid=uid,
                jid=jid,
                price_at=stk.price,
                qty=qty
            )
            db.add(own)
        
        wallet.money = float(wallet.money) - tot_cost
        
        db.commit()
        return {"msg": f"{stk.name} {qty}주를 성공적으로 매수했습니다"}