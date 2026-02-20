from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi_utilities import repeat_every 
from sqlmodel import SQLModel, Session
from core.session import engine
from core.session import get_session
from schemas.schemas import *
from crud.data_manager import DataManager
from datetime import date, time
import logging
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# @asynccontextmanager
# def lifespan(app: FastAPI):
#     # Startup code can be added here
#     SQLModel.metadata.create_all(bind=engine)
#     yield
#     # Shutdown code can be added here



# app = FastAPI(lifespan=lifespan)
app = FastAPI()

@app.on_event("startup")
@repeat_every(seconds=20)
async def db_sync():
    logger.info("START")
    # We use to_thread to keep the background task from blocking the API
    await asyncio.to_thread(sync_worker)
    logger.info("END")

def sync_worker():
    # This is a regular sync function
    with Session(engine) as session:
        dm = DataManager(session)
        dm.refresh_db_apicash()

@app.on_event("startup")
@repeat_every(seconds=24 * 60 * 60)
async def reset_counts():
    with Session(engine) as session:
        dm = DataManager(session=session)
        dm.reset_daily_limit()

def get_dm(session:Session=Depends(get_session)):
    return DataManager(session)

@app.put("/generareApi/", response_model=upload_API_key_schema)
async def generate_apikey(create_API_schema: create_API_key_schema, data_manager : DataManager=Depends(get_dm)):
    new_key = data_manager.generate_apikey(response_model=create_API_schema)
    if not new_key:
        raise HTTPException(status_code=401, detail="key name already exists")
    return new_key

@app.get("/get_historyChart")
async def get_HistorychartData(key_name:str,
                             api_key : str,
                             start_date : Optional[date]=Query(None, description="Start date in YYYY-MM-DD format"),
                             end_date : Optional[date]=Query(None, description="End date in YYYY-MM-DD format"),
                            limit : int = None,
                             data_manager :DataManager=Depends(get_dm)):
    if not data_manager.authenticate_apikey(key_name, api_key):
        raise HTTPException(status_code=404, detail="key name or api key not found")
    elif not data_manager.check_rate_limit(key_name):
        raise HTTPException(status_code=429, detail="Too many requests")
    else:
        chart_data = data_manager.get_chart(
            type="history",
            limit = limit,
            start = start_date,
            end=end_date
        )
        data_manager.increment_request_count(key_name)
        data_manager.update_lastrequest_date(key_name)
        return chart_data
    
@app.get("/get_liveChart")
async def get_livechartData(key_name:str,
                             api_key : str,
                             start_time : Optional[time]=Query(None, description="Start time in HH:MM:SS format"),
                             end_time : Optional[time]=Query(None, description="End time in HH:MM:SS format"),
                            limit : int = None,
                             data_manager: DataManager=Depends(get_dm)):
    if not data_manager.authenticate_apikey(key_name, api_key):
        raise HTTPException(status_code=404, detail="key name or api key not found")
    elif not data_manager.check_rate_limit(key_name):
        raise HTTPException(status_code=429, detail="Too many requests")
    else:
        chart_data = data_manager.get_chart(
            type="live",
            limit = limit,
            start = start_time,
            end=end_time
        )
        data_manager.increment_request_count(key_name)
        data_manager.update_lastrequest_date(key_name)
        return chart_data
    

@app.get("/get_historyOhlc")
async def get_HistoryOhlcData(key_name:str,
                             api_key : str,
                             start_date : Optional[date]=Query(None, description="Start date in YYYY-MM-DD format"),
                             end_date : Optional[date]=Query(None, description="End date in YYYY-MM-DD format"),
                            limit : int = None,
                             data_manager: DataManager=Depends(get_dm)):
    if not data_manager.authenticate_apikey(key_name, api_key):
        raise HTTPException(status_code=404, detail="key name or api key not found")
    elif not data_manager.check_rate_limit(key_name):
        raise HTTPException(status_code=429, detail="Too many requests")
    else:
        ohlc_data = data_manager.get_ohlc(
            type="history",
            limit = limit,
            start = start_date,
            end=end_date
        )
        data_manager.increment_request_count(key_name)
        data_manager.update_lastrequest_date(key_name)
        return ohlc_data
    
@app.get("/get_liveOhlc")
async def get_liveOhlcData(key_name:str,
                             api_key : str,
                             start_time : Optional[time]=Query(None, description="Start time in HH:MM:SS format"),
                             end_time : Optional[time]=Query(None, description="End time in HH:MM:SS format"),
                            limit : int = None,
                             data_manager: DataManager=Depends(get_dm)):
    if not data_manager.authenticate_apikey(key_name, api_key):
        raise HTTPException(status_code=404, detail="key name or api key not found")
    elif not data_manager.check_rate_limit(key_name):
        raise HTTPException(status_code=429, detail="Too many requests")
    else:
        ohlc_data = data_manager.get_chart(
            type="live",
            limit = limit,
            start = start_time,
            end=end_time
        )
        data_manager.increment_request_count(key_name)
        data_manager.update_lastrequest_date(key_name)
        return ohlc_data
    

