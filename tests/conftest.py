"""conftest.py

File that pytest automatically looks for in any directory.
"""
import os
import pytest
import asyncio

from fastapi import Depends
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from api.database import BASE, get_db
from api.main import app
from api.config import BASE_DIR, settings

# Set up ENV var for testing
os.environ["ENV"] = "test"

WHOOSH_INDEX_DIR = os.path.join(BASE_DIR, settings.WHOOSH_INDEX_DIR)
SQLALCHEMY_DATABASE_TEST_URL = "sqlite+aiosqlite:///./test.db"

# Create an async engine for tests
engine = create_async_engine(
    SQLALCHEMY_DATABASE_TEST_URL,
    echo=False,
    connect_args={"check_same_thread": False},
)

# Create an async session factory
TestingSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)


@pytest.fixture(scope="function")
async def db_session() -> AsyncSession:
    """Create a new database session and clean up after the test."""
    async with engine.begin() as conn:
        await conn.run_sync(BASE.metadata.drop_all)  # Clean the DB before each test
        await conn.run_sync(BASE.metadata.create_all)  # Recreate fresh tables

    async with TestingSessionLocal() as session:
        yield session  # Provide the session to the test
        await session.rollback()


@pytest.fixture(scope="function")
async def session_test(db_session: AsyncSession):
    """Create a test client that overrides the database session."""

    async def override_get_db():
        async with db_session as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
