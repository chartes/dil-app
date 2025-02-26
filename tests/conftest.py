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

# set up ENV var for testing
os.environ["ENV"] = "test"

WHOOSH_INDEX_DIR = os.path.join(BASE_DIR, settings.WHOOSH_INDEX_DIR)
SQLALCHEMY_DATABASE_TEST_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_TEST_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=True,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

BASE.metadata.drop_all(bind=engine)
BASE.metadata.create_all(bind=engine)


def override_get_db():
    """Override the get_db() dependency with a test database."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db



@pytest.fixture(scope="function")
def session():
    """Fixture qui fournit une session de test isolée pour chaque test."""
    db = TestingSessionLocal()  # Crée une session propre
    try:
        yield db
        db.commit()  # Commit les changements après le test
    except Exception:
        db.rollback()  # Annule en cas d'erreur
        raise
    finally:
        db.close()  # Ferme la session après le test

client = TestClient(app)