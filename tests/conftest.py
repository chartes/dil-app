import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from api.database import BASE, get_db
from api.main import app

os.environ["ENV"] = "test"

SQLALCHEMY_DATABASE_TEST_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_TEST_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=True,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    BASE.metadata.create_all(bind=engine)

init_db()

def override_get_db():
    """Override la dépendance get_db avec une session de test."""
    try:
        db = TestingSessionLocal()
        yield db
    except:
        db.rollback()
        raise
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def session():
    """Crée une session de test avec rollback après chaque test."""
    init_db()  # 🔥 Ajoute ça pour être sûr que les tables existent avant chaque test
    db = TestingSessionLocal()
    try:
        yield db
        db.commit()
    except:
        db.rollback()
        raise
    finally:
        db.close()
