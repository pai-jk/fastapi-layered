from datetime import datetime, timezone
from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from src.app_base.domain import HelloAppBaseDomain
from src.app_orm_db.domain import UserProfile, UserRole


class CamelModel(BaseModel):
    """FastAPI의 모든 Request, Response 모델에 CamelCase를 적용하도록 수정"""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class OkDTO(BaseModel):
    ok: bool = Field(default=True)
    content: Optional[Any] = Field(default=None)


class ExistDTO(BaseModel):
    exist: bool


class ErrorResponseDTO(BaseModel):
    message: str = Field(default="잘못된 요청입니다.", description="에러 메시지")
    code: str = Field(default="InvalidRequestException", description="에러 코드")
    trace_id: str = Field(
        default="c3a5e514e37a96c58e479a7346583a79", description="에러 추적 ID"
    )


class HelloAppBaseDTO(CamelModel):
    message: str = Field(
        description="Message",
        examples=["AppBaseService Not Found"],
    )

    @staticmethod
    def from_domain(domain: HelloAppBaseDomain) -> "HelloAppBaseDTO":
        return HelloAppBaseDTO(
            message=domain.message,
        )


class CreateUserDTO(CamelModel):
    """User 생성 DTO"""

    name: str = Field(
        description="User Name",
        examples=["John Doe"],
        min_length=1,
        max_length=100,
    )
    email: str = Field(
        description="User Email",
        examples=["john.doe@example.com"],
        max_length=255,
    )

    def to_domain(self) -> UserProfile:
        return UserProfile(
            user_id=None,
            user_name=self.name,
            email=self.email,
            roles=[UserRole.USER],
            is_deleted=False,
            created_at=datetime.now(tz=timezone.utc),
            updated_at=datetime.now(tz=timezone.utc),
        )


class UpdateUserDTO(CamelModel):
    """User 수정 DTO"""

    name: Optional[str] = Field(
        default=None,
        description="User Name",
        examples=["John Doe Updated"],
        min_length=1,
        max_length=100,
    )
    email: Optional[str] = Field(
        default=None,
        description="User Email",
        examples=["john.doe.updated@example.com"],
        max_length=255,
    )

    def to_domain(self) -> UserProfile:
        return UserProfile(
            user_id=None,
            user_name=self.name,  # type: ignore
            email=self.email,  # type: ignore
            roles=[UserRole.USER],
            is_deleted=False,
            created_at=datetime.now(tz=timezone.utc),
            updated_at=datetime.now(tz=timezone.utc),
        )


class UserDTO(CamelModel):
    """User 응답 DTO"""

    id: Optional[int] = Field(
        default=None,
        description="User ID",
        examples=[1],
    )
    name: str = Field(
        description="User Name",
        examples=["John Doe"],
    )
    email: Optional[str] = Field(
        default=None,
        description="User Email",
        examples=["john.doe@example.com"],
    )
    # Pydantic v2에서는 alias를 필드 정의에서 직접 사용
    created_at: Optional[datetime] = Field(
        default=None,
        description="생성일시",
        serialization_alias="createdAt",
        validation_alias="createdAt",
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        description="수정일시",
        serialization_alias="updatedAt",
        validation_alias="updatedAt",
    )

    @staticmethod
    def from_domain(domain: UserProfile) -> "UserDTO":
        return UserDTO(
            id=domain.user_id,
            name=domain.user_name,
            email=domain.email,
            created_at=domain.created_at,
            updated_at=domain.updated_at,
        )


class UserListDTO(CamelModel):
    """User 목록 응답 DTO"""

    users: List[UserDTO] = Field(description="User 목록")
    total: int = Field(description="전체 User 수")
    # skip: int = Field(description="건너뛴 수")
    # limit: int = Field(description="제한 수")

    @staticmethod
    def from_domains(domains: List[UserProfile], total: int) -> "UserListDTO":
        return UserListDTO(
            users=[UserDTO.from_domain(domain) for domain in domains], total=total
        )
