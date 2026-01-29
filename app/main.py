from db import chartHistory
from fastapi import FastAPI

app = FastAPI()


@app.get("/", response_model=dict)
async def root():
    chart1 = chartHistory(date_key="20240101", time_key="1200", currency_key="USD", coin_key="BTC", prices=34000.5, market_caps=650000000.0)
    return {
        "message": "Welcome to the Bitcoin API!",
        "sample_chart_data": chart1
    }