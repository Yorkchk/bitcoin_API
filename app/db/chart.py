from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List


class chartBase(SQLModel):
    id : Optional[int] = Field(default=None, primary_key=True)

    date_key: str = Field(index=True, foreign_key="date.date_key", description="Date key of the chart data point")
    time_key: str = Field(index=True, foreign_key="time.time_key", description="timestamp key of the chart data point")
    currency_key: str = Field(default="USD", foreign_key="currency.currency_key", description="currency symbol, e.g., USD, CAD")
    coin_key: str = Field(default="BTC", foreign_key="currency.currency_key", description="coin symbol, e.g., BTC, ETH")

    
    prices: float = Field(gt=0, description="coin price")
    market_caps: float = Field(gt=0, description="market capitalization")

    date : "Date" = Relationship(back_populates="chart_data")
    time : "Time" = Relationship(back_populates="chart_data")
    currency : "Currency" = Relationship(back_populates="chart_data")
    coin : "Coin" = Relationship(back_populates="chart_data")

class chartHistory(chartBase, table=True):
    __tablename__ = "gold_fact_hourlyprices_last90days"


class chartLive(chartBase, table=True):
    __tablename__ = "gold_fact_5minprices_lastday"

