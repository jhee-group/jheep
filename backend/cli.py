from argparse import Namespace

import typer
import uvicorn
import alembic
from dramatiq import cli as dcli

from jheep.paths import ALEMBIC_CONFIG_FILE
from jheep.config import settings, Environment


app = typer.Typer(help="JHEEP Commands")


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


@app.command("server")
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
        "jheep.main:app",
        host=host, port=port, workers=workers,
        reload=reload, log_level=log_level, debug=debug
    )


@app.command(
    "worker",
    context_settings={
        "allow_extra_args": True,
        "ignore_unknown_options": True
    },
    add_help_option=False,
)
def run_worker(ctx: typer.Context):
    parser = dcli.make_argument_parser()
    args = parser.parse_args(ctx.args + ["jheep.worker"])
    dcli.main(args)


if __name__ == "__main__":
    app()
