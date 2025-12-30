from pydantic import BaseModel , float

class ModelInputSchema(BaseModel):
    sepal_length:float
    sepal_width:float
    petal_length:float
    petal_width: float