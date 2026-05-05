from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")

    llm_provider: str = Field(default="grok", alias="LLM_PROVIDER")
    llm_api_key: str | None = Field(default=None, alias="LLM_API_KEY")
    llm_model: str = Field(default="grok-3-mini", alias="LLM_MODEL")
    llm_base_url: str = Field(default="https://api.x.ai/v1", alias="LLM_BASE_URL")

    # Backward-compatible env values
    grok_api_key: str | None = Field(default=None, alias="GROK_API_KEY")
    grok_model: str = Field(default="grok-3-mini", alias="GROK_MODEL")
    grok_base_url: str = Field(default="https://api.x.ai/v1", alias="GROK_BASE_URL")
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")
    openai_base_url: str = Field(default="https://api.openai.com/v1", alias="OPENAI_BASE_URL")

    confluence_mcp_server_url: str | None = Field(default=None, alias="CONFLUENCE_MCP_SERVER_URL")
    jira_mcp_server_url: str | None = Field(default=None, alias="JIRA_MCP_SERVER_URL")
    github_mcp_server_url: str | None = Field(default=None, alias="GITHUB_MCP_SERVER_URL")
    mcp_auth_token: str | None = Field(default=None, alias="MCP_AUTH_TOKEN")

    mock_mode: bool = Field(default=True, alias="MOCK_MODE")


settings = Settings()
