from datetime import timedelta
from typing import Optional

from fastapi import HTTPException, status
from fastapi_login import LoginManager
from fastapi_login.exceptions import InvalidCredentialsException
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

manager = LoginManager(
    settings.secret_key,
    token_url="/api/v1/auth/login",
    use_cookie=True,
    cookie_name=settings.cookie_name,
)


class User:
    def __init__(self, username: str = "admin"):
        self.username = username
        self.id = username

    def __repr__(self):
        return f"User(username='{self.username}')"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


@manager.user_loader()
def load_user(username: str) -> Optional[User]:
    """Load user for authentication - only allow admin user"""
    if username == "admin":
        return User(username)
    return None


def verify_master_password(password: str) -> bool:
    return verify_password(password, settings.master_password_hash)


def authenticate_user(password: str) -> Optional[User]:
    if verify_master_password(password):
        return User("admin")
    return None


def create_access_token(username: str) -> str:
    return manager.create_access_token(
        data={"sub": username},
        expires=timedelta(minutes=settings.session_expire_minutes),
    )


def get_current_user_from_cookie(token: str = None):
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    try:
        user = manager.get_current_user(token)
        return user
    except InvalidCredentialsException as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        ) from exc
