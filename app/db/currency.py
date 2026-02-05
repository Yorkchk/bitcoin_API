from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

class Currency(SQLModel, table=True):
    __tablename__ = "gold_dim_currency"

    currency_key : str = Field(primary_key=True, description="Unique identifier for the currency, e.g., bitcurrency, ethereum")


    currency_code : str = Field(description="Currency code used in external APIs, e.g., USD, CAD")
    currency_name : str = Field(description="Full name of the currency, e.g., United States Dollar, Canadian Dollar")
    currency_symbol : str = Field(description="Symbol of the currency, e.g., $, CA$")
    is_active : bool = Field(description="Indicates if the currency is currently active")

    ohlc_history : List["ohlcHistory"] = Relationship(back_populates='currency_ohlc_history')
    chart_history : List["chartHistory"] = Relationship(back_populates='currency_chart_history')

    ohlc_live : List["ohlcLive"] = Relationship(back_populates='currency_ohlc_live')
    chart_live : List["chartLive"] = Relationship(back_populates='currency_chart_live')