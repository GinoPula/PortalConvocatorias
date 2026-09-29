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
    # Documentacion interactiva de la API (/docs, /redoc, /openapi.json). Cerrada por
    # defecto: cualquiera que encuentre la URL puede ver y hasta probar todos los
    # endpoints, incluidos los de administrador. Se habilita solo con ENABLE_DOCS=true.
    ENABLE_DOCS: bool = os.environ.get("ENABLE_DOCS", "false").lower() == "true"
    # Secreto de Google reCAPTCHA v2, usado para verificar el login. La clave publica
    # (site key) va en el frontend, no aqui. Ver services/recaptcha.py.
    RECAPTCHA_SECRET_KEY: str = os.environ.get("RECAPTCHA_SECRET_KEY", "")
    # reCAPTCHA v3 no tiene casilla: cada intento recibe un puntaje de 0 (bot) a 1
    # (humano). Por debajo de este umbral se rechaza el login.
    RECAPTCHA_MIN_SCORE: float = float(os.environ.get("RECAPTCHA_MIN_SCORE", "0.5"))


settings = Settings()
