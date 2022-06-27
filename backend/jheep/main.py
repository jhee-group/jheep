import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from fastapi_versioning import VersionedFastAPI

from .routers import router
from .settings import settings, Environment
from .paths import STATIC_DIRECTORY


log_cfg = Path(__file__).parent / 'logging.conf'
logging.config.fileConfig(log_cfg, disable_existing_loggers=False)


# main app
app = FastAPI(debug=(settings.environment == Environment.DEVELOPMENT))

# CORS
origins = [
    "http://localhost",
    "http://localhost:8001",
    "http://localhost:8002",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# router
app.include_router(router)

# api version
app = VersionedFastAPI(
    app,
    version_format='{major}',
    prefix_format='/v{major}',
    default_api_version=(1),
)

# mount needs to be defined after VersionedFastAPI call
app.mount("/static", StaticFiles(directory=STATIC_DIRECTORY), name="static")
