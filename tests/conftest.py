import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.models.models import *
from api.database import BASE


"""
@pytest.fixture(scope="session")
def engine():
    return create_engine("sqlite:///:memory:", connect_args={
        "check_same_thread": False
    })  # Ou utiliser un fichier

@pytest.fixture(scope="session")
def tables(engine):
    BASE.metadata.create_all(engine)  # Crée les tables avant les tests
    yield
    BASE.metadata.drop_all(engine)  # Nettoyage après les tests

@pytest.fixture(scope="function")
def session(engine, tables):
    Session propre par test
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()

    yield session

    session.close()
    transaction.rollback()  # Annule tout après le test
    connection.close()
"""

@pytest.fixture(scope="function")
def session():
    engine = create_engine("sqlite:///:memory:", connect_args={
        "check_same_thread": False
    })
    Session = sessionmaker(bind=engine, expire_on_commit=False)
    if not engine.url.get_backend_name() == "sqlite":
        raise RuntimeError('Use SQLite backend to run tests')

    BASE.metadata.create_all(engine)
    try:
        with Session() as session:
            yield session
    finally:
        BASE.metadata.drop_all(engine)
