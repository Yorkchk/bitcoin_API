from db import chartHistory
from fastapi import FastAPI, Depends
from sqlmodel import Session, select
from core.session import get_session
from crud.chart_service import ChartService

app = FastAPI()

@app.get("/", response_model=list)
async def root(session : Session = Depends(get_session)):
    chartHistoryService = ChartService(session)
    
    results = chartHistoryService.get_chart_history_limit(limit=10)

    return results