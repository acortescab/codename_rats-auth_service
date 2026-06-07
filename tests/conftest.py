import pytest

from app.main import app as fastapi_app
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.session import engine_writer
from sqlalchemy import text
from sqlalchemy.orm import Session

@pytest.fixture
def anyio_backend():
    return "asyncio"

@pytest.fixture
async def async_client():
    """
    Provides an async HTTP client for FastAPI tests.
    """
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test"
    ) as client:
        yield client

@pytest.fixture
def db_connection():
    """
    Creates a DB connection with rollback
    """
    connection = engine_writer.connect()
    transaction = connection.begin()

    yield connection

    transaction.rollback()
    connection.close()

@pytest.fixture
def db_session_writer(db_connection):
    """
    Creates the session writer
    """
    return Session(bind=db_connection)

@pytest.fixture
def db_session_reader(db_connection):
    """
    Creates the session reader
    """
    return Session(bind=db_connection)

@pytest.fixture(autouse=True)
def clean_db():
    """
    Clear db for tests
    """
    yield

    with engine_writer.connect() as conn:
        conn.execute(text("""
            TRUNCATE TABLE
                refresh_tokens,
                players
            RESTART IDENTITY CASCADE;
        """))
        conn.commit()


@pytest.fixture
def get_app():
    return fastapi_app