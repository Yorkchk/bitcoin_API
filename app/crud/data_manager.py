from fastapi import Depends
import json
from .api_service import APIService
from .redis_servicev2 import RedisService
from .chart_service import ChartService
from .ohlc_service import OhlcService
from pydantic import ValidationError
from db import APIkey


class DataManager():

    def __init__(self, redis : RedisService=Depends(), api_service : APIService=Depends(), chart_service : ChartService=Depends(), ohlc_service : OhlcService=Depends()):
        self.r = redis
        self.api_service = api_service
        self.chart_service = chart_service
        self.ohlc_service = ohlc_service

    def authenticate_apikey(self, keyname_provided:str, provided_key: str):
        if self.r.authenticate_apikey(keyname_provided, provided_key):
            return True
        else:
            api_key = self.api_service.verify_apikey(provided_key, keyname_provided):
            if api_key:
                json_data = api_key.model_dump_json()
                self.r.set_key(f"auth:{keyname_provided}", json_data, ex=300)
                return True
            else:
                return False
    
    def check_rate_limit(self, keyname_provided):
        return self.r.check_rate_limit(keyname_provided)
    
    def increment_request_count(self, keyname_provided: str):
        return self.r.increment_request_count(keyname_provided)
    
    def reset_daily_limit(self):
        return self.r.reset_daily_limit()
    
    def get_chart(self,type : str, limit : int, start: str, end: str):
        chart_data = self.r.cache_chart(type, limit, start, end)
        if chart_data:
            return chart_data
        else:
            redis_key = f"data:chart_{type}:{limit}:{start}:{end}"
            
            if type == "lastday":
                data = self.chart_service.get_chart_lastday(limit, start, end)
            elif type == "history":
                data = self.chart_service.get_chart_history(limit, start, end)
            
            json_data = json.dumps([item.model_dump() for item in data])
            self.r.set_key(redis_key, json_data, ex=300)  # Cache for 5 minutes
            return data
        
    def get_ohlc(self,type : str, limit : int, start: str, end: str):
        ohlc_data = self.r.cache_chart(type, limit, start, end)
        if ohlc_data:
            return ohlc_data
        else:
            redis_key = f"data:ohlc_{type}:{limit}:{start}:{end}"            
            if type == "lastday":
                data = self.ohlc_service.get_ohlc_lastday(limit, start, end)
            elif type == "history":
                data = self.ohlc_service.get_ohlc_history(limit, start, end)
            
            json_data = json.dumps([item.model_dump() for item in data])
            self.r.set_key(redis_key, json_data, ex=300)  # Cache for 5 minutes
            return data
        
    
    def update_lastrequest_date(self, key_name: str):
        return self.r.update_lastrequest_date(key_name)
    
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

