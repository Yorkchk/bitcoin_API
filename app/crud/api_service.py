from db import APIkey
from sqlmodel import Session
from schemas.schemas import create_API_key_schema, upload_API_key_schema

class APIService:
    def __init__(self, session: Session):
        self.session = session
        self.api_key = APIkey()


    def create_api_key(self, api_key_schema: create_API_key_schema):
        key_name = api_key_schema.key_name
        owner_email = api_key_schema.owner_email

        key_value = self.api_key.generate_APIkey()

        new_api_key = APIkey(
            key_name=key_name,
            owner_email=owner_email,
            key_value=key_value)
        
        self.session.add(new_api_key)
        self.session.commit()
        self.session.refresh(new_api_key)

        return upload_API_key_schema(
            key_name=new_api_key.key_name,
            api_key=self.api_key.hash_APIkey(key_value)
            )