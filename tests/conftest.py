import os

from fastapi.testclient import TestClient
from fastapi_pagination import add_pagination
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker, scoped_session

from api.database import (get_db, BASE)
from api.main import (app)
#from api.database_utils import populate_db_process
from api.config import BASE_DIR, settings
#from api.index_fts.index_utils import (create_index,
#                                       create_store)
#from api.index_conf import st
#from api.index_fts.schemas import PersonIdxSchema

# set up ENV var for testing
os.environ["ENV"] = "test"

WHOOSH_INDEX_DIR = os.path.join(BASE_DIR, settings.WHOOSH_INDEX_DIR)
SQLALCHEMY_DATABASE_TEST_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_TEST_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=True,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

BASE.metadata.create_all(bind=engine)
# add manually the tables

def override_get_db():
    """Override the get_db() dependency with a test database."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db



# populate database from last migration
#create_store(st, WHOOSH_INDEX_DIR)
#create_index(st, PersonIdxSchema)
# add data
# populate_db_process(in_session=local_session)
# populate index
# populate_index(session=local_session, index_=ix, model=Person)
add_pagination(app)
client = TestClient(app)

local_session = TestingSessionLocal()
