from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from config.database import get_db
from services.yf_svc import YfSvc
from services.stk_upd2 import StkUpd2

rt = APIRouter(prefix="/admin/stks", tags=["stk-admin"])

stk_upd = StkUpd2()

@rt.post("/fetch-kr")
def fetch_kr_stks(db: Session = Depends(get_db)):
    try:
        yf_svc = YfSvc()
        stks_data = yf_svc.get_kr_stks_data()
        
        if not stks_data:
            raise HTTPException(status_code=400, detail="주식 데이터를 가져올 수 없습니다")
        
        yf_svc.upd_stks_db(stks_data, db)
        
        return {
            "msg": f"{len(stks_data)}개 한국 주식 데이터를 성공적으로 가져왔습니다",
            "stks": [
                {
                    "name": s["name"], 
                    "price": s["price"],
                    "sym": s["sym"]
                } for s in stks_data
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"오류 발생: {str(e)}")

@rt.get("/search")
def search_kr_stks(q: str = Query(..., description="검색어"), db: Session = Depends(get_db)):
    try:
        yf_svc = YfSvc()
        res = yf_svc.search_kr_stk(q)
        
        return {
            "q": q,
            "res": res,
            "cnt": len(res)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"검색 중 오류 발생: {str(e)}")

@rt.post("/start-auto")
def start_auto():
    suc = stk_upd.start_bg_upds()
    
    if suc:
        return {"msg": "한국 주식 자동 업데이트가 시작되었습니다 (10분 주기)"}
    else:
        return {"msg": "자동 업데이트가 이미 실행 중입니다"}

@rt.post("/stop-auto")
def stop_auto():
    suc = stk_upd.stop_upds()
    
    if suc:
        return {"msg": "주식 자동 업데이트가 중지되었습니다"}
    else:
        return {"msg": "실행 중인 자동 업데이트가 없습니다"}

@rt.get("/status")
def get_status():
    return {
        "running": stk_upd.running,
        "interval": "10분",
        "src": "Yahoo Finance (yfinance)",
        "cnt": "한국 주요 15개 종목"
    }

@rt.post("/manual")
def manual_upd(db: Session = Depends(get_db)):
    try:
        yf_svc = YfSvc()
        stks_data = yf_svc.get_kr_stks_data()
        
        if stks_data:
            yf_svc.upd_stks_db(stks_data, db)
            return {
                "msg": f"수동 업데이트 완료: {len(stks_data)}개 종목",
                "upd_stks": [s["name"] for s in stks_data]
            }
        else:
            raise HTTPException(status_code=400, detail="업데이트할 데이터가 없습니다")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"수동 업데이트 실패: {str(e)}")