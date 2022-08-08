import shutil as su
from pathlib import Path

from pydantic import DirectoryPath
from pydantic.dataclasses import dataclass
import alembic
from jinja2 import Template, filters

from .config import settings


_alembic_base: str = "alembic"
_static_base: str = "static"
_locales_base: str = "locales"
_templates_base: str = "templates"
_email_templates_base: str = "email_templates"

_templates_root: DirectoryPath = Path(__file__).parent.joinpath("templates")
_alembic_ini_filename: str = "alembic.ini"


def make_root_dir(path: Path | None = None) -> DirectoryPath:
    if path is None:
        path = settings.config_root
    path.mkdir(mode=0o755, parents=True, exist_ok=True)
    return path


def init_alembic(path: Path) -> None:
    db_param = settings.get_database_connection_parameters(asyncio=False)

    from alembic.config import Config
    config = Config(str(path.joinpath(_alembic_ini_filename)))
    config.set_section_option("alembic", "script_location", "migrations")
    config.set_section_option("alembic", "sqlalchemy.url", str(db_param[0]))
    alembic.command.init(config, str(path), template='generic', package=True)


def init_alembic_from_templates(path: Path) -> None:
    db_param = settings.get_database_connection_parameters(asyncio=False)
    data = {
        'alembic_root': str(path),
        'database_dsn': str(db_param[0]),
        'top_package': settings.alembic_top_package,
        'extra_import': settings.alembic_extra_import,
    }
    src_root = _templates_root.joinpath('alembic')
    for src in src_root.rglob('*'):
        dst = path.joinpath(src.relative_to(src_root))
        if src.is_dir():
            dst.mkdir(mode=0o755, parents=True, exist_ok=True)
            continue

        with open(src, 'r') as f:
            template = f.read()
        rendered = Template(template).render(data)
        with open(dst, 'w') as f:
            f.write(rendered)

    versions_dir = path.joinpath("migrations", "versions")
    versions_dir.mkdir(mode=0o755, parents=True, exist_ok=True)


def make_alembic_dir(path: Path | None = None) -> DirectoryPath:
    if path is None:
        path = settings.config_root / _alembic_base
    if path.exists():
        return path
    path.mkdir(mode=0o755, parents=True, exist_ok=True)

    init_alembic_from_templates(path)

    return path


def make_static_dir(path: Path | None = None) -> DirectoryPath:
    if path is None:
        path = settings.config_root / _static_base
    if path.exists():
        return path
    path.mkdir(mode=0o755, parents=True, exist_ok=True)

    src = _templates_root.joinpath("static")
    dst = path
    if src.exists():
        su.copytree(src, dst, dirs_exist_ok=True)
    return path


def make_locales_dir(path: Path | None = None) -> DirectoryPath:
    if path is None:
        path = settings.config_root / _locales_base
    if path.exists():
        return path
    path.mkdir(mode=0o755, parents=True, exist_ok=True)

    src = _templates_root.joinpath("locales")
    dst = path
    if src.exists():
        su.copytree(src, dst, dirs_exist_ok=True)
    return path


def make_templates_dir(path: Path | None = None) -> DirectoryPath:
    if path is None:
        path = settings.config_root / _templates_base
    if path.exists():
        return path
    path.mkdir(mode=0o755, parents=True, exist_ok=True)

    src = _templates_root.joinpath("templates")
    dst = path
    if src.exists():
        su.copytree(src, dst, dirs_exist_ok=True)
    return path


def make_email_templates_dir(path: Path | None = None) -> DirectoryPath:
    if path is None:
        path = settings.config_root / _email_templates_base
    if path.exists():
        return path
    path.mkdir(mode=0o755, parents=True, exist_ok=True)

    src = _templates_root.joinpath("email_templates")
    dst = path
    if src.exists():
        su.copytree(src, dst, dirs_exist_ok=True)
    return path


@dataclass
class PathSettings:
    root_dir: DirectoryPath = make_root_dir()
    alembic_dir: DirectoryPath = make_alembic_dir()
    static_dir: DirectoryPath = make_static_dir()
    locales_dir: DirectoryPath = make_locales_dir()
    templates_dir: DirectoryPath = make_templates_dir()
    email_templates_dir: DirectoryPath = make_email_templates_dir()

    @property
    def alembic_ini_file(self):
        return self.alembic_dir / _alembic_ini_filename


paths = PathSettings()
