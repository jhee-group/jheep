import os
from pathlib import Path
from enum import Enum
from typing import Optional, Callable
from urllib.parse import urlparse

from pydantic import (
    BaseSettings,
    DirectoryPath,
    root_validator,
    validator,
)

from .db.types import (
    DatabaseConnectionParameters,
    DatabaseType,
    create_database_connection_parameters,
)
from .exceptions import UnsupportedEnvironment


def get_config_root(base_dir: str = "jheep") -> Path:
    config_root = os.environ.get("JHEEP_CONFIG_PATH", None)
    if config_root is None:
        config_root = os.environ.get('XDG_CONFIG_HOME', None)
        if config_root is None:
            config_root = Path.home().joinpath(".config", base_dir)
        else:
            config_root = Path(config_root).joinpath(base_dir)
    else:
        config_root = Path(config_root)
    return config_root


default_config_path = get_config_root().joinpath(".env")


class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TEST = "test"


"""
class SingletonClass(object):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SingletonClass, cls).__new__(cls)
            # Put any initialization here.
        return cls._instance
"""


class DefaultSettings(BaseSettings):
    environment: Environment = Environment.DEVELOPMENT
    host: str = "localhost"
    port: int = 8801
    allow_origin_regex: str = "http://.*localhost:[0-9]+"
    log_level: str = "INFO"
    unit_tests: bool = False

    database_type: DatabaseType = DatabaseType.POSTGRESQL
    database_url: Optional[str] = None
    database_host: Optional[str] = "db"
    database_port: Optional[int] = 5432
    database_username: Optional[str] = "postgres"
    database_password: Optional[str] = "postgres"
    database_name: Optional[str] = "jheep_db"
    database_ssl_mode: Optional[str] = None
    database_location: DirectoryPath = Path.cwd()
    database_pool_recycle_seconds: int = 600

    redis_url: str = "redis://redis:6379"
    use_cache: bool = True

    csrf_cookie_name: str = "jheep_csrftoken"
    csrf_cookie_secure: bool = True

    class Config:
        env_file = default_config_path
        env_file_encoding = 'utf-8'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @root_validator(pre=True)
    def parse_database_url(cls, values):
        database_url = values.get("database_url")
        if database_url is not None:
            parsed_database_url = urlparse(database_url)
            values["database_host"] = parsed_database_url.hostname
            values["database_port"] = parsed_database_url.port
            values["database_username"] = parsed_database_url.username
            values["database_password"] = parsed_database_url.password
            values["database_name"] = parsed_database_url.path[1:]
        return values

    @validator("database_port", pre=True)
    def validate_empty_port(cls, value: Optional[str]) -> Optional[str]:
        if value is None or value == "":
            return None
        return value

    @property
    def config_root(cls) -> Path:
        return get_config_root()

    def get_database_connection_parameters(
        self, asyncio: bool = True, schema: Optional[str] = None
    ) -> DatabaseConnectionParameters:
        """
        Returns a proper database URL and connection arguments for async or not-async context.
        Some tools like Alembic still require a sync connection.
        """
        return create_database_connection_parameters(
            self.database_type,
            asyncio=asyncio,
            username=self.database_username,
            password=self.database_password,
            host=self.database_host,
            port=self.database_port,
            database=self.database_name,
            path=settings.database_location,
            schema=schema,
            ssl_mode=settings.database_ssl_mode,
        )


env = os.environ.get("ENVIRONMENT", Environment.DEVELOPMENT.value)
match env:
    case Environment.DEVELOPMENT.value:
        settings = DefaultSettings()
    case Environment.TEST.value:
        settings = DefaultSettings(
            database_name="jheep_test",
        )
    case _:
        settings = None
        raise UnsupportedEnvironment(f"{env} is not a supported environment")
