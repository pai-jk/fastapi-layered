import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

from src.exceptions import (
    ClientException,
    DatabaseException,
    DBIntegrityException,
    ForbiddenException,
    NotFoundException,
    ServerException,
    UnknownException,
)
from webapp.container import ApplicationContainer, create_container
from webapp.dto import ErrorResponseDTO
from webapp.routers import app_base, app_db, app_query_db, health
from webapp.settings import ApplicationSettings

logger = logging.getLogger(__name__)


def create_app(container: ApplicationContainer | None = None) -> FastAPI:
    app_container = container or create_container()
    settings: ApplicationSettings = app_container.settings()
    allowed_origins = settings.ALLOWED_ORIGINS.split(",")

    if settings.APP_ENV == "dev":
        docs_url, redoc_url, openapi_url = "/docs", "/redoc", "/openapi.json"
        allowed_origins += [
            "http://localhost",
            "http://localhost:8000",
            "http://127.0.0.1:8000",
        ]
    else:
        docs_url, redoc_url, openapi_url = None, None, None

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # set up
        logger.info("Setting up application")

        # 컨테이너 바인딩
        app.container = app_container  # type: ignore

        # 비동기 Resource들을 이벤트 루프에서 미리 초기화
        init_result = app_container.init_resources()  # type: ignore
        if init_result is not None:
            await init_result

        # 데이터베이스 테이블 생성
        session_factory = app_container.app_db_container.session_factory()  # type: ignore
        await session_factory.create_database()

        try:
            yield
        finally:
            # 종료 시 리소스 정리
            shutdown_result = app_container.shutdown_resources()  # type: ignore
            if shutdown_result is not None:
                await shutdown_result
            logger.info("Tearing down application")

    app = FastAPI(
        title="FastAPI Layered Architecture Sample",
        lifespan=lifespan,
        root_path="/api",
        generate_unique_id_function=lambda route: route.name,
        responses={
            400: {"model": ErrorResponseDTO},
            500: {"model": ErrorResponseDTO},
        },
        docs_url=docs_url,
        redoc_url=redoc_url,
        openapi_url=openapi_url,
    )

    app.include_router(health.router, tags=["health"])
    app.include_router(app_base.router, tags=["app-base"])
    app.include_router(app_db.router, tags=["app-db"])
    app.include_router(app_query_db.router, tags=["app-query-db"])

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 프로메테우스 Metric 설정
    # from prometheus_fastapi_instrumentator import Instrumentator

    # (
    #     Instrumentator(
    #         excluded_handlers=[
    #             "/docs",
    #             "/redoc",
    #             "/openapi.json",
    #             "/metrics",
    #             "/health",
    #             "/favicon.ico",
    #         ],
    #     )
    #     .instrument(app)
    #     .expose(
    #         app,
    #         include_in_schema=False,
    #     )
    # )

    @app.exception_handler(ClientException)
    async def client_exception_handler(request: Request, exc: ClientException):
        # logger.error(f"Client exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=400,
            content={
                "message": exc.message,
                "code": exc.__class__.__name__,
            },
        )

    @app.exception_handler(ForbiddenException)
    async def forbidden_exception_handler(request: Request, exc: ForbiddenException):
        # logger.error(f"Forbidden exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=403,
            content={
                "message": exc.message,
                "code": exc.__class__.__name__,
            },
        )

    @app.exception_handler(NotFoundException)
    async def not_found_exception_handler(request: Request, exc: NotFoundException):
        logger.error(f"Not found exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=404,
            content={
                "message": exc.message,
                "code": exc.__class__.__name__,
            },
        )

    @app.exception_handler(ServerException)
    async def server_exception_handler(request: Request, exc: ServerException):
        # logger.error(f"Server exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "message": exc.message,
                "code": exc.__class__.__name__,
            },
        )

    @app.exception_handler(DBIntegrityException)
    async def db_integrity_exception_handler(
        request: Request, exc: DBIntegrityException
    ):
        logger.error(f"DB integrity exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=400,
            content={
                "message": exc.message,
                "code": exc.__class__.__name__,
            },
        )

    @app.exception_handler(DatabaseException)
    async def database_exception_handler(request: Request, exc: DatabaseException):
        logger.error(f"Database exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "message": exc.message,
                "code": exc.__class__.__name__,
            },
        )

    @app.exception_handler(UnknownException)
    async def unknown_exception_handler(request: Request, exc: UnknownException):
        # logger.error(f"Unknown exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "message": exc.message,
                "code": exc.__class__.__name__,
            },
        )

    return app
