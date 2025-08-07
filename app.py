import sqlite3
import yfinance as yf
import time
import threading
import schedule
from datetime import datetime
from typing import Dict, List, Tuple
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('stock_collector.log'),
        logging.StreamHandler()
    ]
)

class StockDataCollector:
    def __init__(self, db_path: str = "stock_data.db"):
        self.db_path = db_path
        # 주요 글로벌 주식 10개 종목 (yfinance 티커와 이름)
        self.stocks = {
            "AAPL": "Apple Inc.",
            "GOOGL": "Alphabet Inc.",
            "MSFT": "Microsoft Corporation", 
            "AMZN": "Amazon.com Inc.",
            "TSLA": "Tesla Inc.",
            "META": "Meta Platforms Inc.",
            "NVDA": "NVIDIA Corporation",
            "NFLX": "Netflix Inc.",
            "AMD": "Advanced Micro Devices",
            "INTC": "Intel Corporation"
        }
        self.init_database()
        self.running = False
        
    def init_database(self):
        """데이터베이스 초기화 및 테이블 생성"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 주식 정보 테이블
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS stock_info (
                        stock_code TEXT PRIMARY KEY,
                        stock_name TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # 주식 가격 데이터 테이블
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS stock_prices (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        stock_code TEXT NOT NULL,
                        stock_name TEXT NOT NULL,
                        current_price REAL NOT NULL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (stock_code) REFERENCES stock_info (stock_code)
                    )
                ''')
                
                # 주식 정보 삽입
                for code, name in self.stocks.items():
                    cursor.execute('''
                        INSERT OR REPLACE INTO stock_info (stock_code, stock_name)
                        VALUES (?, ?)
                    ''', (code, name))
                
                conn.commit()
                logging.info("데이터베이스 초기화 완료")
                
        except Exception as e:
            logging.error(f"데이터베이스 초기화 오류: {e}")
    
    def get_stock_price(self, stock_code: str) -> float:
        """
        yfinance를 사용하여 실시간 주식 현재가 조회
        """
        try:
            # yfinance로 주식 정보 가져오기
            ticker = yf.Ticker(stock_code)
            
            # 현재가 정보 가져오기
            info = ticker.info
            current_price = info.get('currentPrice')
            
            # currentPrice가 없으면 regularMarketPrice 시도
            if current_price is None:
                current_price = info.get('regularMarketPrice')
            
            # 그래도 없으면 최신 1일 데이터에서 가져오기
            if current_price is None:
                hist = ticker.history(period="1d", interval="1m")
                if not hist.empty:
                    current_price = float(hist['Close'].iloc[-1])
            
            if current_price is not None:
                return float(current_price)
            else:
                logging.warning(f"가격 정보를 찾을 수 없음: {stock_code}")
                return 0.0
                
        except Exception as e:
            logging.error(f"주식가격 조회 오류 ({stock_code}): {e}")
            return 0.0
    
    def collect_and_save_data(self):
        """모든 주식 데이터 수집 및 저장"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                timestamp = datetime.now()
                
                for stock_code, stock_name in self.stocks.items():
                    current_price = self.get_stock_price(stock_code)
                    
                    if current_price > 0:
                        cursor.execute('''
                            INSERT INTO stock_prices (stock_code, stock_name, current_price, timestamp)
                            VALUES (?, ?, ?, ?)
                        ''', (stock_code, stock_name, current_price, timestamp))
                        
                        logging.info(f"{stock_name}({stock_code}): ${current_price:.2f}")
                
                conn.commit()
                logging.info(f"데이터 수집 완료 - {timestamp}")
                
        except Exception as e:
            logging.error(f"데이터 수집 오류: {e}")
    
    def start_collecting(self):
        """1분마다 데이터 수집 시작"""
        self.running = True
        
        # 스케줄 설정 - 1분마다 실행
        schedule.every(1).minutes.do(self.collect_and_save_data)
        
        # 즉시 첫 번째 데이터 수집
        self.collect_and_save_data()
        
        logging.info("주식 데이터 수집 시작 (1분 간격)")
        
        while self.running:
            schedule.run_pending()
            time.sleep(1)
    
    def stop_collecting(self):
        """데이터 수집 중지"""
        self.running = False
        logging.info("주식 데이터 수집 중지")

