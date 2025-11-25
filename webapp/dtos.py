from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from src.app1.domains import App1


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


class RequestDTO(BaseModel):
    id: int = Field(description="ID", examples=[1])
    contents: str = Field(
        description="Contents",
        examples=["Hello, world!"],
    )

    @staticmethod
    def from_domain(domain: RequestDomain) -> "RequestDTO":
        return RequestDTO(
            id=domain.id,
            name=domain.content,
        )


class ResponseDTO(CamelModel):
    id: str = Field(description="ID")
    contents: str = Field(
        description="Contents",
        examples=["Hello, world!"],
    )

    @staticmethod
    def from_domain(domain: ResponseDomain) -> "ResponseDTO":
        return ResponseDTO(
            id=domain.id,
            contents=domain.content,
        )
