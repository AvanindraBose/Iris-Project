from app.core.config import settings
import pandas as pd
from app.cache.redis_cache import get_cached_prediction,set_cached_prediction
from app.core.security import make_cache_key
from app.core.dependecies import get_model


def predict_flower(data:dict):
    key = make_cache_key(data)
    cached_result = get_cached_prediction(key)
    if cached_result :
        return cached_result
    model = get_model()
    df = pd.DataFrame([data])
    prediction = model.predict(df)[0]

    set_cached_prediction(key , {"prediction":int(prediction)})

    return {"prediction": int(prediction)}


