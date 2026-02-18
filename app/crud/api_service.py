from fastapi import Depends
from db import APIkey
from sqlmodel import Session
from .utilities import verify_APIkey_hashedkey
from core.session import get_session
from schemas.schemas import create_API_key_schema, upload_API_key_schema
import hashlib
import uuid
import os
from datetime import datetime


class APIService:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session


    def create_api_key(self, api_key_schema: create_API_key_schema):
        
        key_name = api_key_schema.key_name
        owner_email = api_key_schema.owner_email
        
        # keyname is blank
        if key_name.strip() == "":
            return None
        
        # check if key_name exists
        if self.keyname_exists(key_name):
            return None
    
        key_value = self.generate_APIkey()

        new_api_key = APIkey(
            key_name=key_name,
            owner_email=owner_email,
            key_value=self.hash_APIkey(key_value))
        
        self.session.add(new_api_key)
        self.session.commit()
        self.session.refresh(new_api_key)

        return upload_API_key_schema(
            key_name=new_api_key.key_name,
            api_key=key_value
            )

    def generate_APIkey(self) -> str:
        key_value = str(uuid.uuid4()).replace('-', '')
        return key_value
    
    def hash_APIkey(self, api_key: str) -> str:
        salt = os.urandom(16)
        hashed_key = hashlib.sha256(salt + api_key.encode()).hexdigest()
        return f"{salt.hex()}:{hashed_key}"
    
    def verify_apikey(self, provided_key: str, keyname_provided : str) -> bool:
        # check for duplicate key_name
        hashed_key = self.get_api_key(keyname_provided)
        if hashed_key is None:
            return False
        elif verify_APIkey_hashedkey(hashed_key.key_value, provided_key) and hashed_key.key_name == keyname_provided:
            return hashed_key
        return False
    
    
    def get_api_key(self, key_name: str):
        api_key = self.session.get(APIkey, key_name)
        return api_key
    
    def keyname_exists(self, key_name: str):
        existing_key = self.get_api_key(key_name)
        if existing_key is None:
            return False
        return True
    
    def check_rate_limit(self, key_name: str) -> bool:
        api_key = self.get_api_key(key_name)
        if api_key is None:
            return False
        elif not isinstance(api_key, APIkey):
            return False
        return api_key.verify_rate_limit()
    
    def reset_daily_limit(self, key_name: str):
        api_key = self.get_api_key(key_name)
        if api_key is not None and isinstance(api_key, APIkey):
            api_key.reset_daily_limit()
            self.session.add(api_key)
            self.session.commit()
            return True
        return False
    
    def update_last_request_date(self, key_name: str, date: datetime):
        api_key = self.get_api_key(key_name)
        if api_key is not None and isinstance(api_key, APIkey):
            api_key.set_last_request_date(date)
            self.session.add(api_key)
            self.session.commit()
            return True
        return False
    
    def update_api_key(self, is_active: bool, requests_made_today: int, last_request_date: datetime, key_name: str):
        api_key = self.get_api_key(key_name)
        if api_key is not None and isinstance(api_key, APIkey):
            api_key.is_active = is_active
            api_key.requests_made_today = requests_made_today
            api_key.last_request_date = last_request_date
            self.session.add(api_key)
            self.session.commit()
            return True
        return False