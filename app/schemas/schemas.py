from pydantic import BaseModel
from datetime import datetime


class chartPoint(BaseModel):
    bitcoin_date: datetime
    price: float
    market_cap: float

class chartPointv2(BaseModel):
    bitcoin_date: datetime
    coin_name: str
    currency_name: str
    price: float
    market_cap: float
    total_volume: float

class ohlcPoint(BaseModel):
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float

class chartData(BaseModel):
    currency_name: str
    coin_name : str
    data_points: list[chartPoint]

class ohlcData(BaseModel):
    currency_name: str
    coin_name : str
    data_points: list[ohlcPoint]