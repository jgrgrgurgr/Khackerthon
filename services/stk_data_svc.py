import requests
import json
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from models.models import Stk
from config.kw_cfg import KwCfg

class StkDataSvc:
    def __init__(self):
        self.cfg = KwCfg()
        self.token = None
        
    async def get_token(self) -> Optional[str]:
        if not self.cfg.KIS_KEY or not self.cfg.KIS_SEC:
            return None
            
        url = f"{self.cfg.KIS_URL}/oauth2/tokenP"
        data = {
            "grant_type": "client_credentials",
            "appkey": self.cfg.KIS_KEY,
            "appsecret": self.cfg.KIS_SEC
        }
        
        try:
            resp = requests.post(url, json=data)
            if resp.status_code == 200:
                res = resp.json()
                self.token = res.get("access_token")
                return self.token
        except Exception as e:
            print(f"토큰 획득 실패: {e}")
            return None
    
    async def get_stk_price(self, stk_code: str) -> Optional[Dict]:
        if not self.token:
            await self.get_token()
            
        if not self.token:
            return None
            
        url = f"{self.cfg.KIS_URL}/uapi/domestic-stock/v1/quotations/inquire-price"
        hdrs = {
            "Content-Type": "application/json",
            "authorization": f"Bearer {self.token}",
            "appkey": self.cfg.KIS_KEY,
            "appsecret": self.cfg.KIS_SEC,
            "tr_id": "FHKST01010100"
        }
        params = {
            "fid_cond_mrkt_div_code": "J",
            "fid_input_iscd": stk_code
        }
        
        try:
            resp = requests.get(url, headers=hdrs, params=params)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("rt_cd") == "0":
                    out = data.get("output", {})
                    return {
                        "code": stk_code,
                        "name": out.get("hts_kor_isnm", ""),
                        "price": int(out.get("stck_prpr", 0)),
                        "chg_rate": float(out.get("prdy_ctrt", 0)),
                        "vol": int(out.get("acml_vol", 0))
                    }
        except Exception as e:
            print(f"주식 가격 조회 실패 ({stk_code}): {e}")
            return None
    
    async def get_pop_stks(self) -> List[Dict]:
        if not self.token:
            await self.get_token()
            
        if not self.token:
            return []
            
        maj_stks = [
            "005930",  # 삼성전자
            "000660",  # SK하이닉스
            "035420",  # NAVER
            "005380",  # 현대차
            "006400",  # 삼성SDI
            "035720",  # 카카오
            "051910",  # LG화학
            "068270",  # 셀트리온
            "207940",  # 삼성바이오로직스
            "373220",  # LG에너지솔루션
        ]
        
        stks_data = []
        for code in maj_stks:
            stk_info = await self.get_stk_price(code)
            if stk_info:
                stks_data.append(stk_info)
                
        return stks_data
    
    def upd_stks_db(self, stks_data: List[Dict], db: Session):
        for stk_data in stks_data:
            ex_stk = db.query(Stk).filter(
                Stk.name == stk_data["name"]
            ).first()
            
            if ex_stk:
                ex_stk.price = stk_data["price"]
            else:
                new_stk = Stk(
                    name=stk_data["name"],
                    exp=f"종목코드: {stk_data['code']}",
                    price=stk_data["price"]
                )
                db.add(new_stk)
        
        db.commit()
        print(f"{len(stks_data)}개 주식 정보 업데이트 완료")