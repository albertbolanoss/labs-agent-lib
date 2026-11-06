"""Tests for the shared prompt log writer."""

import json
from pathlib import Path

from labs_agent_lib.observability import PromptLogWriter


class _FakeSettings:
    def __init__(self, tmp_path: Path, observability_enabled: bool = True) -> None:
        self.observability_enabled = observability_enabled
        self.prompt_log_dir = str(tmp_path / "prompt_log")


def _read_lines(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_log_prompt_writes_one_jsonl_line_with_the_expected_fields(tmp_path: Path):
    writer = PromptLogWriter(_FakeSettings(tmp_path), service="talent_distiller_agent")

    writer.log_prompt(
        correlation_id="corr-1",
        agent="coordinator",
        model="model-x",
        system_prompt_name="resume_coordinator_orchestration",
        user_prompt="<resume_path>resume/jane.pdf</resume_path>",
    )

    lines = _read_lines(tmp_path / "prompt_log" / "corr-1.jsonl")
    assert lines[0]["correlation_id"] == "corr-1"
    assert lines[0]["service"] == "talent_distiller_agent"
    assert lines[0]["agent"] == "coordinator"
    assert lines[0]["event"] == "prompt"
    assert lines[0]["attempt"] == 1
    assert "timestamp" in lines[0]


def test_log_prompt_keys_by_agent_when_requested(tmp_path: Path):
    writer = PromptLogWriter(
        _FakeSettings(tmp_path), service="mcp_skills_extractor_agents", key_by_agent=True
    )

    writer.log_prompt(
        correlation_id="corr-2",
        agent="extract_technical_skills",
        model="model-x",
        system_prompt_name="extract_technical_skills",
        user_prompt="a",
        attempt=2,
    )

    lines = _read_lines(tmp_path / "prompt_log" / "corr-2__extract_technical_skills.jsonl")
    assert lines[0]["attempt"] == 2


def test_log_prompt_is_a_noop_when_observability_is_disabled(tmp_path: Path):
    writer = PromptLogWriter(
        _FakeSettings(tmp_path, observability_enabled=False), service="talent_distiller_agent"
    )

    writer.log_prompt(
        correlation_id="corr-3",
        agent="coordinator",
        model="model-x",
        system_prompt_name="x",
        user_prompt="irrelevant",
    )

    assert not (tmp_path / "prompt_log").exists()
