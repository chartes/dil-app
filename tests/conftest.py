import pytest
from sqlalchemy import create_engine
from api.database import BASE
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


@pytest.fixture(scope="session")
def engine():
    return create_engine("sqlite:///:memory:", connect_args={
        "check_same_thread": False
    })

@pytest.fixture(scope="session")
def tables(engine):
    BASE.metadata.create_all(engine)
    yield
    BASE.metadata.drop_all(engine)

@pytest.fixture(scope="function")
def session(engine, tables):
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()

    yield session

    session.close()
    transaction.rollback()
    connection.close()