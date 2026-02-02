from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import date



class Date(SQLModel, table=True):
    __tablename__ = "gold_dim_date"

    date_key : str = Field(primary_key=True, description="Date key in YYYYMMDD format")

    ohlc_history : List["ohlcHistory"] = Relationship(back_populates='date_ohlc_history')
    chart_history : List["chartHistory"] = Relationship(back_populates='date_chart_history')
    
    ohlc_live : List["ohlcLive"] = Relationship(back_populates='date_ohlc_live')
    chart_live : List["chartLive"] = Relationship(back_populates='date_chart_live')

    full_date : date = Field(description="Full date")
    day_of_week : str = Field(description="Day of the week, e.g., Monday, Tuesday")
    day_number_in_week : int = Field(description="Day number in the week, e.g., 1 for Monday, 7 for Sunday")
    month_name : str = Field(description="Month name, e.g., January, February")
    quarter : int = Field(description="Quarter of the year, e.g., 1, 2, 3, 4")
    year : int = Field(description="Year, e.g., 2023")
    is_weekend : bool = Field(description="Indicates if the date falls on a weekend")

    # ohlc_history_id : Optional[int] = Field(foreign_key="ohlcHistory.id", description="Identifier for OHLC history data")
    # ohlc_live_id : Optional[int] = Field(foreign_key="ohlcLive.id", description="Identifier for OHLC live data")

    # chart_history_id : Optional[int] = Field(foreign_key="chartHistory.id", description="Identifier for chart history data")
    # chart_live_id : Optional[int] = Field(foreign_key="chartLive.id", description="Identifier for chart live data")

class Time(SQLModel, table=True):
    __tablename__ = "gold_dim_time"

    time_key : str = Field(primary_key=True, description="Time key in HHMM format")

    ohlc_history : List["ohlcHistory"] = Relationship(back_populates='time_ohlc_history')
    chart_history : List["chartHistory"] = Relationship(back_populates='time_chart_history')
    
    ohlc_live : List["ohlcLive"] = Relationship(back_populates='time_ohlc_live')
    chart_live : List["chartLive"] = Relationship(back_populates='time_chart_live')
    
    time_of_day : str = Field(description="Time of day in HH:MM format")
    hour : int = Field(description="Hour of the day, e.g., 0-23")
    minute : int = Field(description="Minute of the hour, e.g., 0-59")
    period_name : str = Field(description="Period name, e.g., Morning, Afternoon, Evening, Night")
    trading_session : str = Field(description="Trading session, e.g., Asian, European, American")
    is_4h_interval : bool = Field(description="Indicates if the time falls on a 4-hour interval")
    is_30min_interval : bool = Field(description="Indicates if the time falls on a 30-minute interval")
    is_1h_interval : bool = Field(description="Indicates if the time falls on a 1-hour interval")
