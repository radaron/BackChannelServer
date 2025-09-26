from app.schemas.base import BaseSchema


class OrderResponse(BaseSchema):
    port: int | None = None


class MetricData(BaseSchema):
    uptime: float
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    temperature: float


class MetricResponse(BaseSchema):
    message: str
