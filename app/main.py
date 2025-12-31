from fastapi import FastAPI
from app.api import routes_auth,routes_test
from app.core.database import engine,Base
from app.middlewares.response_logger import ResponseLoggerMiddleware
from app.core.exception import register_exception_handlers

app = FastAPI()
Base.metadata.create_all(bind=engine)
app.add_middleware(ResponseLoggerMiddleware)
register_exception_handlers(app)
app.include_router(routes_auth.router , tags = ["Auth"])
app.include_router(routes_test.router,tags = ["Predict"])
