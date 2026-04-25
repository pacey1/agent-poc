from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")

    grok_api_key: str | None = Field(default=None, alias="GROK_API_KEY")
    grok_model: str = Field(default="grok-3-mini", alias="GROK_MODEL")
    grok_base_url: str = Field(default="https://api.x.ai/v1", alias="GROK_BASE_URL")

    mcp_server_url: str | None = Field(default=None, alias="MCP_SERVER_URL")
    mcp_auth_token: str | None = Field(default=None, alias="MCP_AUTH_TOKEN")

    mock_mode: bool = Field(default=True, alias="MOCK_MODE")


settings = Settings()
