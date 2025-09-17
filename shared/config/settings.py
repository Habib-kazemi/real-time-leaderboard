from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    POSTGRES_HOST: str = "postgres"
    POSTGRES_USER: str = "leaderboard"
    POSTGRES_PASSWORD: str = "your_password"
    POSTGRES_DB: str = "leaderboard"
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASSWORD: str = "guest"
    RABBITMQ_HOST: str = "rabbitmq"
    JWT_SECRET: str = "your_jwt_secret"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
