from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60       # default: 1 hour
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7          # default: 7 days

    class Config:
        env_file = ".env"


settings = Settings()
