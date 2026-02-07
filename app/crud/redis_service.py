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

    # r = redis.Redis(decode_responses=True) 

    def __init__(self, api_service: APIService, redis):
        self.api_service = api_service
        self.r = redis

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
            usage_key = f"usage:{keyname_provided}"
            auth_key = f"auth:{keyname_provided}"
            
            # 1. Efficiently get auth data
            raw_auth = self.get_value(auth_key)
            if not raw_auth:
                return False 
            
            api_info = APIkey.model_validate_json(raw_auth)
            
            # 2. Atomic check and increment
            # Use INCRBY 0 to get current value without changing it, or just GET
            current_usage = int(self.get_value(usage_key) or 0)

            if current_usage >= api_info.rate_limit_per_day:
                self.deactivate_key(keyname_provided)
                return False
                
            return True
        except Exception as e:
            # Logging here would be better than returning an Exception object
            return False
        
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
            new_count = self.r.incr(redis_key)
            if new_count == 1:
                self.r.expire(redis_key, 86400)
            return new_count
            
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
        # 1. Collect all keys
        keys = list(self.r.scan_iter("auth:*"))
        if not keys:
            return True

        # 2. Pipeline all GET requests (Auth objects and Usage counts)
        with self.r.pipeline() as pipe:
            for key in keys:
                pipe.get(key)
                # Derive the usage key from the auth key (auth:name -> usage:name)
                name = key.split(":", 1)[1]
                pipe.get(f"usage:{name}")
            
            # results will be [auth1, usage1, auth2, usage2, ...]
            results = pipe.execute()

        # 3. Process the results in pairs
        for i in range(0, len(results), 2):
            raw_auth = results[i]
            raw_usage = results[i+1]

            if raw_auth:
                try:
                    api_key_obj = APIkey.model_validate_json(raw_auth)
                    
                    # Default to 0 if usage key doesn't exist in Redis yet
                    usage_count = int(raw_usage) if raw_usage else 0
                    
                    # 4. Sync to Database
                    self.api_service.update_api_key(
                        key_name=api_key_obj.key_name,
                        is_active=api_key_obj.is_active,
                        requests_made_today=usage_count,
                        last_request_date=api_key_obj.last_request_date
                    )
                except (ValidationError, ValueError) as e:
                    # Log the error but continue with other keys
                    print(f"Error processing key {keys[i//2]}: {e}")
                    continue

        return True
    

