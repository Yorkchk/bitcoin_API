from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import date

class Coin(SQLModel, table=True):
    __tablename__ = "gold_dim_coin"

    coin_key : str = Field(primary_key=True, description="Unique identifier for the coin, e.g., bitcoin, ethereum")

    coin_id : str = Field(description="Coin ID used in external APIs, e.g., bitcoin, ethereum")

    founded_year : date = Field(description="Year the coin was founded")
    ticker_symbol : str = Field(description="Ticker symbol of the coin, e.g., BTC, ETH")
    source : str = Field(description="Source of the coin data, e.g., CoinGecko, CoinMarketCap")
    is_active : bool = Field(description="Indicates if the coin is currently active")

    ohlc_data : List["ohlcBase"] = Relationship(back_populates='coin')
    chart_data : List["chartBase"] = Relationship(back_populates='coin')