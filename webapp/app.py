import logging
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator
from pytz import timezone
from starlette.middleware.cors import CORSMiddleware

from src.exceptions import (
    ClientException,
    ExpiredTokenException,
    ForbiddenException,
    NTSChatbotException,
    NotFoundException,
    RateLimitExceededException,
    ServerException,
)
from webapp.container import ApplicationContainer, create_container
from webapp.dto import ErrorResponseDTO
from webapp.middlewares.elapsed_time import ElapsedTimeMiddleware
from webapp.routers import (
    beta_test,
    chat,
    feedback,
    health,
    manual_data,
    opinion,
    question,
    tax_category,
    video,
)
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
            "http://localhost:5173",
            "http://127.0.0.1:5173",
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
        await app.container.init_resources()  # type: ignore

        # 싱글턴 서비스 프리워밍 및 참조 저장
        app.state.agent_service = app.container.agent().service()  # type: ignore

        try:
            yield
        finally:
            # 종료 시 리소스 정리
            await app.container.llm().chat_model_provider().aclose()  # type: ignore
            await app.container.shutdown_resources()  # type: ignore
            logger.info("Tearing down application")

    app = FastAPI(
        title="NTS Chatbot Server",
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
    app.include_router(chat.router, tags=["chat"])
    app.include_router(question.router, tags=["popular"])
    app.include_router(manual_data.router, tags=["manual-data"])
    app.include_router(tax_category.router, tags=["tax-category"])
    app.include_router(feedback.router, tags=["feedback"])
    app.include_router(video.router, tags=["video"])
    app.include_router(opinion.router, tags=["opinion"])

    # Beta Test TODO
    app.include_router(beta_test.router, tags=["beta-test"])

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(ElapsedTimeMiddleware)

    # 프로메테우스 Metric 설정
    (
        Instrumentator(
            excluded_handlers=[
                "/docs",
                "/redoc",
                "/openapi.json",
                "/metrics",
                "/health",
                "/favicon.ico",
            ],
        )
        .instrument(app)
        .expose(
            app,
            include_in_schema=False,
        )
    )

    @app.exception_handler(ClientException)
    async def client_exception_handler(request: Request, exc: ClientException):
        logger.error(f"Client exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=400,
            content={
                "message": exc.message,
                "code": exc.__class__.__name__,
            },
        )

    @app.exception_handler(ForbiddenException)
    async def forbidden_exception_handler(request: Request, exc: ForbiddenException):
        logger.error(f"Forbidden exception: {exc}", exc_info=True)
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
        logger.error(f"Server exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "message": exc.message,
                "code": exc.__class__.__name__,
            },
        )

    return app
