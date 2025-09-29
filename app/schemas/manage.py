from app.schemas.base import BaseSchema


class ManageDataResponseItem(BaseSchema):
    name: str
    polled_time: float
    uptime: int | None = None
    cpu_usage: int | None = None
    memory_usage: int | None = None
    disk_usage: int | None = None
    temperature: int | None = None


class ManageDataResponse(BaseSchema):
    data: list[ManageDataResponseItem] = []


class ManageDeleteData(BaseSchema):
    name: str

class ManageDeleteDataResponse(BaseSchema):
    message: str


class ManageConnectData(BaseSchema):
    name: str


class ManageConnectResponse(BaseSchema):
    job_id: str
