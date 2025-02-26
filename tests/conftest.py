import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.database import BASE

@pytest.fixture()
def engine():
    return create_engine("sqlite:///test.db", connect_args={"check_same_thread": False})

@pytest.fixture()
def tables(engine):
    BASE.metadata.create_all(engine)
    yield
    BASE.metadata.drop_all(engine)

@pytest.fixture()
def session(engine, tables):
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection, autoflush=False, autocommit=False)
    session = Session()


    try:
        yield session
    except Exception as e:
        transaction.rollback()  # Ce rollback sera ignoré si une exception est déjà gérée
        raise
    finally:
        if transaction.is_active:
            transaction.rollback()  # Ne rollback que si actif
        session.close()
        connection.close()