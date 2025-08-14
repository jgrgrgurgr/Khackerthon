from fastapi import FastAPI
from config.database import eng, Base
from routers import users, stocks, trading, stk_admin

Base.metadata.create_all(bind=eng)

app = FastAPI(title="Stock Trading API", version="1.0.0", description="주식 거래 시스템 API")

app.include_router(users.rt)
app.include_router(stocks.rt)
app.include_router(trading.rt)
app.include_router(stk_admin.rt)

@app.get("/")
def root():
    return {"msg": "Stock Trading API is running", "ver": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)