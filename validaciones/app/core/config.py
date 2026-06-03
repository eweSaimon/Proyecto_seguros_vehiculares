from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Microservicio de Validaciones"
    VERSION: str = "3.0.0"
    DATABASE_URL: str = "sqlite+aiosqlite:///./validaciones.db"
    FASECOLDA_URL: str = "http://localhost:8001"

    # Reglas de puntuación (enunciado)
    PUNTOS_LATAS:   int = 100
    PUNTOS_HERIDOS: int = 200
    PUNTOS_MUERTOS: int = 300
    UMBRAL_RECHAZO: int = 400

    class Config:
        env_file = ".env"


settings = Settings()
