from urllib.parse import urlparse

import dask
from dask.distributed import Client

from ..config import settings


client = Client(settings.dask_scheduler_url)


def _update_dashboard_config(dashboard_port=8787):
    dslink = dask.config.get('distributed.dashboard.link')
    url = urlparse(dslink)
    if url.hostname != "scheduler":
        return
    else:
        # replace scheduler docker container name to its ip address
        # to be used not only inside docker but also from host browser
        scheduler_addr = client.scheduler_info()['address']
        url = urlparse(scheduler_addr)
        dask.config.set({
            'distributed.dashboard.link': f'http://{url.hostname}:{dashboard_port}'
        })

# for docker-compose env
_update_dashboard_config()
