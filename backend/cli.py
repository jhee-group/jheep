from argparse import Namespace

import typer
import uvicorn
import alembic

from cns.paths import ALEMBIC_CONFIG_FILE
from cns.settings import settings, Environment


app = typer.Typer(help="JHEE CNS (Central Nervious System) Commands")


def preprocess_for_alembic():
    from sqlalchemy import create_engine
    from alembic.config import Config

    url, connect_args = settings.get_database_connection_parameters(asyncio=False)
    engine = create_engine(url, connect_args=connect_args)
    config = Config(ALEMBIC_CONFIG_FILE, ini_section="alembic")
    return engine, config


@app.command("makemigrations")
def make_migrations():
    engine, config = preprocess_for_alembic()
    with engine.begin() as connection:
        config.attributes["connection"] = connection
        if config.cmd_opts is None:     # for process_revision_directives in env.py
            config.cmd_opts = Namespace(autogenerate=True)
        alembic.command.revision(config, autogenerate=True)


@app.command("migrate")
def migrate_main():
    engine, config = preprocess_for_alembic()
    with engine.begin() as connection:
        config.attributes["connection"] = connection
        alembic.command.upgrade(config, revision="head")


@app.command("run")
def run_server(
    host: str = "0.0.0.0",
    port: int = settings.port,
    log_level: str = settings.log_level,
    migrate: bool = False,
):
    if migrate:
        migrate_main()

    if settings.environment == Environment.DEVELOPMENT:
        reload, workers, log_level, debug = True, 1, "debug", True
    else:
        reload, workers, log_level, debug = False, 8, log_level.lower(), False

    uvicorn.run(
        "cns.main:app",
        host=host, port=port, workers=workers,
        reload=reload, log_level=log_level, debug=debug
    )


if __name__ == "__main__":
    app()
