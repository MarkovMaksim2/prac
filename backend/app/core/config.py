from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    MAX_FILES: int = 500
    UPLOAD_DIR: str = "uploads"
    REPORT_DIR: str = "reports"


settings = Settings()