from fastapi import FastAPI
from app.api import routes_auth,routes_test
from app.core.database import engine,Base

app = FastAPI()
Base.metadata.create_all(bind=engine)

app.include_router(routes_auth.router , tags = ["Auth"])
app.include_router(routes_test.router,tags = ["Test"])
