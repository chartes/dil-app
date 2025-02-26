import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.database import BASE



@pytest.fixture(scope="function")
def session():
    engine = create_engine("sqlite:///:memory:",
                  echo=False,
                  connect_args={'check_same_thread': False})
    BASE.metadata.create_all(engine)
    #BASE.metadata.drop_all(engine)
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