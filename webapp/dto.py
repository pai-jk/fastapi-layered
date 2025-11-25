from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from src.app_base.domain import HelloAppBaseDomain


class CamelModel(BaseModel):
    """FastAPI의 모든 Request, Response 모델에 CamelCase를 적용하도록 수정"""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class OkDTO(BaseModel):
    ok: bool = Field(default=True)


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
