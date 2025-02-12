import pytest
from playwright.sync_api import sync_playwright
from pytest_base_url.plugin import base_url
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.database import BASE
import subprocess
import time
import requests

@pytest.fixture(scope="module")
def engine():
    return create_engine("sqlite:///:memory:")


@pytest.fixture(scope="module")
def flask_server():
    """Lance le serveur Flask en arrière-plan."""
    #env = os.environ.copy()
    #env["FLASK_APP"] = FLASK_APP_PATH

    # Lance le serveur Flask
    #process = subprocess.Popen(["./run.sh", "dev"], cwd="..", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # uvicorn api.main:app --host $HOST --port $PORT --reload into process
    process = subprocess.Popen(["uvicorn", "api.main:app", "--host", "localhost", "--port", "8888", "--reload"], cwd="..", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    augment_time = 0
    yield  # Le test démarre ici

    # Arrête le serveur Flask à la fin
    process.terminate()
    process.wait()

@pytest.fixture(scope="function")
def page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(base_url="http://localhost:8888")
        page = ctx.new_page()
        yield page
        browser.close()


@pytest.fixture(scope="module")
def tables(engine):
    BASE.metadata.create_all(engine)
    yield
    BASE.metadata.drop_all(engine)

@pytest.fixture(scope="function")
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