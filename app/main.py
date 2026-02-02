from db import chartHistory
from fastapi import FastAPI, Depends
from sqlmodel import Session, select
from core.session import get_session

app = FastAPI()

@app.get("/", response_model=dict)
async def root(session : Session = Depends(get_session)):
    statement = select(chartHistory).limit(10)
    results = session.exec(statement).all()
    
    return {
        "message": "Welcome to the Bitcoin API!",
        "database_data" : results
    }