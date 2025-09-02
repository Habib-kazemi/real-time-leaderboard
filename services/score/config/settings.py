from os import environ
from dotenv import load_dotenv


load_dotenv()


class Settings:
    """Configuration settings for the application."""
    JWT_SECRET: str = environ.get("JWT_SECRET")
    REDIS_HOST: str = environ.get("REDIS_HOST")
    REDIS_PORT: int = int(environ.get("REDIS_PORT"))
    POSTGRES_HOST: str = environ.get("POSTGRES_HOST")
    POSTGRES_USER: str = environ.get("POSTGRES_USER")
    POSTGRES_PASSWORD: str = environ.get("POSTGRES_PASSWORD")
    POSTGRES_DB: str = environ.get("POSTGRES_DB")


settings = Settings()
