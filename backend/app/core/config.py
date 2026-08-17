import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    DATABASE_URL: str = os.environ.get(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:postgres@localhost:5432/portal_mvcs",
    )
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "cambiar-esta-clave-en-produccion")
    SESSION_MAX_AGE: int = 60 * 60 * 12  # 12 horas
    OPENAI_API_KEY: str = os.environ.get("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    CORS_ORIGINS: list[str] = [
        o.strip() for o in os.environ.get("CORS_ORIGINS", "").split(",") if o.strip()
    ] or ["http://localhost:5173"]
    STORAGE_PATH: str = os.environ.get("STORAGE_PATH", "/app/storage")


settings = Settings()
