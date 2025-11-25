from fastapi import APIRouter, Depends

from src.app_base.service import AppBaseService
from webapp.dependency import app_base_service_dependency
from webapp.dto import HelloAppBaseDTO

router = APIRouter()


@router.get("/hello-app-base")
async def hello_app_base(
    service: AppBaseService = Depends(app_base_service_dependency),
) -> HelloAppBaseDTO:
    hello_app_base_domain = service.hello()
    return HelloAppBaseDTO.from_domain(hello_app_base_domain)


@router.get("/simulate/client-error")
async def simulate_client_error(
    service: AppBaseService = Depends(app_base_service_dependency),
) -> None:
    service.simulate_error_scenario("client_error")


@router.get("/simulate/forbidden-error")
async def simulate_forbidden_error(
    service: AppBaseService = Depends(app_base_service_dependency),
) -> None:
    service.simulate_error_scenario("forbidden")


@router.get("/simulate/not-found-error")
async def simulate_not_found_error(
    service: AppBaseService = Depends(app_base_service_dependency),
) -> None:
    service.simulate_error_scenario("not_found")


@router.get("/simulate/server-error")
async def simulate_server_error(
    service: AppBaseService = Depends(app_base_service_dependency),
) -> None:
    service.simulate_error_scenario("server_error")


@router.get("/simulate/database-error")
async def simulate_database_error(
    service: AppBaseService = Depends(app_base_service_dependency),
) -> None:
    service.simulate_error_scenario("database_error")


@router.get("/simulate/integrity-error")
async def simulate_integrity_error(
    service: AppBaseService = Depends(app_base_service_dependency),
) -> None:
    service.simulate_error_scenario("integrity_error")


@router.get("/simulate/unknown-error")
async def simulate_unknown_error(
    service: AppBaseService = Depends(app_base_service_dependency),
) -> None:
    service.simulate_error_scenario("unknown")

