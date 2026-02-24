from sqlmodel import create_engine, Session
from core.config import settings
import redis

redis_pool = redis.Redis(
    host=settings.redis_host,
      port=settings.redis_port,
        decode_responses=True,
          socket_connect_timeout=1,
            socket_timeout=2)

engine = create_engine(settings.database_url, echo=True)

def get_session():
    with Session(engine) as session:
        yield session

def get_redis():
    try:
        yield redis_pool
    finally:
        pass