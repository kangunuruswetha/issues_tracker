from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlalchemy import create_engine # Added this import
from sqlalchemy.orm import sessionmaker # Added this import

from alembic import context

# --- Begin custom imports and path setup ---
import sys
import os

# Add your project root to the Python path.
# This allows Alembic to find modules like 'app.models.models'.
# 'os.path.dirname(__file__)' is the 'alembic/' directory.
# 'os.path.join(..., '..')' goes up one level to the project root.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import your SQLAlchemy declarative base.
# Make sure 'Base' is the correct name for your declarative base.
# If it's something like 'SQLAlchemyBase' in models.py, use that instead.
from app.models.models import Base
# --- End custom imports and path setup ---


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata # This line is correct


# other values from the config, defined by the needs of env.py,
# can be acquired directly from the config object.
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

# --- Define your DATABASE_URL here ---
# IMPORTANT: This DATABASE_URL matches your docker-compose.yml 'db' service credentials.
DATABASE_URL = "postgresql://postgres:postgres@issues_db:5432/issue_tracker"

# Optional: Read from an environment variable if you set it in docker-compose.yml for the backend service
# import os
# DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://user:password@issues_db:5432/dbname")
# --- End DATABASE_URL definition ---


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well. By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # In offline mode, Alembic tries to get the URL from the .ini file,
    # but we can explicitly set it if needed.
    url = DATABASE_URL # Use our defined DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Create the engine using our defined DATABASE_URL
    connectable = create_engine(DATABASE_URL, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # include_schemas=True, # Uncomment if you are using distinct schemas and want to include them
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()