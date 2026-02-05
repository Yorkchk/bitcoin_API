from pydantic import BaseModel
from datetime import datetime



class chart_data(BaseModel):
    bitcoin_date: datetime
    coin_name: str
    currency_name: str
    price: float
    market_cap: float
    total_volume: float

class ohlc_data(BaseModel):
    timestamp: datetime
    coin_name: str
    currency_name: str
    open: float
    high: float
    low: float
    close: float

