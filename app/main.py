from fastapi import FastAPI
from app.api import routes_auth,routes_predict, routes_health
from app.core.database import engine,Base
from app.middlewares.response_logger import ResponseLoggerMiddleware
from app.core.exception import register_exception_handlers
from app.core import logging_config

app = FastAPI()
Base.metadata.create_all(bind=engine)
app.add_middleware(ResponseLoggerMiddleware)

app.include_router(routes_auth.router , tags = ["Auth"])
app.include_router(routes_predict.router,tags = ["Predict"])
app.include_router(routes_health.router , tags=["Health"])

register_exception_handlers(app)