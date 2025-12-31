import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger("exception_handler")

def register_exception_handlers(app: FastAPI):
    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.exception(
            "Unhandled exception | method=%s path=%s",
            request.method,
            request.url.path
        )
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error"}
        )
