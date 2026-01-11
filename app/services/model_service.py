from app.core.config import settings
import pandas as pd
from app.cache.redis_cache import get_cached_prediction,set_cached_prediction
from app.core.security import make_cache_key
from app.core.dependecies import get_model
from fastapi.concurrency import run_in_threadpool

async def predict_flower(data:dict):
    key = make_cache_key(data)
    cached_result = await get_cached_prediction(key)
    if cached_result :
        return cached_result
    model = get_model()
    prediction = await run_in_threadpool(
        _run_model_prediction,
        model,
        data,
    )
    result = {"prediction": prediction}
    await set_cached_prediction(key,result)

    return result

def _run_model_prediction(model , data:dict):
    df = pd.DataFrame([data])
    return int(model.predict(df)[0])



