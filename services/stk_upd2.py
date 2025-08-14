import schedule
import time
import threading
from sqlalchemy.orm import Session
from config.database import SessLocal
from services.yf_svc import YfSvc

class StkUpd2:
    def __init__(self):
        self.yf_svc = YfSvc()
        self.running = False
        self.upd_th = None
        
    def upd_all_stks(self):
        if not self.running:
            return
            
        db = SessLocal()
        try:
            print("=" * 50)
            print("주식 정보 업데이트 시작...")
            stks_data = self.yf_svc.get_kr_stks_data()
            
            if stks_data:
                self.yf_svc.upd_stks_db(stks_data, db)
                print(f"업데이트 완료: {len(stks_data)}개 종목")
            else:
                print("주식 데이터를 가져올 수 없습니다.")
                
        except Exception as e:
            print(f"주식 업데이트 중 오류 발생: {e}")
        finally:
            db.close()
            print("=" * 50)
    
    def sched_upds(self):
        schedule.every(10).minutes.do(self.upd_all_stks)
        
        print("주식 업데이트 스케줄러 시작 (10분 간격)")
        while self.running:
            schedule.run_pending()
            time.sleep(30)
    
    def start_bg_upds(self):
        if not self.running:
            self.running = True
            self.upd_th = threading.Thread(target=self.sched_upds, daemon=True)
            self.upd_th.start()
            print("백그라운드 주식 업데이트 시작")
            return True
        else:
            print("이미 업데이트가 실행 중입니다.")
            return False
    
    def stop_upds(self):
        if self.running:
            self.running = False
            schedule.clear()
            print("주식 업데이트 중지")
            return True
        else:
            print("업데이트가 실행되고 있지 않습니다.")
            return False