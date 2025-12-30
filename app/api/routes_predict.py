from fastapi import APIRouter,HTTPException,Depends,status
from app.core.dependecies import get_current_user,get_api_key
from app.schemas.model_schema import ModelInputSchema
from app.services.model_service import predict_flower

router = APIRouter(prefix="/predict",tags=["Predict"])

@router.post("/predict")
def predict(data:ModelInputSchema , user = Depends(get_current_user) , _= Depends(get_api_key)):
    try : 
        prediction = predict_flower(data.model_dump())
        return prediction
    except :
        raise HTTPException(
            status_code= status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Error Occured During Prediction"
        )
