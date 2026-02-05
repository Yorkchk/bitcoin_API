from fastapi import FastAPI, Depends
from sqlmodel import Session
from core.session import get_session
from crud.chart_service import ChartService
from crud.ohlc_service import OhlcService

app = FastAPI()

@app.get("/", response_model=list)
async def root(session : Session = Depends(get_session)):
    chartHistoryService = OhlcService(session)
    
    results = chartHistoryService.get_ohlc_history(start_time="2026-02-01 00:00:00", end_time="2026-02-04 23:59:59")

    return results