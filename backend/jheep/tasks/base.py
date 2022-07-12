from dask.distributed import Client

from ..config import settings


client = Client(settings.task_scheduler_url)
