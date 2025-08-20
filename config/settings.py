from os import environ


class Settings:
    """Configuration settings for the application."""
    JWT_SECRET: str = environ.get("JWT_SECRET", "your-secret-key")
    REDIS_HOST: str = environ.get("REDIS_HOST", "redis")
    REDIS_PORT: int = int(environ.get("REDIS_PORT", 6379))
    POSTGRES_HOST: str = environ.get("POSTGRES_HOST", "postgres")
    POSTGRES_USER: str = environ.get("POSTGRES_USER", "leaderboard")
    POSTGRES_PASSWORD: str = environ.get("POSTGRES_PASSWORD", "ppassword")
    POSTGRES_DB: str = environ.get("POSTGRES_DB", "leaderboard_db")


settings = Settings()
