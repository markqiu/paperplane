from fastapi import FastAPI
from starlette.exceptions import HTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

from .core.settings import Settings
from .version import PROJECT_NAME, description, VERSION
from .api.v1.endpoints.api import router as api_router
from .core.errors import http_422_error_handler, http_error_handler
from .core.engine import start_engine, stop_engine
from .db.client.mongodb_utils import close_mongo_connection, connect_to_mongo


app = FastAPI(title=PROJECT_NAME, description=description, version=VERSION)

if not Settings.ALLOWED_HOSTS:
    Settings.ALLOWED_HOSTS = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=Settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_event_handler("startup", connect_to_mongo)
app.add_event_handler("startup", start_engine)
app.add_event_handler("shutdown", stop_engine)
app.add_event_handler("shutdown", close_mongo_connection)

app.add_exception_handler(HTTPException, http_error_handler)
app.add_exception_handler(HTTP_422_UNPROCESSABLE_ENTITY, http_422_error_handler)

app.include_router(api_router, prefix=Settings.API_BASE_URL)
