"""conftest.py

File that pytest automatically looks for in any directory.
"""
import os

import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from api.database import (BASE, get_db)
from api.main import (app)
from api.config import BASE_DIR, settings
from api.models.models import (
    User,
    Person,
    Patent,
    City,
    Address,
    Image,
    PatentHasRelations,
    PatentHasAddresses,
    PersonHasAddresses,
    PatentHasImages
)

# set up ENV var for testing
os.environ["ENV"] = "test"

WHOOSH_INDEX_DIR = os.path.join(BASE_DIR, settings.WHOOSH_INDEX_DIR)
SQLALCHEMY_DATABASE_TEST_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_TEST_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

BASE.metadata.create_all(bind=engine)  # Création des tables


@pytest.fixture(scope="function")
def db_session():
    """Create a new database session with a rollback at the end of the test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()



@pytest.fixture(scope="function")
def session_test(db_session):
    """Create a test client that uses the override_get_db fixture to return a session."""

    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
