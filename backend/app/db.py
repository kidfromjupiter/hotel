import os
from typing import Optional

from psycopg2.pool import ThreadedConnectionPool

_pool: Optional[ThreadedConnectionPool] = None


def get_pool() -> Optional[ThreadedConnectionPool]:
    global _pool
    if _pool is None:
        dsn = os.environ.get(
            "DATABASE_URL",
            "postgresql://app_user:app_password@localhost:5432/app_db",
        )
        try:
            _pool = ThreadedConnectionPool(minconn=1, maxconn=10, dsn=dsn)
        except Exception:
            _pool = None
    return _pool


def get_db():
    pool = get_pool()
    if pool is None:
        yield None
        return

    connection = None
    try:
        connection = pool.getconn()
        yield connection
        connection.commit()
    except Exception:
        if connection:
            connection.rollback()
        raise
    finally:
        if pool and connection:
            pool.putconn(connection)
