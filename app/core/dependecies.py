import joblib
import redis
import os
from fastapi import Header,HTTPException,status,Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings
from app.core.security import verify_access_token
from app.core.database import SessionLocal
from dotenv import load_dotenv

load_dotenv()
REDIS_URL = os.getenv("REDIS_URL")
security = HTTPBearer()

def get_api_key(api_key:str = Header(...)):
    if api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key"
        )

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
        credentials:HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    payload = verify_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid or expired access token"
        )
    
    return payload["sub"]

def get_redis_client():
    return redis.StrictRedis.from_url(REDIS_URL,decode_responses=True,socket_timeout=2,socket_connect_timeout=2)

_model = None

def get_model():
    global _model
    if _model is None:
        _model = joblib.load(settings.MODEL_PATH)
    return _model


