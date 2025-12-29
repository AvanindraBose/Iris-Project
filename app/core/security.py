import bcrypt
from datetime import datetime, timezone ,timedelta
from jose import JWTError , jwt
from app.core.config import settings

ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7
# --> Old Logic
# def create_token(data:dict , expire_minutes=30):
#     to_encode = data.copy()
#     expire = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
#     to_encode.update({"exp" : expire})
    
#     return jwt.encode(
#         to_encode,
#         key=settings.JWT_SECRET_KEY,
#         algorithm= settings.JWT_ALGORITHM
#     )

# Replacing New Logic with Access and Refresh Tokens

def create_access_tokens(user_id:str):
    now  = datetime.now(timezone.utc)

    payload = {
        "sub":user_id,
        "token_type":"access",
        "iat":now,
        "exp" : now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }

    return jwt.encode(
        payload,
        settings.JWT_ACCESS_SECRET_KEY,
        settings.JWT_ALGORITHM  
    )

# Refresh Tokens

def create_refresh_tokens(user_id:str):
    now  = datetime.now(timezone.utc)

    payload = {
        "sub":user_id,
        "token_type":"refresh",
        "iat":now,
        "exp" : now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    }

    return jwt.encode(
        payload,
        settings.JWT_REFRESH_SECRET_KEY,
        settings.JWT_ALGORITHM  
    )


# def verify_token(token:str):
#     try:
#         payload = jwt.decode(token,key=settings.JWT_SECRET_KEY,algorithms=[settings.JWT_ALGORITHM])
#         return payload
#     except JWTError:
#         return None

def verify_access_token(token: str):
    try:
        payload = jwt.decode(
            token,
            settings.JWT_ACCESS_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )

        if payload.get("token_type") != "access":
            return None

        return payload

    except JWTError:
        return None

def verify_refresh_token(token: str):
    try:
        payload = jwt.decode(
            token,
            settings.JWT_REFRESH_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )

        if payload.get("token_type") != "refresh":
            return None

        return payload

    except JWTError:
        return None

def hash_password(password:str)-> str:
    return bcrypt.hashpw(
        password.encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')

def verify_password(password:str , hashed_password:str)-> bool:
    return bcrypt.checkpw(
        password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


