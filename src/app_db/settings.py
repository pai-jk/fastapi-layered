from pydantic import Field
from pydantic_settings import BaseSettings


class AppDBSettings(BaseSettings):
    """AppDB 설정"""

    DB_URL: str = Field(
        default="sqlite:///./app_db.db",
        description="SQLite 데이터베이스 URL",
    )

    class Config:
        env_prefix = "APP_DB_"
