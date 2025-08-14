import yfinance as yf
import pandas as pd
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from models.models import Stk
from config.stk_cfg import StkCfg
import time

class YfSvc:
    def __init__(self):
        self.cfg = StkCfg()
        
    def get_stk_info(self, sym: str) -> Optional[Dict]:
        try:
            stk = yf.Ticker(sym)
            hist = stk.history(period="1d")
            info = stk.info
            
            if hist.empty:
                return None
                
            cur_price = hist['Close'].iloc[-1]
            vol = hist['Volume'].iloc[-1]
            
            cur_price = float(cur_price)
            
            return {
                "sym": sym,
                "price": int(cur_price),
                "vol": int(vol),
                "cur": info.get("currency", "KRW"),
                "mcap": info.get("marketCap", 0),
                "prev": float(hist['Close'].iloc[-1]) if len(hist) > 0 else cur_price
            }
            
        except Exception as e:
            print(f"주식 정보 조회 실패 ({sym}): {e}")
            return None
    
    def get_multi_stks(self, syms: List[str]) -> List[Dict]:
        stks_data = []
        
        try:
            data = yf.download(syms, period="1d", group_by="ticker")
            
            for sym in syms:
                try:
                    if len(syms) == 1:
                        stk_data = data
                    else:
                        stk_data = data[sym]
                    
                    if stk_data.empty:
                        continue
                        
                    cur_price = float(stk_data['Close'].iloc[-1])
                    vol = int(stk_data['Volume'].iloc[-1])
                    
                    stks_data.append({
                        "sym": sym,
                        "price": int(cur_price),
                        "vol": vol,
                        "prev": float(stk_data['Close'].iloc[-1])
                    })
                    
                except Exception as e:
                    print(f"개별 주식 처리 실패 ({sym}): {e}")
                    continue
                    
        except Exception as e:
            print(f"다중 주식 조회 실패: {e}")
            for sym in syms:
                stk_info = self.get_stk_info(sym)
                if stk_info:
                    stks_data.append(stk_info)
                time.sleep(0.1)
        
        return stks_data
    
    def get_kr_stks_data(self) -> List[Dict]:
        print("한국 주식 데이터 조회 시작...")
        
        syms = [stk["sym"] for stk in self.cfg.KR_STKS]
        stks_data = self.get_multi_stks(syms)
        
        sym_to_info = {stk["sym"]: stk for stk in self.cfg.KR_STKS}
        
        res = []
        for stk_data in stks_data:
            sym = stk_data["sym"]
            if sym in sym_to_info:
                kr_info = sym_to_info[sym]
                res.append({
                    **stk_data,
                    "name": kr_info["name"],
                    "desc": kr_info["desc"]
                })
        
        print(f"총 {len(res)}개 한국 주식 데이터 조회 완료")
        return res
    
    def search_kr_stk(self, q: str) -> List[Dict]:
        res = []
        q_lower = q.lower()
        
        for stk in self.cfg.KR_STKS:
            if (q_lower in stk["name"].lower() or 
                q_lower in stk["desc"].lower() or
                q in stk["sym"]):
                
                stk_data = self.get_stk_info(stk["sym"])
                if stk_data:
                    res.append({
                        **stk_data,
                        "name": stk["name"],
                        "desc": stk["desc"]
                    })
        
        return res
    
    def upd_stks_db(self, stks_data: List[Dict], db: Session):
        upd_cnt = 0
        add_cnt = 0
        
        for stk_data in stks_data:
            try:
                ex_stk = db.query(Stk).filter(
                    Stk.name == stk_data["name"]
                ).first()
                
                if ex_stk:
                    old_price = ex_stk.price
                    ex_stk.price = stk_data["price"]
                    upd_cnt += 1
                    print(f"업데이트: {stk_data['name']} {old_price} -> {stk_data['price']}")
                else:
                    new_stk = Stk(
                        name=stk_data["name"],
                        exp=stk_data["desc"],
                        price=stk_data["price"]
                    )
                    db.add(new_stk)
                    add_cnt += 1
                    print(f"신규 추가: {stk_data['name']} {stk_data['price']}")
                    
            except Exception as e:
                print(f"DB 업데이트 실패 ({stk_data.get('name', 'Unknown')}): {e}")
                continue
        
        try:
            db.commit()
            print(f"DB 업데이트 완료 - 신규: {add_cnt}개, 업데이트: {upd_cnt}개")
        except Exception as e:
            db.rollback()
            print(f"DB 커밋 실패: {e}")