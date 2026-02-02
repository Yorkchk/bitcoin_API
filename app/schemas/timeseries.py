from pydantric import BaseModel



class chartPoint(BaseModel):
    timestamp: str
    price: float

class ohlcPoint(BaseModel):
    timestamp: str
    open: float
    high: float
    low: float
    close: float

class chartData(BaseModel):
    currency_key: str
    data_points: list[chartPoint]

class ohlcData(BaseModel):
    currency_key: str
    data_points: list[ohlcPoint]