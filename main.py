from contextlib import asynccontextmanager

from fastapi import FastAPI

from core.database import Base, engine, ensure_database_exists
from core.entity_registry import entity_registry
from core.settings import settings


entity_registry.build()


@asynccontextmanager
async def lifespan(_: FastAPI):
    ensure_database_exists()
    if settings.auto_create_tables:
        Base.metadata.create_all(bind=engine)
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="AI-Native JSON CMS", lifespan=lifespan)

    for router in entity_registry.routers:
        app.include_router(router)

    @app.get("/")
    async def root():
        return {
            "message": "AI-Native JSON CMS",
            "entities": list(entity_registry.entities.keys()),
            "tables": sorted(Base.metadata.tables.keys()),
            "docs": "/docs",
        }

    return app


app = create_app()