import mysql.connector
from mysql.connector import pooling
from contextlib import contextmanager
from config import Config
import logging

logger = logging.getLogger(__name__)

connection_pool = pooling.MySQLConnectionPool(
    pool_name="inventory_pool",
    pool_size=5,
    host=Config.DB_HOST,
    port=Config.DB_PORT,
    database=Config.DB_NAME,
    user=Config.DB_USER,
    password=Config.DB_PASSWORD,
    autocommit=False,
)

@contextmanager
def get_db():
    conn = connection_pool.get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        yield conn, cursor
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"DB error, rolling back: {e}")
        raise
    finally:
        cursor.close()
        conn.close()