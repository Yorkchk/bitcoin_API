from sqlmodel import Session, select, func, col, cast
from sqlalchemy import DateTime
from db import ohlcHistory, Date,Time,Coin,Currency,ohlcLive
from schemas.schemas import ohlc_schema


class OhlcService:
    def __init__(self, session: Session):
        self.session = session


    def get_ohlc_history(self, limit: int = None, start_time: str = None, end_time: str = None):
        statement = (
            select(
                # 1. CAST(CONCAT(...) AS DATETIME2)
                cast(
                    func.concat(Date.full_date, ' ', Time.time_of_day),
                    DateTime
                ).label("timestamp"),
                
                # 2. Column Aliasing (.label in SQLAlchemy/SQLModel)
                Coin.coin_id.label("coin_name"),
                Currency.currency_code.label("currency_name"),
                ohlcHistory.open.label("open"),
                ohlcHistory.high.label("high"),
                ohlcHistory.low.label("low"),
                ohlcHistory.close.label("close")
            )
            # 3. Joins
            .join(Coin, ohlcHistory.coin_key == Coin.coin_key)
            .join(Currency, ohlcHistory.currency_key == Currency.currency_key)
            .join(Date, ohlcHistory.date_key == Date.date_key)
            .join(Time, ohlcHistory.time_key == Time.time_key)
            .order_by(col(Date.full_date), col(Time.time_of_day))

        )
        if start_time:
            statement = statement.where(
                func.concat(Date.full_date, ' ', Time.time_of_day) >= start_time
            )
        if end_time:
            statement = statement.where(
                func.concat(Date.full_date, ' ', Time.time_of_day) <= end_time
            )
        statement = statement.limit(limit)

        results = self.session.exec(statement).all()

        schema = [
            ohlc_schema(
                timestamp=row.timestamp,
                coin_name=row.coin_name,
                currency_name=row.currency_name,
                open=row.open,
                high=row.high,
                low=row.low,
                close=row.close
            )
            for row in results
        ]
        return schema
    
    def get_ohlc_lastday(self, limit : int = None, start_time: str = None, end_time: str = None):
        statement = (
            select(
                # 1. CAST(CONCAT(...) AS DATETIME2)
                cast(
                    func.concat(Date.full_date, ' ', Time.time_of_day),
                    DateTime
                ).label("timestamp"),
                
                # 2. Column Aliasing (.label in SQLAlchemy/SQLModel)
                Coin.coin_id.label("coin_name"),
                Currency.currency_code.label("currency_name"),
                ohlcLive.open.label("open"),
                ohlcLive.high.label("high"),
                ohlcLive.low.label("low"),
                ohlcLive.close.label("close")
            )
            # 3. Joins
            .join(Coin, ohlcLive.coin_key == Coin.coin_key)
            .join(Currency, ohlcLive.currency_key == Currency.currency_key)
            .join(Date, ohlcLive.date_key == Date.date_key)
            .join(Time, ohlcLive.time_key == Time.time_key)
            .order_by(col(Date.full_date), col(Time.time_of_day))
        )
    
        if start_time:
            statement = statement.where(Time.time_of_day >= start_time)
        if end_time:
            statement = statement.where(Time.time_of_day <= end_time)

        statement = statement.limit(limit)

        results = self.session.exec(statement).all()

        schema = [
            ohlc_schema(
                timestamp=row.timestamp,
                coin_name=row.coin_name,
                currency_name=row.currency_name,
                open=row.open,
                high=row.high,
                low=row.low,
                close=row.close
            )
            for row in results
        ]
        return schema
    
    