"""conftest.py

File that pytest automatically looks for in any directory.
"""
from typing import TYPE_CHECKING


import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.models.models import BASE

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

@pytest.fixture(scope="session")
def connection_url():
    return "sqlite:///:memory:"

@pytest.fixture(scope="function")
def engine(connection_url):
    return create_engine(connection_url)

@pytest.fixture(scope="function")
def sqlalchemy_declarative_base():
    return BASE

@pytest.fixture(scope="function")
def connection(engine, sqlalchemy_declarative_base):
    if sqlalchemy_declarative_base:
        sqlalchemy_declarative_base.metadata.create_all(engine)
    return engine

@pytest.fixture(scope="function")
def session(connection, sqlalchemy_declarative_base):
    session: Session = sessionmaker()(bind=connection)
    yield session
    session.close()