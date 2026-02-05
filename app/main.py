from fastapi import FastAPI, Depends
from sqlmodel import Session
from core.session import get_session
from crud.chart_service import ChartService
from crud.ohlc_service import OhlcService
from crud.currency_service import CurrencyService

app = FastAPI()

@app.get("/", response_model=list)
async def root(session : Session = Depends(get_session)):
    chartHistoryService = CurrencyService(session)
    
    results = chartHistoryService.get_all_currencies()

    return results