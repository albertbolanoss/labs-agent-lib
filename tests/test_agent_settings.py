import pytest

from labs_agent_lib.agent_settings import AgentSettings, LogLevel, Provider, get_agent_settings


def test_provider_values():
    assert Provider.PORTKEY == "portkey"
    assert Provider.ANTHROPIC == "anthropic"


def test_log_level_values():
    assert LogLevel.DEBUG == "DEBUG"
    assert LogLevel.INFO == "INFO"
    assert LogLevel.WARNING == "WARNING"
    assert LogLevel.ERROR == "ERROR"


def test_defaults_when_no_env_vars_are_set():
    settings = AgentSettings(_env_file=None)

    assert settings.provider is Provider.PORTKEY
    assert settings.log_level is LogLevel.INFO
    assert settings.portkey_base_url == "https://portkeygateway.perficient.com"
    assert settings.anthropic_base_url == "https://api.anthropic.com"
    assert settings.portkey_api_key.get_secret_value() == ""
    assert settings.anthropic_api_key.get_secret_value() == ""


def test_reads_provider_and_log_level_from_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("LABS_AGENT_LIB_PROVIDER", "anthropic")
    monkeypatch.setenv("LABS_AGENT_LIB_LOG_LEVEL", "DEBUG")

    settings = AgentSettings(_env_file=None)

    assert settings.provider is Provider.ANTHROPIC
    assert settings.log_level is LogLevel.DEBUG


def test_reads_base_urls_and_api_keys_from_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("LABS_AGENT_LIB_PORTKEY_BASE_URL", "https://portkey.example.com")
    monkeypatch.setenv("LABS_AGENT_LIB_PORTKEY_API_KEY", "portkey-secret")
    monkeypatch.setenv("LABS_AGENT_LIB_ANTHROPIC_BASE_URL", "https://anthropic.example.com")
    monkeypatch.setenv("LABS_AGENT_LIB_ANTHROPIC_API_KEY", "anthropic-secret")

    settings = AgentSettings(_env_file=None)

    assert settings.portkey_base_url == "https://portkey.example.com"
    assert settings.portkey_api_key.get_secret_value() == "portkey-secret"
    assert settings.anthropic_base_url == "https://anthropic.example.com"
    assert settings.anthropic_api_key.get_secret_value() == "anthropic-secret"


def test_api_keys_are_masked_in_str_and_repr(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("LABS_AGENT_LIB_PORTKEY_API_KEY", "super-secret")

    settings = AgentSettings(_env_file=None)

    assert "super-secret" not in str(settings.portkey_api_key)
    assert "super-secret" not in repr(settings)


def test_unknown_env_vars_with_the_app_prefix_are_ignored(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("LABS_AGENT_LIB_SOME_UNKNOWN_FIELD", "whatever")

    settings = AgentSettings(_env_file=None)  # must not raise

    assert settings.provider is Provider.PORTKEY


def test_get_agent_settings_returns_an_agent_settings_instance(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("LABS_AGENT_LIB_PROVIDER", "anthropic")

    settings = get_agent_settings()

    assert isinstance(settings, AgentSettings)
    assert settings.provider is Provider.ANTHROPIC


def test_get_agent_settings_is_cached_across_calls(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("LABS_AGENT_LIB_PROVIDER", "anthropic")
    first = get_agent_settings()

    monkeypatch.setenv("LABS_AGENT_LIB_PROVIDER", "portkey")
    second = get_agent_settings()

    assert first is second
    assert second.provider is Provider.ANTHROPIC
