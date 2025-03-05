import pytest
from sqlalchemy import create_engine
from api.database import BASE
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

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
    from api.models.models import (City,
                                   Person,
                                   Patent,
                                   Address,
                                   User,
                                   PersonHasAddresses,
                                   PatentHasAddresses,
                                   Image,
                                   PatentHasImages,)

    City.metadata.create_all(engine)
    Person.metadata.create_all(engine)
    Patent.metadata.create_all(engine)
    Address.metadata.create_all(engine)
    User.metadata.create_all(engine)
    PersonHasAddresses.metadata.create_all(engine)
    PatentHasAddresses.metadata.create_all(engine)
    Image.metadata.create_all(engine)
    PatentHasImages.metadata.create_all(engine)

    if not engine.url.get_backend_name() == "sqlite":
        raise RuntimeError('Use SQLite backend to run tests')

    #Base.metadata.create_all(engine)
    try:
        with Session() as session:
            yield session
    finally:
        City.metadata.drop_all(engine)
        Person.metadata.drop_all(engine)
        Patent.metadata.drop_all(engine)
        Address.metadata.drop_all(engine)
        User.metadata.drop_all(engine)
        PersonHasAddresses.metadata.drop_all(engine)
        PatentHasAddresses.metadata.drop_all(engine)
        Image.metadata.drop_all(engine)
        PatentHasImages.metadata.drop_all(engine)

        #Base.metadata.drop_all(engine)
