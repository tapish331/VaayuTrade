import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = None


def _get_sqlalchemy_url() -> str:
    """
    Resolve the SQLAlchemy URL for Alembic runs.
    Prefer alembic.ini's [alembic] sqlalchemy.url; fall back to $DATABASE_URL.
    """
    url: str | None = config.get_main_option("sqlalchemy.url")
    if not url or not url.strip():
        url = os.getenv("DATABASE_URL")
    if not url or not url.strip():
        raise RuntimeError(
            "Missing SQLAlchemy URL. Set [alembic] sqlalchemy.url in alembic.ini "
            "or export DATABASE_URL."
        )
    return url


def run_migrations_offline() -> None:
    url = _get_sqlalchemy_url()
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    url = _get_sqlalchemy_url()
    connectable = engine_from_config(
        {"sqlalchemy.url": url},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
