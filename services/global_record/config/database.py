import redis
import psycopg2
from psycopg2.extras import RealDictCursor
from config.settings import settings


def get_redis_client():
    """Return a Redis client instance."""
    return redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        decode_responses=True
    )


def get_postgres_conn():
    """Return a PostgreSQL connection instance."""
    return psycopg2.connect(
        dbname=settings.POSTGRES_DB,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        host=settings.POSTGRES_HOST,
        port=5432,
        cursor_factory=RealDictCursor
    )
