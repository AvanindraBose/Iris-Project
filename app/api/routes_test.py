from fastapi import APIRouter, Depends
from app.core.dependecies import get_current_user

router = APIRouter()

@router.get("/protected")
def protected_route(current_user=Depends(get_current_user)):
    return {
        "message": "You are authenticated",
        "user": current_user
    }
