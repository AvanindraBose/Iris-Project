import json
from app.core.dependecies  import get_redis_client


def get_cached_prediction(key:str):
    try:
        redis_client = get_redis_client()
        value = redis_client.get(key)
        return json.loads(value) if value else None
    except Exception as e:
        print(f"Error retrieving cached prediction: {e}")
        return None

def set_cached_prediction(key:str,value:dict , ttl:int = 300):
    try:
        redis_client = get_redis_client()
        redis_client.setex(key,ttl,json.dumps(value))
    except Exception as e:
        print(f"Error setting cached prediction: {e}")