import logging

from . import __version__
from . import tasks


logger = logging.getLogger(__name__)
logger.info(f"jheep worker started (version: {__version__})")


__all__ = ["tasks"]
