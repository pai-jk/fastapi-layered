from pydantic import BaseModel, Field


class HelloAppBaseDomain(BaseModel):
    message: str = Field(
        description="Message",
        examples=["Hello, AppBaseService!"],
    )
