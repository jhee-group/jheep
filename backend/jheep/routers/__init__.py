from fastapi import APIRouter

from . import artifacts

router = APIRouter()
router.include_router(artifacts.router, include_in_schema=True)
