"""Alembic migration environment.

The target database URL is read from the application's typed settings
(``ML_DATABASE_URL``) so migrations always run against the same database the app
uses. No connection string is stored in ``alembic.ini``, because a real one
contains a password.

Override the URL programmatically when an isolated database is needed, for
example from a test:

    config.set_main_option("sqlalchemy.url", url)
"""

from __future__ import annotations

from logging.config import fileConfig

from sqlalchemy import create_engine, pool

from alembic import context
from app.core.config import Settings

# Importing the models package registers every table on Base.metadata, which is
# what autogenerate compares against.
from app.models import Base

config = context.config

if config.config_file_name is not None:
    # Interpret the config file for Python logging.
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _database_url() -> str:
    """Resolve the migration target.

    An explicitly set ``sqlalchemy.url`` (for example from a test) takes
    precedence over the environment-derived setting.
    """
    configured = config.get_main_option("sqlalchemy.url")
    if configured:
        return configured
    return Settings().database_url


def run_migrations_offline() -> None:
    """Run migrations without a DBAPI connection, emitting SQL."""
    context.configure(
        url=_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations against a live connection."""
    url = _database_url()
    connectable = create_engine(url, poolclass=pool.NullPool)
    is_sqlite = url.startswith("sqlite")

    try:
        with connectable.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                compare_type=True,
                # SQLite cannot ALTER most column definitions. Batch mode
                # recreates the table instead, so the same migrations work in
                # local development and on PostgreSQL.
                render_as_batch=is_sqlite,
            )

            with context.begin_transaction():
                context.run_migrations()
    finally:
        connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
