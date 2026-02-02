from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING


class chartBase(SQLModel):
    # id : Optional[int] = Field(default=None, primary_key=True)

    date_key: str = Field(index=True,primary_key=True, foreign_key="gold_dim_date.date_key", description="Date key of the chart data point")
    time_key: str = Field(index=True,primary_key=True, foreign_key="gold_dim_time.time_key", description="timestamp key of the chart data point")
    currency_key: str = Field(default="USD", foreign_key="gold_dim_currency.currency_key", description="currency symbol, e.g., USD, CAD")
    coin_key: str = Field(default="BTC", foreign_key="gold_dim_coin.coin_key", description="coin symbol, e.g., BTC, ETH")

    
    prices: float = Field(gt=0, description="coin price")
    market_caps: float = Field(gt=0, description="market capitalization")

class chartHistory(chartBase, table=True):
    __tablename__ = "gold_fact_hourlyprices_last90days"

    date_chart_history : Optional["Date"] = Relationship(back_populates="chart_history")
    time_chart_history : Optional["Time"] = Relationship(back_populates="chart_history")
    currency_chart_history : Optional["Currency"] = Relationship(back_populates="chart_history")
    coin_chart_history : Optional["Coin"] = Relationship(back_populates="chart_history")



class chartLive(chartBase, table=True):
    __tablename__ = "gold_fact_5minprices_lastday"
    
    date_chart_live : Optional["Date"] = Relationship(back_populates="chart_live")
    time_chart_live : Optional["Time"] = Relationship(back_populates="chart_live")
    currency_chart_live : Optional["Currency"] = Relationship(back_populates="chart_live")
    coin_chart_live : Optional["Coin"] = Relationship(back_populates="chart_live")
