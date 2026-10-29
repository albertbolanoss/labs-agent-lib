"""Application settings for projects built on labs-agent-lib.

Consuming projects configure this via a `.env` file (or real env vars) at their own
repository root, prefixing every key with `LABS_AGENT_LIB_`, e.g.:

    LABS_AGENT_LIB_PROVIDER=anthropic
    LABS_AGENT_LIB_LOG_LEVEL=DEBUG
    LABS_AGENT_LIB_ANTHROPIC_API_KEY=sk-ant-...

Call `get_agent_settings()` to get the cached singleton instead of instantiating
`AgentSettings` directly, so the `.env` file is only read once per process.
"""

from enum import StrEnum
from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Provider(StrEnum):
    """Anthropic-Messages-API-compatible gateways this agent can route through."""

    PORTKEY = "portkey"
    ANTHROPIC = "anthropic"


class LogLevel(StrEnum):
    """Verbosity for labs_resume_agent.libs.logger - maps 1:1 to stdlib logging levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class AgentSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="LABS_AGENT_LIB_",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    provider: Provider = Provider.PORTKEY
    log_level: LogLevel = LogLevel.INFO

    portkey_base_url: str = "https://portkeygateway.perficient.com"
    portkey_api_key: SecretStr = SecretStr("")
    portkey_virtual: str = ""
    
    anthropic_base_url: str = "https://api.anthropic.com"
    anthropic_api_key: SecretStr = SecretStr("")

    disable_prompt_caching: bool = False


@lru_cache
def get_agent_settings() -> AgentSettings:
    """Return the cached application settings singleton."""
    return AgentSettings()
