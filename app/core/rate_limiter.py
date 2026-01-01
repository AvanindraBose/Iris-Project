from fastapi import HTTPException,Request,status,Depends
from app.core.dependecies import get_redis_client , get_refresh_user_id , get_current_user
import os
from dotenv import load_dotenv

load_dotenv()
LOGIN_RATE_LIMIT = int(os.getenv("LOGIN_RATE_LIMIT", 5))
LOGIN_RATE_WINDOW = int(os.getenv("LOGIN_RATE_WINDOW", 60))

REFRESH_RATE_LIMIT = int(os.getenv("REFRESH_RATE_LIMIT", 10))
REFRESH_RATE_WINDOW = int(os.getenv("REFRESH_RATE_WINDOW", 300))

PREDICT_RATE_LIMIT = int(os.getenv("PREDICT_RATE_LIMIT", 50))
PREDICT_RATE_WINDOW = int(os.getenv("PREDICT_RATE_WINDOW", 60))


def login_rate_limiter(request:Request):
    redis_client = get_redis_client()
    client_ip = request.client.host

    key = f"rate:login:{client_ip}"

    current_count = redis_client.get(key)

    if current_count is None:
        redis_client.setex(key,LOGIN_RATE_WINDOW,1)
        return
    
    if int(current_count) >= LOGIN_RATE_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later."
        )
    
    redis_client.incr(key)

def refresh_rate_limiter(user_id:str = Depends(get_refresh_user_id)):
    redis_client = get_redis_client()

    key = f"rate:refresh:{user_id}"
    current_count = redis_client.get(key)
    # redis_client returns string values

    if current_count is None:
        redis_client.setex(key,REFRESH_RATE_WINDOW,1)
        return
    
    if int(current_count) >= REFRESH_RATE_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many refresh token attempts. Please try again later."
        )
    redis_client.incr(key)

def predict_rate_limiter(user_id:str = Depends(get_current_user)):
    redis_client = get_redis_client()

    key = f"rate:predict:{user_id}"

    current_count = redis_client.get(key)

    if current_count is None:
        redis_client.setex(key,PREDICT_RATE_WINDOW,1)
        return
    
    if int(current_count) >= PREDICT_RATE_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail = "Too many prediction requests. Please try again Later"
        )
    
    redis_client.incr(key)



