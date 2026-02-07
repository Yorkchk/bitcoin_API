from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime



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

