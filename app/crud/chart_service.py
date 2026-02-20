from sqlmodel import Session, select, func, col, cast
from sqlalchemy import DateTime
from db import chartHistory, Date,Time,Coin,Currency,chartHistory, chartLive
from schemas.schemas import chart_schema


class ChartService:
    def __init__(self, session:Session):
        self.session = session

    def get_chart_history(self, limit: int = None, start_date: str = None, end_date: str = None):
        statement = (
            select(
                # 1. CAST(CONCAT(...) AS DATETIME2)
                cast(
                    func.concat(Date.full_date, ' ', Time.time_of_day),
                    DateTime
                ).label("bitcoin_date"),
                
                # 2. Column Aliasing (.label in SQLAlchemy/SQLModel)
                Coin.coin_id.label("coin_name"),
                Currency.currency_code.label("currency_name"),
                chartHistory.prices.label("price"),
                chartHistory.market_caps.label("market_cap"),
                chartHistory.total_volumes.label("total_volume")
            )
            # 3. Joins
            .join(Coin, chartHistory.coin_key == Coin.coin_key)
            .join(Currency, chartHistory.currency_key == Currency.currency_key)
            .join(Date, chartHistory.date_key == Date.date_key)
            .join(Time, chartHistory.time_key == Time.time_key)
            .order_by(col(Date.full_date), col(Time.time_of_day))
        )
        if start_date:
            statement = statement.where(
                func.concat(Date.full_date, ' ', Time.time_of_day) >= start_date
            )
        if end_date:
            statement = statement.where(
                func.concat(Date.full_date, ' ', Time.time_of_day) <= end_date
            )
        statement = statement.limit(limit)

        results = self.session.exec(statement).all()

        schema = [
            chart_schema(
                bitcoin_date=row.bitcoin_date,
                coin_name=row.coin_name,
                currency_name=row.currency_name,
                price=row.price,
                market_cap=row.market_cap,
                total_volume=row.total_volume
            )
            for row in results
        ]
        return schema

    def get_chart_lastday(self, limit : int = None, start_time: str = None, end_time: str = None):
        statement = (
            select(
                # 1. CAST(CONCAT(...) AS DATETIME2)
                cast(
                    func.concat(Date.full_date, ' ', Time.time_of_day),
                    DateTime
                ).label("bitcoin_date"),
                
                # 2. Column Aliasing (.label in SQLAlchemy/SQLModel)
                Coin.coin_id.label("coin_name"),
                Currency.currency_code.label("currency_name"),
                chartLive.prices.label("price"),
                chartLive.market_caps.label("market_cap"),
                chartLive.total_volumes.label("total_volume")
            )
            # 3. Joins
            .join(Coin, chartLive.coin_key == Coin.coin_key)
            .join(Currency, chartLive.currency_key == Currency.currency_key)
            .join(Date, chartLive.date_key == Date.date_key)
            .join(Time, chartLive.time_key == Time.time_key)
            .order_by(col(Date.full_date), col(Time.time_of_day))
        )
    
        if start_time:
            statement = statement.where(Time.time_of_day >= start_time)
        if end_time:
            statement = statement.where(Time.time_of_day <= end_time)

        statement = statement.limit(limit)

        results = self.session.exec(statement).all()

        schema = [
            chart_schema(
                bitcoin_date=row.bitcoin_date,
                coin_name=row.coin_name,
                currency_name=row.currency_name,
                price=row.price,
                market_cap=row.market_cap,
                total_volume=row.total_volume
            )
            for row in results
        ]
        return schema
    

