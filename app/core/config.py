from typing import Optional

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "BackChannel Server"
    app_version: str = "0.1.0"

    secret_key: str = "f91c37fb27be410bbba182ddc776416f"
    master_password_hash: str = (
        "$2b$12$GbY1LhtWYBgVvfQbhprIJeDiZzgF01rA9ikRtQgb08H96/SHu.wJS"
    )
    session_expire_minutes: int = 60  # Session expiration time
    cookie_name: str = "backchannel_session"

    allowed_origins: Optional[str] = "*"

    port_range_start: int = 20000
    port_range_end: int = 30000
    local_address: str = "127.0.0.1"

    model_config = ConfigDict(env_file=".env")


settings = Settings()
