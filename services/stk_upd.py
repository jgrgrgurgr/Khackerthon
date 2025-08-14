import schedule
import time
import asyncio
from threading import Thread
from sqlalchemy.orm import Session
from config.database import SessLocal
from services.stk_data_svc import StkDataSvc

class StkUpd:
    def __init__(self):
        self.stk_svc = StkDataSvc()
        self.running = False
        
    async def upd_all_stks(self):
        db = SessLocal()
        try:
            print("주식 정보 업데이트 시작...")
            stks_data = await self.stk_svc.get_pop_stks()
            if stks_data:
                self.stk_svc.upd_stks_db(stks_data, db)
                print(f"업데이트 완료: {len(stks_data)}개 종목")
            else:
                print("주식 데이터를 가져올 수 없습니다.")
        except Exception as e:
            print(f"주식 업데이트 중 오류 발생: {e}")
        finally:
            db.close()
    
    def sched_upds(self):
        schedule.every(5).minutes.do(
            lambda: asyncio.run(self.upd_all_stks())
        )
        
        self.running = True
        while self.running:
            schedule.run_pending()
            time.sleep(1)
    
    def start_bg_upds(self):
        if not self.running:
            th = Thread(target=self.sched_upds, daemon=True)
            th.start()
            print("백그라운드 주식 업데이트 시작")
    
    def stop_upds(self):
        self.running = False
        schedule.clear()
        print("주식 업데이트 중지")