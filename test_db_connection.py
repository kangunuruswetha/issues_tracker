# D:\issues_tracker\test_db_connection.py

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
import logging

logging.basicConfig(level=logging.DEBUG) # Set to DEBUG for maximum verbosity
logger = logging.getLogger(__name__)

logger.info("Starting database connection test...")

try:
    # Read environment variables
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "issue_tracker")
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "postgres")

    logger.debug(f"DB_HOST: {db_host}")
    logger.debug(f"DB_PORT: {db_port}")
    logger.debug(f"DB_NAME: {db_name}")
    logger.debug(f"DB_USER: {db_user}")
    # logger.debug(f"DB_PASSWORD: {db_password}") # Don't log password in production!

    # Construct the PostgreSQL URL
    database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    logger.debug(f"DATABASE_URL: {database_url.replace(db_password, '********')}") # Censor password

    # Create SQLAlchemy engine
    engine = create_engine(database_url, connect_args={"connect_timeout": 5}) # Add timeout
    logger.info("SQLAlchemy engine created.")

    # Attempt to connect and execute a simple query
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        logger.info(f"Successfully connected to database. Query result: {result.scalar()}")
        
        # Try to import models and Base
        from app.database.database import Base
        from app.models.models import User
        logger.info("Successfully imported Base and User model.")
        
        # Verify tables exist (optional, but good for debugging)
        inspector = connection.dialect.inspector(connection)
        table_names = inspector.get_table_names()
        logger.info(f"Tables in database: {table_names}")
        if "users" in table_names:
            logger.info(" 'users' table found.")
        else:
            logger.warning(" 'users' table NOT found. Tables might not have been created.")

    logger.info("Database connection test completed successfully.")

except Exception as e:
    logger.error(f"Database connection test FAILED: {e}", exc_info=True)
    import sys
    sys.exit(1) # Exit with error code if test fails