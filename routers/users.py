from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from config.database import get_db
from services.user_service import UsrSvc
from schemas.schemas import UsrCrt, UsrResp, UsrProfitInfo, StkInfo

rt = APIRouter(prefix="/usr", tags=["usr"])

@rt.post("/", response_model=dict)
def crt_usr(usr: UsrCrt, db: Session = Depends(get_db)):
    new_usr = UsrSvc.crt_usr(usr, db)
    return {"msg": "사용자가 성공적으로 생성되었습니다", "uid": new_usr.uid}

@rt.get("/{uid}/profit", response_model=float)
def get_usr_profit_sold(uid: int, db: Session = Depends(get_db)):
    return UsrSvc.get_usr_profit_sold(uid, db)

@rt.get("/{uid}/stks", response_model=List[StkInfo])
def get_usr_stks(uid: int, db: Session = Depends(get_db)):
    res = UsrSvc.get_usr_stks(uid, db)
    
    return [
        StkInfo(
            name=r.name,
            qty=r.qty,
            buy_price=float(r.buy_price),
            cur_price=float(r.cur_price),
            pl=float(r.pl)
        )
        for r in res
    ]

@rt.get("/profit/all", response_model=List[UsrProfitInfo])
def get_all_usr_profit(db: Session = Depends(get_db)):
    res = UsrSvc.get_all_usr_profit(db)
    
    return [
        UsrProfitInfo(
            uid=r.uid,
            uname=r.uname,
            profit_sold=float(r.profit_sold or 0)
        )
        for r in res
    ]