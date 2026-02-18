from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class chart_schema(BaseModel):
    bitcoin_date: datetime
    coin_name: str
    currency_name: str
    price: float
    market_cap: float
    total_volume: float

class ohlc_schema(BaseModel):
    timestamp: datetime
    coin_name: str
    currency_name: str
    open: float
    high: float
    low: float
    close: float

class currency_schema(BaseModel):
    currency_key: str
    currency_code: str
    currency_name: str
    currency_symbol : str
    is_active: bool

class coin_schema(BaseModel):
    coin_key: str
    coin_id: str
    founded_year : datetime
    ticker_symbol : str
    source : str
    is_active: bool

class create_API_key_schema(BaseModel):
    key_name: str
    owner_email: str | None = None

class upload_API_key_schema(BaseModel):
    key_name: str
    api_key: str

class data_request_model(upload_API_key_schema):
    limit: Optional[int] = None
    start_date : Optional[datetime] = None
    end_date : Optional[datetime] = None