from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://indexer:indexer@localhost:5432/indexer"
    redis_url: str = "redis://localhost:6379/0"
    cors_origins: str = "http://localhost:5173"

settings = Settings()
