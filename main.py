from fastapi import FastAPI
from config.database import engine, Base
from routers import user, stock, trade

Base.metadata.create_all(bind=engine)

# FastAPI 앱 생성
app = FastAPI(title="Stock Trading API", version="1.0.0", description="주식 거래 시스템 API")

app.include_router(user.router)
app.include_router(stock.router)
app.include_router(trade.router)

@app.get("/", summary="API 상태 확인")
def read_root():
    return {"message": "주식 거래 API 동작", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)