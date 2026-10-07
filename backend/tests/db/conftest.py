import pytest
from app.db import get_db  # Adjust the import path if needed


@pytest.fixture
def db_connection():
    db_generator = get_db()
    connection = next(db_generator)

    try:
        yield connection
    finally:
        connection.rollback()
        db_generator.close()
