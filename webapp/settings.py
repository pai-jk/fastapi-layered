from pydantic import Field
from pydantic_settings import BaseSettings


class ApplicationSettings(BaseSettings):
    APP_ENV: str = Field(default="prod")
    ALLOWED_ORIGINS: str = Field(
        default="*", description="','로 구분된 allowed origins"
    )
