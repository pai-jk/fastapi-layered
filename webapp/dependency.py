from fastapi import Request
from src.app_base.service import AppBaseService
from src.app_orm_db.service import AppDBService

from webapp.container import ApplicationContainer


def app_base_service_dependency(request: Request) -> AppBaseService:
    """AppBaseService 의존성 주입"""
    container: ApplicationContainer = request.app.container  # type: ignore
    return container.app_base_container.app_base_service()


def app_db_service_dependency(request: Request) -> AppDBService:
    """AppDBService 의존성 주입"""
    container: ApplicationContainer = request.app.container  # type: ignore
    return container.app_db_container.app_db_service()
