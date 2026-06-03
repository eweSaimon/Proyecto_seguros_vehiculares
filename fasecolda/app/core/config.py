from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Microservicio Fasecolda"
    VERSION: str = "2.0.0"
    DATABASE_URL: str = "sqlite+aiosqlite:///./fasecolda.db"

    class Config:
        env_file = ".env"


settings = Settings()
