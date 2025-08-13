from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from config.database import get_db
from services.stock_service import StkSvc
from schemas.schemas import StkCrt, StkResp, TopStkInfo

rt = APIRouter(prefix="/stk", tags=["stk"])

@rt.post("/", response_model=dict)
def crt_stk(stk: StkCrt, db: Session = Depends(get_db)):
    new_stk = StkSvc.crt_stk(stk, db)
    return {"msg": "주식이 성공적으로 생성되었습니다", "jid": new_stk.jid}

@rt.get("/top", response_model=List[TopStkInfo])
def get_top_stks(lmt: int = 3, db: Session = Depends(get_db)):
    res = StkSvc.get_top_stks(lmt, db)
    
    return [
        TopStkInfo(
            name=r.name,
            tot_qty=r.tot_qty
        )
        for r in res
    ]

@rt.get("/", response_model=List[StkResp])
def get_all_stks(db: Session = Depends(get_db)):
    stks = StkSvc.get_all_stks(db)
    return stks

@rt.get("/{jid}", response_model=StkResp)
def get_stk(jid: int, db: Session = Depends(get_db)):
    stk = StkSvc.get_stk_by_id(jid, db)
    if not stk:
        raise HTTPException(status_code=404, detail="주식을 찾을 수 없습니다")
    return stk