from __future__ import annotations

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.config import settings
from app.constants import APP_VERSION
from app.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger = setup_logging(level=settings.app_log_level, logger_name="aiclip")
    app.state.logger = logger

    logger.info(
        "Application startup",
        extra={
            "app_name": settings.app_name,
            "environment": settings.app_env,
            "debug": settings.app_debug,
        },
    )
    yield
    logger.info("Application shutdown")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=APP_VERSION,
        description="AI Campaign Clip Workflow API",
        debug=settings.app_debug,
        lifespan=lifespan,
    )

    app.include_router(api_router, prefix=settings.api_prefix)

    @app.get("/", tags=["system"])
    async def root() -> JSONResponse:
        return JSONResponse(
            content={
                "message": f"{settings.app_name} API is running",
                "docs": "/docs",
                "health": "/health",
                "api_prefix": settings.api_prefix,
            }
        )

    @app.get("/health", tags=["system"])
    async def health_check() -> JSONResponse:
        return JSONResponse(
            content={
                "status": "ok",
                "service": settings.app_name,
                "version": APP_VERSION,
                "environment": settings.app_env,
            }
        )

    return app


def run() -> None:
    """Executable helper for `project.scripts` entrypoint."""
    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_debug,
        log_level=settings.app_log_level.lower(),
    )


app = create_app()


if __name__ == "__main__":
    run()
