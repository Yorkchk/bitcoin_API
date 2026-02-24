import redis
import json
from schemas.schemas import chart_schema, ohlc_schema
from pydantic import ValidationError
from db import APIkey
from datetime import datetime


class RedisService:


    def __init__(self, redis_host):
        self.r = redis_host

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
            return False
        else:
            return redis_value
            
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
            auth_key = f"auth:{keyname_provided}"
            new_count = self.r.incr(redis_key)

            if new_count == 1:
                self.r.expire(redis_key, 86400)
            raw_auth = self.r.get(auth_key)

            if raw_auth:
                data = json.loads(raw_auth)
                data["requests_made_today"] = new_count
                self.r.set(auth_key, json.dumps(data))            
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
            return False
        else:
            try:
                data_list = json.loads(redis_value)
                return [chart_schema.model_validate(item) for item in data_list]
            except (ValidationError, json.JSONDecodeError):
                return None
            
    def cache_ohlc(self,type : str, limit : int, start: str, end: str):
        redis_key = f"data:ohlc_{type}:{limit}:{start}:{end}"
        redis_value = self.get_value(redis_key)
        if redis_value is None:
            return False
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

    def scan_over_keys(self):
        print("Step 1: Starting scan...")
        for key in self.r.scan_iter("usage:*"):
            print(f"Step 2: Found key {key}, fetching value...")
            value = self.r.get(key)
            print(f"Step 3: Value is {value}")
        print("Step 4: Done!")
    # def refresh_db_apicash(self):
    #     # 1. Collect all keys
    #     keys = list(self.r.scan_iter("auth:*"))
    #     if not keys:
    #         return True

    #     # 2. Pipeline all GET requests (Auth objects and Usage counts)
    #     with self.r.pipeline() as pipe:
    #         for key in keys:
    #             pipe.get(key)
    #             # Derive the usage key from the auth key (auth:name -> usage:name)
    #             name = key.split(":", 1)[1]
    #             pipe.get(f"usage:{name}")
            
    #         # results will be [auth1, usage1, auth2, usage2, ...]
    #         results = pipe.execute()

    #     # 3. Process the results in pairs
    #     for i in range(0, len(results), 2):
    #         raw_auth = results[i]
    #         raw_usage = results[i+1]

    #         if raw_auth:
    #             try:
    #                 api_key_obj = APIkey.model_validate_json(raw_auth)
                    
    #                 # Default to 0 if usage key doesn't exist in Redis yet
    #                 usage_count = int(raw_usage) if raw_usage else 0
                    
    #                 # 4. Sync to Database
    #                 self.api_service.update_api_key(
    #                     key_name=api_key_obj.key_name,
    #                     is_active=api_key_obj.is_active,
    #                     requests_made_today=usage_count,
    #                     last_request_date=api_key_obj.last_request_date
    #                 )
    #             except (ValidationError, ValueError) as e:
    #                 # Log the error but continue with other keys
    #                 print(f"Error processing key {keys[i//2]}: {e}")
    #                 continue

    #     return True
    

