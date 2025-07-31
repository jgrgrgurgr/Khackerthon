from fastapi import FastAPI, HTTPException
import yfinance as yf
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/stock/{ticker}")
async def get_stock_price(ticker: str):
    try:
        # 주식 데이터 가져오기
        stock = yf.Ticker(ticker)
        # 최신 가격 정보
        data = stock.history(period="1d", interval="1m")
        
        if data.empty:
            raise HTTPException(status_code=404, detail="Stock not found or no data available")
        
        # 최신 종가
        latest_price = data['Close'].iloc[-1]
        latest_time = data.index[-1].strftime("%Y-%m-%d %H:%M:%S")
        
        return {
            "ticker": ticker,
            "price": round(latest_price, 2),
            "timestamp": latest_time
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stock data: {str(e)}")

@app.get("/stocks/{tickers}")
async def get_multiple_stock_prices(tickers: str):
    try:
        # 쉼표로 구분된 티커 목록
        ticker_list = tickers.split(",")
        results = []
        
        for ticker in ticker_list:
            ticker = ticker.strip()
            stock = yf.Ticker(ticker)
            data = stock.history(period="1d", interval="1m")
            
            if not data.empty:
                latest_price = data['Close'].iloc[-1]
                latest_time = data.index[-1].strftime("%Y-%m-%d %H:%M:%S")
                results.append({
                    "ticker": ticker,
                    "price": round(latest_price, 2),
                    "timestamp": latest_time
                })
            else:
                results.append({
                    "ticker": ticker,
                    "error": "No data available"
                })
                
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stock data: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)