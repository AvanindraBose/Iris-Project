import logging
from fastapi import APIRouter,HTTPException,status,Depends,Request
from fastapi.responses import JSONResponse
from app.core.security import create_access_tokens, create_refresh_tokens,verify_refresh_token,verify_password,hash_password,hash_refresh_token,verify_hashed_refresh_token
from app.schemas.users_auth import UserCreate,UserLogin
from app.core.dependecies import get_db
from sqlalchemy.orm import Session
from app.db.models.users import User
from app.db.models.refresh_token import RefreshToken
from datetime import datetime, timezone
from app.core.rate_limiter import login_rate_limiter , refresh_rate_limiter

router = APIRouter(prefix="/auth",tags=["Auth"])
logger = logging.getLogger(__name__)

@router.post("/signup")
def signup(user_input:UserCreate , db:Session = Depends(get_db)):
    existing_user = db.query(User).filter(
        User.email == user_input.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "User Already Exists"
        )
    
    new_user = User(
        username = user_input.username,
        email = user_input.email,
        password_hash = hash_password(user_input.password)
    )
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except Exception:
        db.rollback()
        logger.error(
            "Signup failed due to DB error",
            exc_info=True,
            extra = {user_input.email}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Could not create user , please try again"
        )

    return {
        "message":"User Created successfully"
    }

@router.post("/login")
def login(request:Request , user_input:UserLogin , db:Session = Depends(get_db) , _ = Depends(login_rate_limiter)):
    db_user = db.query(User).filter(
        User.email == user_input.email
    ).first()

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid credentials"
        )
    
    if not verify_password(user_input.password , db_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid credentials"
        )
    
    access_token = create_access_tokens(str(db_user.id))
    refresh_token,expires_at = create_refresh_tokens(str(db_user.id))

    existing_token = db.query(RefreshToken).filter(
        RefreshToken.user_id == db_user.id
    ).first()

    try:
        if existing_token:
            existing_token.token = hash_refresh_token(refresh_token)
            existing_token.expires_at = expires_at
        else :
            new_refresh_token = RefreshToken(
            user_id = db_user.id,
            token = hash_refresh_token(refresh_token),
            expires_at = expires_at
        )
            db.add(new_refresh_token)
        db.commit()
    except Exception:
        db.rollback()
        logger.error(
            "Login Token Persistance Failed",
            exc_info= True,
            extra={"user_id":db_user.id}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Could not create tokens , please try again"
        )

    response = JSONResponse(
        content= {
            "access_token" : access_token,
            "token_type" : "bearer"
        }
    )
    max_age = int((expires_at - datetime.now(timezone.utc)).total_seconds())
    response.set_cookie(
        key = "refresh_token",
        value = refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        path = "/",
        max_age = max_age
    )
    return response


@router.post("/refresh")
def refresh_access_tokens(request:Request, db:Session = Depends(get_db), _= Depends(refresh_rate_limiter)):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
     raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Refresh token missing"
    )
    payload = verify_refresh_token(refresh_token)
# Using Nested Dependecies
    if payload is None :
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid or expired refresh token"
        )
    
    user_id = payload["sub"]
    # refresh_rate_limiter(user_id)

    db_token = (db.query(RefreshToken).filter(
        RefreshToken.user_id == user_id
    ).with_for_update().first())
# Important technique for row locking
    if db_token is None : 
        logger.warning(
            "Valid refresh JWT but no DB token found",
            extra={"user_id": user_id}
        )
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Refresh Token not found Please login again"
        )
    if not verify_hashed_refresh_token(refresh_token,db_token.token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid Refresh Token Please Login again"
        )
    
    if db_token.expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail = "Refresh Token Expired Please login again"
        )
    
    try:
        new_access_token = create_access_tokens(user_id)
        new_refresh_token , expires_at = create_refresh_tokens(user_id)
        db_token.token = hash_refresh_token(new_refresh_token)
        db_token.expires_at = expires_at
        db.commit()
    except Exception:
        db.rollback()
        logger.error(
            "Refresh token rotation failed",
            exc_info=True,
            extra={"user_id": user_id}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Could not refresh tokens , please try again"
        )
    
    response = JSONResponse(
        content= {
            "access_token" : new_access_token,
            "token_type" : "bearer"
        }
    )
    max_age = int((expires_at - datetime.now(timezone.utc)).total_seconds())
    response.set_cookie(
        key = "refresh_token",
        value = new_refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        path = "/",
        max_age = max_age
    )
    return response

@router.post("/logout")
def logout(
    request: Request,
    db: Session = Depends(get_db)
):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
     raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Refresh token missing"
    )
    payload = verify_refresh_token(refresh_token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    user_id = payload["sub"]

    db_token = db.query(RefreshToken).filter(
        RefreshToken.user_id == user_id
    ).first()

    if not db_token:
        # Already logged out → idempotent logout
        return {"message": "Logged out successfully"}

    if not verify_hashed_refresh_token(refresh_token, db_token.token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    try:
        db.delete(db_token)
        db.commit()
    except Exception:
        db.rollback()
        logger.error(
            "Logout DB operation failed",
            exc_info=True,
            extra={"user_id": user_id}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )

    return {"message": "Logged out successfully"}
