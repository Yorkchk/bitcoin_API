from db import chartHistory
from fastapi import FastAPI, Depends

from core.config import settings
from sqlmodel import Session, select, create_engine

app = FastAPI()
print("Database URL:", settings.database_url)  # Debugging line to check if the URL is loaded correctly
engine = create_engine(settings.database_url, echo=True)
def get_session():
    with Session(engine) as session:
        yield session

@app.get("/", response_model=dict)
async def root(session : Session = Depends(get_session)):
    # chart1 = chartHistory(date_key="20240101", time_key="1200", currency_key="USD", coin_key="BTC", prices=34000.5, market_caps=650000000.0, total_volumes=45000000.0, id=1, created_at="2024-01-01T12:00:00", updated_at="2024-01-01T12:00:00")
    statement = select(chartHistory).limit(10)
    results = session.exec(statement).all()
    
    return {
        "message": "Welcome to the Bitcoin API!",
        # "sample_chart_data": chart1,
        "database_data" : results
    }