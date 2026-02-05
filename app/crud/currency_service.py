from sqlmodel import Session, select
from db import Currency
from schemas.schemas import currency_schema

class CurrencyService:
    def __init__(self, session : Session):
        self.session = session

    def get_all_currencies(self):
        statement = (
            select(
                Currency.currency_key,
                Currency.currency_code,
                Currency.currency_name,
                Currency.currency_symbol,
                Currency.is_active
            )
        )
        results = self.session.exec(statement).all()

        return [
            currency_schema(
                currency_key=row.currency_key,
                currency_code=row.currency_code,
                currency_name=row.currency_name,
                currency_symbol=row.currency_symbol,
                is_active=row.is_active
            )
            for row in results
        ]