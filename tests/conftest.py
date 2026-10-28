"""Shared fixtures for tests of libs/agent_settings.py and libs/logger.py."""

import pytest

from labs_agent_lib.agent_settings import get_settings

_SETTINGS_ENV_KEYS = [
    "LABS_AGENT_LIB_PROVIDER",
    "LABS_AGENT_LIB_LOG_LEVEL",
    "LABS_AGENT_LIB_PORTKEY_BASE_URL",
    "LABS_AGENT_LIB_PORTKEY_API_KEY",
    "LABS_AGENT_LIB_ANTHROPIC_BASE_URL",
    "LABS_AGENT_LIB_ANTHROPIC_API_KEY",
]


@pytest.fixture(autouse=True)
def _isolated_settings(monkeypatch: pytest.MonkeyPatch):
    """Make Settings()/get_settings() deterministic in tests.

    Clears ambient LABS_AGENT_LIB_* env vars (a developer's shell or the
    real .env file could otherwise leak into assertions) and resets the
    get_settings() cache so each test starts from a clean singleton.
    """
    for key in _SETTINGS_ENV_KEYS:
        monkeypatch.delenv(key, raising=False)
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
