import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from api.database import BASE

#@pytest.fixture(scope="function")
#def engine():
#    return create_engine("sqlite:///:memory:")

#@pytest.fixture(scope="function")
#def tables(engine):
#    BASE.metadata.create_all(engine)
#    yield
#    BASE.metadata.drop_all(engine)

@pytest.fixture(scope="session")
def session():
    engine = create_engine("sqlite:///:memory:")
    BASE.metadata.create_all(engine)
    connection = engine.connect()
    transaction = connection.begin()
    session = scoped_session(sessionmaker(bind=connection, autoflush=False, autocommit=False))
    #session = Session()

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