from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    secret_key: str
    master_password_hash: str
    session_expire_minutes: int = 60

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


settings = Settings() # type: ignore[call-arg]
