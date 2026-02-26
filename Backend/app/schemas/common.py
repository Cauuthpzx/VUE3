from pydantic import BaseModel, Field


class MessageResponse(BaseModel):
    message: str = Field(description="Thông báo kết quả thao tác")


class HealthResponse(BaseModel):
    status: str = Field(description="Trạng thái hệ thống")
