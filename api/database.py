"""
database.py

Database connection and session management.
"""

import os

from sqlalchemy import create_engine
#from sqlalchemy.or.declarative import declarative_base
from sqlalchemy.orm import (sessionmaker,
                            scoped_session,
                            declarative_base)

#from whoosh import index

from api.config import BASE_DIR, settings

SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, settings.DB_URI)}"
#WHOOSH_INDEX_DIR = os.path.join(BASE_DIR, settings.WHOOSH_INDEX_DIR)

engine = create_engine(
    SQLALCHEMY_DATABASE_URI,
    # needed for sqlite
    connect_args={'check_same_thread': False},
    pool_size=20,
    max_overflow=0,
    pool_timeout=300,
    pool_recycle=3600,
    echo=bool(settings.DB_ECHO)
)



session = scoped_session(sessionmaker(engine, autocommit=False, autoflush=False))
BASE = declarative_base()

# Dependency for FastAPI endpoints
# to get a database connection.
def get_db() -> scoped_session:
    """
    Get a database connection.
    :return: scoped_session
    :rtype: scoped_session
    """
    db = session
    try:
        yield db
    finally:
        db.close()
