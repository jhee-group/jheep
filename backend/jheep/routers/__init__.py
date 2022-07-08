from fastapi import APIRouter

from . import test
from . import artifacts

router = APIRouter()
router.include_router(test.router, include_in_schema=True)
router.include_router(artifacts.router, include_in_schema=True)
