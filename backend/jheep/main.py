import logging.config
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from fastapi_versioning import VersionedFastAPI

from .routers import router
from .config import settings, Environment
from .paths import paths
from .cache import init_cache


log_cfg = Path(__file__).parent / 'logging.conf'
logging.config.fileConfig(log_cfg, disable_existing_loggers=False)


# main app
app = FastAPI(debug=(settings.environment == Environment.DEVELOPMENT))

# CORS
origins = [
    "http://localhost",
    "http://localhost:8800",
    "http://localhost:8801",
    "http://localhost:8802",
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
app.mount("/static", StaticFiles(directory=paths.static_dir), name="static")


@app.on_event("startup")
async def startup():
    if settings.use_cache:
        await init_cache()
