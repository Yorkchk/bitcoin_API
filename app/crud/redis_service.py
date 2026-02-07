import redis
import json
from api_service import APIService
from chart_service import ChartService
from ohlc_service import OhlcService
from schemas.schemas import chart_schema, ohlc_schema
from pydantic import ValidationError
from db import APIkey
from datetime import datetime


class RedisService:

    r = redis.Redis(decode_responses=True) 

    def __init__(self, api_service: APIService):
        self.api_service = api_service

    def set_key(self, key: str, value: str, ex: int = None):
        self.r.set(key, value, ex=ex)

    def get_value(self, key: str):
        return self.r.get(key)
    
    def authenticate_apikey(self, keyname_provided:str, provided_key: str):
        if keyname_provided == "" or provided_key == "":
            return False
        redis_key = f"auth:{keyname_provided}"
        redis_value = self.get_value(redis_key)
        if redis_value is None:
            api_key = self.api_service.verify_apikey(provided_key, keyname_provided)
            if api_key == False:
                return False
            else:
                json_data = api_key.model_dump_json()
                self.set_key(redis_key, json_data, ex=300)
                return True
        else:
            try:
                # 1. Convert the string back into an APIKey object
                api_key_obj = APIkey.model_validate_json(redis_value)
                
                # 2. Now you can safely access attributes
                return (api_key_obj.key_name == keyname_provided and 
                        self.api_service.verify_APIkey_hashedkey(api_key_obj, provided_key))
                        
            except (ValidationError, AttributeError, json.JSONDecodeError):
                # If the data in Redis is old or corrupted, treat it as a cache miss
                return False
            
    # We assume that the authenticate func is called before this one
    def check_rate_limit(self, keyname_provided: str):
        try:
            redis_key = f"usage:{keyname_provided}"
            redis_value = self.get_value(redis_key)
            
            requests_limit = self.get_value(f"auth:{keyname_provided}").rate_limit_per_day

            if redis_value is None:
                requests_made = self.get_value(f"auth:{keyname_provided}").requests_made_today
                self.set_key(redis_key, requests_made, ex=86400)  # Set with 24-hour expiration
                if requests_made < requests_limit:
                    return True
                else:
                    self.deactivate_key(keyname_provided)
                    return False
            else:
                if redis_value < requests_limit:
                    return True
                else:
                    self.deactivate_key(keyname_provided)
                    return False

        except Exception as e:
            return Exception(f"Error checking rate limit: {str(e)}")
        
    def deactivate_key(self, key_name: str):
        raw_auth = self.get_value(f"auth:{key_name}")
        if raw_auth:
            api_key_obj = APIkey.model_validate_json(raw_auth)
            
            api_key_obj.is_active = False
            
            self.set_key(f"auth:{key_name}", api_key_obj.model_dump_json(), ex=300)
        
    # we assume that the check rate limit func is called before this one
    def increment_request_count(self, keyname_provided: str):
        try:
            redis_key = f"usage:{keyname_provided}"
            redis_value = self.get_value(redis_key)

            # I know that the value exist because the check_rate_limit func is called before this one
            self.set_key(redis_key, int(redis_value) + 1, ex=86400)  # Increment the count and reset expiration to 24 hours
            
        except Exception as e:
            return Exception(f"Error incrementing request count: {str(e)}")

    def reset_daily_limit(self):
        try:    
            for key in self.r.scan_iter("usage:*"):
                self.set_key(key, 0, ex=86400)
                return True
        except Exception as e:
            return Exception(f"Error resetting daily limit: {str(e)}")
        
    def cache_chart(self,type : str, limit : int, start: str, end: str):
        redis_key = f"data:chart_{type}:{limit}:{start}:{end}"
        redis_value = self.get_value(redis_key)
        if redis_value is None:
            chart_service = ChartService(self.api_service.session)
            if type == "lastday":
                data = chart_service.get_chart_lastday(limit, start, end)
            elif type == "history":
                data = chart_service.get_chart_data(limit, start, end)
            json_data = json.dumps([item.model_dump() for item in data])
            self.set_key(redis_key, json_data, ex=300)  # Cache for 5 minutes
            return data
        else:
            try:
                data_list = json.loads(redis_value)
                return [chart_schema.model_validate(item) for item in data_list]
            except (ValidationError, json.JSONDecodeError):
                return None
            
    def cache_ohlc(self,type : str, limit : int, start: str, end: str):
        redis_key = f"data:chart_{type}:{limit}:{start}:{end}"
        redis_value = self.get_value(redis_key)
        if redis_value is None:
            ohlc_service = OhlcService(self.api_service.session)
            if type == "lastday":
                data = ohlc_service.get_ohlc_lastday(limit, start, end)
            elif type == "history":
                data = ohlc_service.get_ohlc_history(limit, start, end)
            json_data = json.dumps([item.model_dump() for item in data])
            self.set_key(redis_key, json_data, ex=300)  # Cache for 5 minutes
            return data
        else:
            try:
                data_list = json.loads(redis_value)
                return [ohlc_schema.model_validate(item) for item in data_list]
            except (ValidationError, json.JSONDecodeError):
                return None
    
    def update_lastrequest_date(self, key_name: str):
        raw_auth = self.get_value(f"auth:{key_name}")
        if raw_auth:
            api_key_obj = APIkey.model_validate_json(raw_auth)
            
            api_key_obj.last_request_date = datetime.now()
            
            self.set_key(f"auth:{key_name}", api_key_obj.model_dump_json(), ex=300)


    def refresh_db_apicash(self):
        for key in self.r.scan_iter("auth:*"):
            json_apikey = self.get_value(key)
            if json_apikey:
                try:
                    api_key_obj = APIkey.model_validate_json(json_apikey)
                    requests_made_today = self.get_value(f"usage:{api_key_obj.key_name}")
                    self.api_service.update_api_key(
                        is_active=api_key_obj.is_active,
                        requests_made_today=requests_made_today,
                        last_request_date=api_key_obj.last_request_date,
                        key_name=api_key_obj.key_name
                    )
                except (ValidationError, json.JSONDecodeError):
                    return Exception(f"Error refreshing DB cache for key {key}: Invalid data format")
        return True
    

