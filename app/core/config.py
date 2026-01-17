from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    secret_key: str
    master_password_hash: str
    session_expire_days: int = 30

    cookie_name: str = "backchannel_session"
    allowed_origins: str

    port_range_start: int = 20000
    port_range_end: int = 20100
    local_address: str = "0.0.0.0"

    custom_messages: str = (
        "Connect: ssh {username}@localhost -p {port},"
        "Dynamic port forward: ssh -D 9999 {username}@localhost -p {port} -t top"
    )

    def get_custom_messages(self) -> list[str]:
        return self.custom_messages.split(",")

    def get_allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",")]


settings = Settings() # type: ignore[call-arg]
