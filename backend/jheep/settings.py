from enum import Enum
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from pydantic import (
    BaseSettings,
    DirectoryPath,
    root_validator,
    validator,
)
from sqlalchemy import engine

from .db.types import (
    DatabaseConnectionParameters,
    DatabaseType,
    create_database_connection_parameters,
)


class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class Settings(BaseSettings):
    environment: Environment = Environment.DEVELOPMENT
    host: str = "localhost"
    port: int = 8001
    allow_origin_regex: str = "http://.*localhost:[0-9]+"
    log_level: str = "INFO"
    unit_tests: bool = False

    database_type: DatabaseType = DatabaseType.POSTGRESQL
    database_url: Optional[str] = None
    database_host: Optional[str] = db
    database_port: Optional[int] = 5432
    database_username: Optional[str] = postgres
    database_password: Optional[str] = postgres
    database_name: Optional[str] = "jheep_db"
    database_ssl_mode: Optional[str] = None
    database_location: DirectoryPath = Path.cwd()
    database_pool_recycle_seconds: int = 600

    redis_url: str = "redis://redis:6379"

    csrf_cookie_name: str = "jheep_csrftoken"
    csrf_cookie_secure: bool = True

    class Config:
        env_file = ".env"

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


settings = Settings()
