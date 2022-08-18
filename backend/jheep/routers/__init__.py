from fastapi import APIRouter

from . import filestore
from . import dataset
from . import mlmodel

router = APIRouter()

router.include_router(filestore.router, include_in_schema=True)
