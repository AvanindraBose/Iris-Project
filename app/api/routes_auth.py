from fastapi import APIRouter,HTTPException,status,Depends
from app.core.security import create_access_tokens, create_refresh_tokens,verify_refresh_token,verify_password,hash_password
from app.schemas.users_auth import UserCreate,UserLogin
from app.core.dependecies import get_db
from sqlalchemy.orm import Session
from app.db.models.users import User

router = APIRouter(prefix="/auth",tags=["Auth"])

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

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message":"User Created successfully"
    }

@router.post("/login")
def login(user_input:UserLogin , db:Session = Depends(get_db)):
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
            detail = "Invalid Password"
        )
    
    access_token = create_access_tokens(str(db_user.id))
    refresh_token = create_refresh_tokens(str(db_user.id))

    return {
        "access_token":access_token,
        "refresh_token":refresh_token,
        "token_type":"bearer"
    }


@router.post("/refresh")
def refresh_access_tokens(refresh_token:str):
    payload = verify_refresh_token(refresh_token)

    if payload is None :
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid or expired refresh token"
        )
    new_access_token = create_access_tokens(payload["sub"])

    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }


