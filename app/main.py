from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from sqlmodel import Session, SQLModel
from core.session import engine
from core.session import get_session
from crud.chart_service import ChartService
from crud.ohlc_service import OhlcService
from crud.currency_service import CurrencyService
from crud.coin_service import CoinService
from crud.api_service import APIService
from schemas.schemas import create_API_key_schema, upload_API_key_schema


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code can be added here
    SQLModel.metadata.create_all(bind=engine)
    yield
    # Shutdown code can be added here

app = FastAPI(lifespan=lifespan)



@app.put("/", response_model=upload_API_key_schema)
async def root(create_API_schema: create_API_key_schema, session: Session = Depends(get_session)):
    apiService = APIService(session)
    
    results = apiService.create_api_key(create_API_schema)

    return results

@app.get("/", response_model=list)
async def root(key_name : str, API_KEY : str, session: Session = Depends(get_session)):
    apiService = APIService(session)
    
    if not apiService.verify_api_key(key_name, API_KEY):
        return {"error": "Invalid API Key"}

    chart = ChartService(session)
    results = chart.get_chart_history(limit=10)
    return results