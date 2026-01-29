
from typing import Optional
from SQLModel import SQLModel, Field



class ohlcBase(SQLModel):
    id : Optional[int] = Field(default=None, primary_key=True)

    date_key: str = Field(index=True, foreign_key="date.date_key", description="Date key of the OHLC data point")
    time_key: str = Field(index=True, foreign_key="time.time_key", description="timestamp key of the OHLC data point")
    currency_key: str = Field(default="BTC", foreign_key="currency.currency_key", description="coin symbol, e.g., BTC, ETH")
    
    open: float = Field(gt=0, description="Opening price")
    high: float = Field(gt=0, description="Highest price")
    low: float = Field(gt=0, description="Lowest price")
    close: float = Field(gt=0, description="Closing price")

    # date : Date = Relationship(back_populates="ohlc_data")
    # time : Time = Relationship(back_populates="ohlc_data")
    # currency : Currency = Relationship(back_populates="ohlc_data")

class ohlcHistory(ohlcBase, table=True):
    __tablename__ = "gold_fact_4hourlyohlc_last30days"


class ohlcLive(ohlcBase, table=True):
    __tablename__ = "gold_fact_30minohlc_lastday"