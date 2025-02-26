from typing import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.engine.base import Engine

import pytest

from api.database import BASE, get_db
from api.main import app


@pytest.fixture(scope="session")
def engine() -> Generator[Engine, None, None]:
    engine = create_engine("sqlite:///:memory:?check_same_thread=False")
    BASE.metadata.create_all(engine)
    yield engine


@pytest.fixture(scope="function")
def test_session(engine) -> Generator[Session, None, None]:
    conn = engine.connect()
    conn.begin()
    db = Session(bind=conn)
    yield db
    db.rollback()
    conn.close()


@pytest.fixture(scope="function")
def test_client() -> Generator[TestClient, None, None]:
    app.dependency_overrides[get_db] = lambda: test_session
    with TestClient(app) as c:
        yield c