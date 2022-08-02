import logging
import asyncio
from typing import AsyncGenerator, Callable, ClassVar
from urllib.parse import urlparse

from sqlalchemy.ext.asyncio import AsyncSession
import dramatiq
from dramatiq.brokers.redis import RedisBroker

from ..db.main import async_session_maker
from ..config import settings


logger = logging.getLogger(__name__)

params = urlparse(settings.redis_url)
broker = RedisBroker(
    host=params.hostname,
    port=params.port,
    username=params.username,
    password=params.password,
    ssl=params.scheme == "rediss",
    ssl_cert_reqs=None,
)
dramatiq.set_broker(broker)


SendTask = Callable[..., None]


def send_task(task: dramatiq.Actor, *args, **kwargs):
    logger.debug("Send task", task=task.actor_name)
    task.send(*args, **kwargs)


class TaskError(Exception):
    pass


class TaskBase:
    __name__: ClassVar[str]

    def __init__(
        self,
        get_session: AsyncGenerator[AsyncSession, None] = async_session_maker,
    ) -> None:
        self.get_session = get_session

    def __call__(self, *args, **kwargs):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # The default policy doesn't create a loop by default for threads (only for main process)
            # Thus, we create one here and set it for future works.
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        logger.debug("start task", task=self.__name__)
        result = loop.run_until_complete(self.run(*args, **kwargs))
        logger.debug("done task", task=self.__name__)
        return result
