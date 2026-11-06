"""Tests for the shared agent transcript writer."""

import json
from pathlib import Path

from labs_agent_lib.observability import AgentTranscriptWriter


class _FakeSettings:
    def __init__(self, tmp_path: Path, observability_enabled: bool = True) -> None:
        self.observability_enabled = observability_enabled
        self.agent_transcript_dir = str(tmp_path / "agent_transcript")


def _read_lines(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_session_start_writes_the_system_prompt_once(tmp_path: Path):
    writer = AgentTranscriptWriter(_FakeSettings(tmp_path), service="talent_distiller_agent")

    writer.session_start(
        "corr-1",
        "coordinator",
        model="model-x",
        system_prompt="You are a coordinator.",
        user_prompt="<resume_path>resume/jane.pdf</resume_path>",
        allowed_tools=["mcp__candidate-skill-agent-technical__extract_technical_skills"],
    )

    lines = _read_lines(tmp_path / "agent_transcript" / "corr-1.jsonl")
    event = lines[0]
    assert event["event"] == "session_start"
    assert event["allowed_tools"] == ["mcp__candidate-skill-agent-technical__extract_technical_skills"]
    assert event["session_id"] is None


def test_session_start_without_allowed_tools_writes_none(tmp_path: Path):
    writer = AgentTranscriptWriter(_FakeSettings(tmp_path), service="mcp_skills_extractor_agents")

    writer.session_start(
        "corr-1b", "extract_technical_skills", model="model-x", system_prompt="x", user_prompt="x"
    )

    lines = _read_lines(tmp_path / "agent_transcript" / "corr-1b.jsonl")
    assert lines[0]["allowed_tools"] is None


def test_assistant_text_writes_the_text_and_session_id(tmp_path: Path):
    writer = AgentTranscriptWriter(_FakeSettings(tmp_path), service="talent_distiller_agent")

    writer.assistant_text("corr-2", "coordinator", text="DONE", session_id="session-1")

    lines = _read_lines(tmp_path / "agent_transcript" / "corr-2.jsonl")
    assert lines[0]["text"] == "DONE"
    assert lines[0]["session_id"] == "session-1"


def test_tool_use_writes_the_dispatched_tool_call(tmp_path: Path):
    writer = AgentTranscriptWriter(_FakeSettings(tmp_path), service="talent_distiller_agent")

    writer.tool_use(
        "corr-3",
        "coordinator",
        tool_use_id="tool-1",
        tool_name="mcp__candidate-skill-agent-technical__extract_technical_skills",
        target_field="technical_skills",
        tool_input={"content": "..."},
    )

    lines = _read_lines(tmp_path / "agent_transcript" / "corr-3.jsonl")
    assert lines[0]["event"] == "tool_use"
    assert lines[0]["tool_use_id"] == "tool-1"


def test_tool_result_writes_the_returned_output(tmp_path: Path):
    writer = AgentTranscriptWriter(_FakeSettings(tmp_path), service="talent_distiller_agent")

    writer.tool_result(
        "corr-4",
        "coordinator",
        tool_use_id="tool-1",
        tool_name="mcp__candidate-skill-agent-technical__extract_technical_skills",
        target_field="technical_skills",
        is_error=False,
        output='[{"skill": "Python"}]',
    )

    lines = _read_lines(tmp_path / "agent_transcript" / "corr-4.jsonl")
    assert lines[0]["event"] == "tool_result"
    assert lines[0]["output"] == '[{"skill": "Python"}]'


def test_retry_writes_the_validation_error(tmp_path: Path):
    writer = AgentTranscriptWriter(
        _FakeSettings(tmp_path), service="mcp_skills_extractor_agents", key_by_agent=True
    )

    writer.retry("corr-5", "extract_certifications", attempt=1, attempts=3, error="invalid JSON")

    lines = _read_lines(tmp_path / "agent_transcript" / "corr-5__extract_certifications.jsonl")
    assert lines[0]["event"] == "retry"
    assert lines[0]["error"] == "invalid JSON"


def test_session_end_writes_the_successful_outcome_with_a_session_id(tmp_path: Path):
    writer = AgentTranscriptWriter(_FakeSettings(tmp_path), service="talent_distiller_agent")

    writer.session_end("corr-6", "coordinator", is_error=False, session_id="session-1", stop_reason="end_turn")

    lines = _read_lines(tmp_path / "agent_transcript" / "corr-6.jsonl")
    assert lines[0]["is_error"] is False
    assert lines[0]["session_id"] == "session-1"
    assert lines[0]["stop_reason"] == "end_turn"
    assert lines[0]["result"] is None
    assert lines[0]["error"] is None


def test_session_end_writes_the_failure_result_and_error(tmp_path: Path):
    writer = AgentTranscriptWriter(
        _FakeSettings(tmp_path), service="mcp_skills_extractor_agents", key_by_agent=True
    )

    writer.session_end(
        "corr-7", "extract_languages", is_error=True, error="agent failed after 3 attempts"
    )

    lines = _read_lines(tmp_path / "agent_transcript" / "corr-7__extract_languages.jsonl")
    assert lines[0]["is_error"] is True
    assert lines[0]["error"] == "agent failed after 3 attempts"
    assert lines[0]["session_id"] is None


def test_events_for_the_same_correlation_id_append_in_order(tmp_path: Path):
    writer = AgentTranscriptWriter(_FakeSettings(tmp_path), service="talent_distiller_agent")

    writer.assistant_text("corr-8", "coordinator", text="first")
    writer.assistant_text("corr-8", "coordinator", text="second")

    lines = _read_lines(tmp_path / "agent_transcript" / "corr-8.jsonl")
    assert [line["text"] for line in lines] == ["first", "second"]


def test_every_event_is_a_noop_when_observability_is_disabled(tmp_path: Path):
    writer = AgentTranscriptWriter(
        _FakeSettings(tmp_path, observability_enabled=False), service="talent_distiller_agent"
    )

    writer.session_start(
        "corr-9", "coordinator", model="x", system_prompt="x", user_prompt="x", allowed_tools=[]
    )
    writer.assistant_text("corr-9", "coordinator", text="x")
    writer.tool_use(
        "corr-9", "coordinator", tool_use_id="x", tool_name="x", target_field="x", tool_input={}
    )
    writer.tool_result(
        "corr-9", "coordinator", tool_use_id="x", tool_name="x", target_field="x", is_error=False, output="x"
    )
    writer.retry("corr-9", "coordinator", attempt=1, attempts=1, error="x")
    writer.session_end("corr-9", "coordinator", is_error=False)

    assert not (tmp_path / "agent_transcript").exists()
