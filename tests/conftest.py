import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from api.database import BASE
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.fixture(scope="module")
def engine():
    logger.info("Creating engine")
    return create_engine("sqlite:///:memory:", connect_args={'check_same_thread': False}, echo=False)

@pytest.fixture(scope="module")
def tables(engine):
    logger.info("Creating tables")
    BASE.metadata.create_all(engine)
    logger.info(BASE.metadata.tables)
    yield
    logger.info("Dropping tables")
    BASE.metadata.drop_all(engine)

@pytest.fixture(scope="function")
def session(engine, tables):
    logger.info("Creating session")
    session = scoped_session(sessionmaker(bind=engine, autoflush=False, autocommit=False))
    try:
        yield session
    except Exception as e:
        logger.error(f"Exception occurred: {e}")
        session.rollback()
        raise
    finally:
        if session.is_active:
            session.rollback()
        session.close()
