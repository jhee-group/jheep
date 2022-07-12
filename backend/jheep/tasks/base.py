from dask.distributed import Client

from ..config import settings


client = Client(settings.dask_scheduler_url)
