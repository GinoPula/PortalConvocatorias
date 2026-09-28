from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from .core.config import settings
from .api import applications, audit, auth, convocations, cv_screening, evaluations, postulant, users

app = FastAPI(
    title="Portal Institucional de Convocatorias y Postulaciones - MVCS",
    docs_url="/docs" if settings.ENABLE_DOCS else None,
    redoc_url="/redoc" if settings.ENABLE_DOCS else None,
    openapi_url="/openapi.json" if settings.ENABLE_DOCS else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    max_age=settings.SESSION_MAX_AGE,
    same_site="lax",
)

app.include_router(auth.router)
app.include_router(convocations.router_public)
app.include_router(convocations.router_admin)
app.include_router(postulant.router)
app.include_router(applications.router_postulante)
app.include_router(applications.router_admin)
app.include_router(evaluations.router)
app.include_router(evaluations.router_ranking)
app.include_router(users.router)
app.include_router(audit.router)
app.include_router(cv_screening.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
