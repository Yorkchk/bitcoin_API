from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime
import uuid
import os
import hashlib


class APIkey(SQLModel, table=True):
    __tablename__ = "api_keys"

    key_name: str = Field(primary_key=True, index=True,max_length=50,unique=True )
    key_value: str
    created_at: datetime = Field(default=datetime.now())
    is_active: bool = Field(default=True)

    rate_limit_per_day: int = Field(default=100)
    requests_made_today: int = Field(default=0)
    last_request_date: Optional[datetime] = Field(default=None)

    owner_email: Optional[str] = Field(default=None)

    def generate_APIkey(self) -> str:
        key_value = str(uuid.uuid4()).replace('-', '')
        return key_value
    
    def hash_APIkey(self, api_key: str) -> str:
        salt = os.urandom(16)
        hashed_key = hashlib.sha256(salt + api_key.encode()).hexdigest()
        return f"{salt.hex()}:{hashed_key}"
    
    def verify_APIkey(self, stored_key: str, provided_key: str) -> bool:
        salt_hex, hashed_key = stored_key.split(':')
        salt = bytes.fromhex(salt_hex)
        provided_hashed = hashlib.sha256(salt + provided_key.encode()).hexdigest()
        return provided_hashed == hashed_key

    def verify_rate_limit(self) -> bool:
        return self.requests_made_today < self.rate_limit_per_day

    def activate_key(self):
        if self.verify_rate_limit():
            return True
        self.is_active = False
        return False
    
    def reset_daily_limit(self):
        self.requests_made_today = 0

    def set_last_request_date(self, date: datetime):
        self.last_request_date = date

    def increment_requests(self):
        self.requests_made_today += 1
