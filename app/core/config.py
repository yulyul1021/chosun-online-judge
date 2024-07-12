from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URL: str = "sqlite:///./coj.db"

    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    SECRET_KEY: str = "3c330b907b36e17beb65996b0810956ffe5303c232f0e892226122fb3bb2c572"

    FIRST_SUPERUSER: str = "ojadmin"
    FIRST_SUPERUSER_PASSWORD: str = "11111111"


settings = Settings()  # type: ignore