class StockDataQuery:
    """SQL 조회를 위한 클래스"""
    
    def __init__(self, db_path: str = "stock_data.db"):
        self.db_path = db_path
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Tuple]:
        """SQL 쿼리 실행"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                return cursor.fetchall()
        except Exception as e:
            logging.error(f"쿼리 실행 오류: {e}")
            return []
    
    def get_latest_prices(self) -> List[Tuple]:
        """최신 주식 가격 조회"""
        query = '''
            SELECT sp.stock_code, sp.stock_name, sp.current_price, sp.timestamp
            FROM stock_prices sp
            INNER JOIN (
                SELECT stock_code, MAX(timestamp) as max_timestamp
                FROM stock_prices
                GROUP BY stock_code
            ) latest ON sp.stock_code = latest.stock_code 
                    AND sp.timestamp = latest.max_timestamp
            ORDER BY sp.stock_name
        '''
        return self.execute_query(query)
    
    def get_price_history(self, stock_code: str, hours: int = 24) -> List[Tuple]:
        """특정 종목의 가격 히스토리 조회"""
        query = '''
            SELECT stock_code, stock_name, current_price, timestamp
            FROM stock_prices
            WHERE stock_code = ? 
            AND timestamp >= datetime('now', '-' || ? || ' hours')
            ORDER BY timestamp DESC
        '''
        return self.execute_query(query, (stock_code, hours))
    
    def get_price_statistics(self, stock_code: str, hours: int = 24) -> List[Tuple]:
        """특정 종목의 가격 통계 조회"""
        query = '''
            SELECT 
                stock_code,
                stock_name,
                MIN(current_price) as min_price,
                MAX(current_price) as max_price,
                AVG(current_price) as avg_price,
                COUNT(*) as data_count
            FROM stock_prices
            WHERE stock_code = ? 
            AND timestamp >= datetime('now', '-' || ? || ' hours')
            GROUP BY stock_code, stock_name
        '''
        return self.execute_query(query, (stock_code, hours))
    
    def get_all_stocks_summary(self) -> List[Tuple]:
        """모든 종목의 요약 정보"""
        query = '''
            SELECT 
                sp.stock_code,
                sp.stock_name,
                sp.current_price as latest_price,
                sp.timestamp as latest_update,
                stats.min_price,
                stats.max_price,
                ROUND(stats.avg_price, 2) as avg_price_24h
            FROM stock_prices sp
            INNER JOIN (
                SELECT stock_code, MAX(timestamp) as max_timestamp
                FROM stock_prices
                GROUP BY stock_code
            ) latest ON sp.stock_code = latest.stock_code 
                    AND sp.timestamp = latest.max_timestamp
            LEFT JOIN (
                SELECT 
                    stock_code,
                    MIN(current_price) as min_price,
                    MAX(current_price) as max_price,
                    AVG(current_price) as avg_price
                FROM stock_prices
                WHERE timestamp >= datetime('now', '-24 hours')
                GROUP BY stock_code
            ) stats ON sp.stock_code = stats.stock_code
            ORDER BY sp.stock_name
        '''
        return self.execute_query(query)

def main():
    """메인 실행 함수"""
    print("=== 주식 데이터 수집 및 조회 시스템 ===")
    
    collector = StockDataCollector()
    query_handler = StockDataQuery()
    
    # 백그라운드에서 데이터 수집 시작
    def start_collector():
        collector.start_collecting()
    
    collector_thread = threading.Thread(target=start_collector, daemon=True)
    collector_thread.start()
    
    # 대화형 쿼리 인터페이스
    while True:
        print("\n" + "="*50)
        print("1. 최신 주식 가격 조회")
        print("2. 특정 종목 히스토리 조회") 
        print("3. 특정 종목 통계 조회")
        print("4. 전체 종목 요약")
        print("5. 사용자 정의 SQL 쿼리")
        print("6. 종료")
        
        choice = input("\n선택하세요 (1-6): ").strip()
        
        if choice == "1":
            print("\n=== 최신 주식 가격 ===")
            results = query_handler.get_latest_prices()
            if results:
                print(f"{'티커':<8} {'종목명':<25} {'현재가':<12} {'업데이트 시간'}")
                print("-" * 70)
                for row in results:
                    print(f"{row[0]:<8} {row[1]:<25} ${row[2]:>10.2f} {row[3]}")
            else:
                print("데이터가 없습니다.")
        
        elif choice == "2":
            stock_code = input("티커를 입력하세요 (예: AAPL): ").strip().upper()
            hours = input("조회할 시간(시간 단위, 기본 24): ").strip()
            hours = int(hours) if hours else 24
            
            print(f"\n=== {stock_code} 가격 히스토리 (최근 {hours}시간) ===")
            results = query_handler.get_price_history(stock_code, hours)
            if results:
                print(f"{'티커':<8} {'종목명':<25} {'가격':<12} {'시간'}")
                print("-" * 70)
                for row in results[:20]:  # 최근 20개만 표시
                    print(f"{row[0]:<8} {row[1]:<25} ${row[2]:>10.2f} {row[3]}")
                if len(results) > 20:
                    print(f"... 외 {len(results)-20}개 데이터")
            else:
                print("데이터가 없습니다.")
        
        elif choice == "3":
            stock_code = input("티커를 입력하세요 (예: AAPL): ").strip().upper()
            hours = input("조회할 시간(시간 단위, 기본 24): ").strip()
            hours = int(hours) if hours else 24
            
            print(f"\n=== {stock_code} 가격 통계 (최근 {hours}시간) ===")
            results = query_handler.get_price_statistics(stock_code, hours)
            if results:
                row = results[0]
                print(f"티커: {row[0]}")
                print(f"종목명: {row[1]}")
                print(f"최저가: ${row[2]:.2f}")
                print(f"최고가: ${row[3]:.2f}")
                print(f"평균가: ${row[4]:.2f}")
                print(f"데이터 수: {row[5]}개")
            else:
                print("데이터가 없습니다.")
        
        elif choice == "4":
            print("\n=== 전체 종목 요약 ===")
            results = query_handler.get_all_stocks_summary()
            if results:
                print(f"{'티커':<8} {'종목명':<20} {'현재가':<12} {'최저가':<12} {'최고가':<12} {'24h평균'}")
                print("-" * 90)
                for row in results:
                    min_price = f"${row[4]:.2f}" if row[4] else "N/A"
                    max_price = f"${row[5]:.2f}" if row[5] else "N/A"
                    avg_price = f"${row[6]:.2f}" if row[6] else "N/A"
                    print(f"{row[0]:<8} {row[1]:<20} ${row[2]:>10.2f} {min_price:>10} {max_price:>10} {avg_price:>10}")
            else:
                print("데이터가 없습니다.")
        
        elif choice == "5":
            sql_query = input("SQL 쿼리를 입력하세요: ").strip()
            if sql_query:
                print("\n=== 쿼리 결과 ===")
                results = query_handler.execute_query(sql_query)
                if results:
                    for row in results:
                        print(row)
                else:
                    print("결과가 없습니다.")
        
        elif choice == "6":
            collector.stop_collecting()
            print("프로그램을 종료합니다.")
            break
        
        else:
            print("올바른 선택을 해주세요.")

if __name__ == "__main__":
    main()