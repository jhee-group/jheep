import sys
import asyncio
from argparse import Namespace
from pathlib import Path
import importlib

import typer
import uvicorn
import alembic
from pydantic import ValidationError
from dramatiq import cli as dcli
from tabulate import tabulate

from jheep import __version__
from jheep.paths import paths
from jheep.config import settings, get_config_root, Environment


app = typer.Typer(help="JHEEP Commands")


@app.command()
def info():
    try:
        typer.secho(f"version: {__version__}", bold=True)
        typer.secho(f"config path: {get_config_root()}", bold=True)
        contents = [[key, value] for key, value in settings.dict().items()]
        table = tabulate(contents, headers=['key', 'value'])
        typer.echo(table)
    except ValidationError as e:
        typer.secho(
            "* Some environment variables are missing or invalid.", bold=True, fg="red"
        )
        for error in e.errors():
            typer.secho(error)
        raise typer.Exit(code=1) from e


def preprocess_for_alembic():
    from sqlalchemy import create_engine
    from alembic.config import Config

    url, connect_args = settings.get_database_connection_parameters(asyncio=False)
    engine = create_engine(url, connect_args=connect_args)
    ini_file = paths.alembic_ini_file
    config = Config(ini_file, ini_section="alembic")
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


@app.command("run")
def run_file(file: str = typer.Argument(...)):
    file_path = Path(file).expanduser().resolve()
    sys.path.append(str(file_path.parent))

    module_name = file_path.stem
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    main_func = module.main

    asyncio.run(main_func())


if __name__ == "__main__":
    app()
