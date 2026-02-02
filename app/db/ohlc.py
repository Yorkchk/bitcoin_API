from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import date

class ohlcBase(SQLModel):
    # id : Optional[int] = Field(default=None, primary_key=True)

    date_key: str = Field(index=True,primary_key=True, foreign_key="gold_dim_date.date_key", description="Date key of the OHLC data point")
    time_key: str = Field(index=True,primary_key=True, foreign_key="gold_dim_time.time_key", description="timestamp key of the OHLC data point")
    currency_key: str = Field(default="USD", foreign_key="gold_dim_currency.currency_key", description="currency symbol, e.g., USD, CAD")
    coin_key: str = Field(default="BTC", foreign_key="gold_dim_coin.coin_key", description="coin symbol, e.g., BTC, ETH")

    open: float = Field(gt=0, description="Opening price")
    high: float = Field(gt=0, description="Highest price")
    low: float = Field(gt=0, description="Lowest price")
    close: float = Field(gt=0, description="Closing price")


class ohlcHistory(ohlcBase, table=True):
    __tablename__ = "gold_fact_4hourlyohlc_last30days"
    date_ohlc_history : Optional["Date"] = Relationship(back_populates="ohlc_history")
    time_ohlc_history : Optional["Time"] = Relationship(back_populates="ohlc_history")
    currency_ohlc_history : Optional["Currency"] = Relationship(back_populates="ohlc_history")
    coin_ohlc_history : Optional["Coin"] = Relationship(back_populates="ohlc_history")


class ohlcLive(ohlcBase, table=True):
    __tablename__ = "gold_fact_30minohlc_lastday"
    date_ohlc_live : Optional["Date"] = Relationship(back_populates="ohlc_live")
    time_ohlc_live : Optional["Time"] = Relationship(back_populates="ohlc_live")
    currency_ohlc_live : Optional["Currency"] = Relationship(back_populates="ohlc_live")
    coin_ohlc_live : Optional["Coin"] = Relationship(back_populates="ohlc_live")
