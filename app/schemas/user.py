from app.schemas.base import BaseSchema


class LoginRequest(BaseSchema):
    password: str


class LoginResponse(BaseSchema):
    message: str
    authenticated: bool
