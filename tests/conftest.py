import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from api.database import BASE, get_db
from api.main import app


SQLALCHEMY_DATABASE_TEST_URL = "sqlite://"
engine = create_engine(
    SQLALCHEMY_DATABASE_TEST_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

BASE.metadata.create_all(bind=engine)

def override_get_db():
    """Override the get_db() dependency with a test database."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def session():
    """Create a new session for each test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal()
    try:
        yield session
    except Exception:
        transaction.rollback()
        raise
    finally:
        if transaction.is_active:
            transaction.rollback()
        session.close()
        connection.close()

@pytest.fixture
def client():
    """Create a new TestClient for each test."""
    with TestClient(app) as client:
        yield client