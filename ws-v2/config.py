import os

from pydantic import BaseSettings


class Settings(BaseSettings):
    db_url: str

    class Config:
        env_file = os.environ.get("ENV_FILE", ".env")


settings = Settings()
