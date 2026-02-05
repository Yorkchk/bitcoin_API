from schemas.schemas import coin_schema
from sqlmodel import Session, select
from db import Coin


class CoinService:
    def __init__(self, session : Session):
        self.session = session

    def get_all_coins(self):
        statement = (
            select(
                Coin.coin_key,
                Coin.coin_id,
                Coin.founded_year,
                Coin.ticker_symbol,
                Coin.source,
                Coin.is_active
            )
        )
        results = self.session.exec(statement).all()

        return [
            coin_schema(
                coin_key=row.coin_key,
                coin_id=row.coin_id,
                founded_year=row.founded_year,
                ticker_symbol=row.ticker_symbol,
                source=row.source,
                is_active=row.is_active
            )
            for row in results
        ]