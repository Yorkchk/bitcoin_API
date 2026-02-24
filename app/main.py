from contextlib import contextmanager
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi_utilities import repeat_every 
from sqlmodel import SQLModel, Session
from core.session import engine
from core.session import get_session, get_redis
from schemas.schemas import *
from crud.data_manager import DataManager
from datetime import date, time
import asyncio


app = FastAPI()


@contextmanager
def get_dm_context():
    """Manual factory for background tasks."""
    # 1. Create session manually
    with Session(engine) as session:
        # 2. Get redis (call the actual logic, not the FastAPI dependency)
        gen = get_redis()
        redis_client = next(gen) 
        # 3. Provide the DM
        yield DataManager(session, redis_client)
    # Session closes automatically here


@app.on_event("startup")
@repeat_every(seconds=15 * 60)  # 15 minutes
async def db_sync():
    await asyncio.to_thread(sync_worker)
    print("Database synchronized with API data.")

def sync_worker():
    with get_dm_context() as dm:
        dm.refresh_db_apicash()
        

@app.on_event("startup")
@repeat_every(seconds=24 * 60 * 60)  # 24 hours
async def reset_counts():
    with get_dm_context() as dm:
        dm.reset_daily_limit()

def get_dm(session:Session=Depends(get_session),redis_host=Depends(get_redis) ):
    return DataManager(session, redis_host)

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
            type="lastday",
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
        ohlc_data = data_manager.get_ohlc(
            type="lastday",
            limit = limit,
            start = start_time,
            end=end_time
        )
        data_manager.increment_request_count(key_name)
        data_manager.update_lastrequest_date(key_name)
        return ohlc_data
    

