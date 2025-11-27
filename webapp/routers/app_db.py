"""AppDB 라우터"""

from fastapi import APIRouter, Depends

from src.app_orm_db.service import AppDBService
from webapp.dependency import app_db_service_dependency
from webapp.dto import CreateUserDTO, UpdateUserDTO, UserDTO, UserListDTO

router = APIRouter()


@router.post("/users", response_model=UserDTO, status_code=201)
async def create_user(
    user_data: CreateUserDTO,
    service: AppDBService = Depends(app_db_service_dependency),
) -> UserDTO:
    """User 생성"""
    user_domain = await service.create_user(user_data.name, user_data.email)
    return UserDTO.from_domain(user_domain)


@router.get("/users/{user_id}", response_model=UserDTO)
async def get_user(
    user_id: int,
    service: AppDBService = Depends(app_db_service_dependency),
) -> UserDTO:
    """User 조회"""
    user_domain = await service.get_user(user_id)
    return UserDTO.from_domain(user_domain)


@router.get("/users", response_model=UserListDTO)
async def get_users(
    service: AppDBService = Depends(app_db_service_dependency),
) -> UserListDTO:
    """User 목록 조회"""
    users = await service.get_users()
    total = len(users)
    return UserListDTO.from_domains(users, total)


@router.put("/users/{user_id}", response_model=UserDTO)
async def update_user(
    user_id: int,
    user_data: UpdateUserDTO,
    service: AppDBService = Depends(app_db_service_dependency),
) -> UserDTO:
    """User 수정"""
    user_domain = await service.update_user(user_id, user_data.name, user_data.email)
    return UserDTO.from_domain(user_domain)


@router.delete("/users/{user_id}", status_code=204)
async def delete_user(
    user_id: int,
    service: AppDBService = Depends(app_db_service_dependency),
) -> None:
    """User 삭제"""
    await service.delete_user(user_id)
