"""Agent transcript: the full, ordered play-by-play of one agent session or tool call.

Complements the prompt log (a flat index of what was asked). See a consuming project's
`documentation/prompt_log_and_agent_transcript.md` for the full design and how
`correlation_id` ties multiple services together.
"""

from typing import Any

from ._jsonl_writer import append_jsonl, file_stem_for, utc_now_iso


class AgentTranscriptWriter:
    """Appends one event line per step of an agent run to `{agent_transcript_dir}/{file_stem}.jsonl`.

    `settings` only needs `observability_enabled: bool` and `agent_transcript_dir: str`
    attributes - any project's own settings object works, no shared schema required.
    `service` names the calling project in every record (e.g. `"mcp_skills_extractor_agents"`).
    Pass `key_by_agent=True` when multiple agents can write under the same
    `correlation_id` concurrently, so each gets its own file instead of interleaving
    writes - e.g. several extraction sub-agents fanned out in parallel by a coordinator.

    Methods cover the union of events either a coordinator (`session_start`,
    `assistant_text`, `tool_use`, `tool_result`, `session_end`) or a self-correcting
    sub-agent (`session_start`, `assistant_text`, `retry`, `session_end`) needs. Callers
    only use the subset that applies to them.
    """

    def __init__(self, settings: Any, *, service: str, key_by_agent: bool = False) -> None:
        self.settings = settings
        self.service = service
        self.key_by_agent = key_by_agent

    def _write(
        self,
        correlation_id: str,
        agent: str,
        event: str,
        *,
        session_id: str | None = None,
        **fields: Any,
    ) -> None:
        if not self.settings.observability_enabled:
            return

        record: dict[str, Any] = {
            "timestamp": utc_now_iso(),
            "correlation_id": correlation_id,
            "service": self.service,
            "agent": agent,
            "session_id": session_id,
            "event": event,
            **fields,
        }
        file_stem = file_stem_for(correlation_id, agent if self.key_by_agent else None)
        append_jsonl(self.settings.agent_transcript_dir, file_stem, record)

    def session_start(
        self,
        correlation_id: str,
        agent: str,
        *,
        model: str,
        system_prompt: str,
        user_prompt: str,
        allowed_tools: list[str] | None = None,
    ) -> None:
        """Records the opening of a session/first attempt, including the system prompt once."""
        self._write(
            correlation_id,
            agent,
            "session_start",
            model=model,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            allowed_tools=list(allowed_tools) if allowed_tools is not None else None,
        )

    def assistant_text(
        self,
        correlation_id: str,
        agent: str,
        *,
        text: str,
        session_id: str | None = None,
    ) -> None:
        """Records a text block/raw response the agent emitted."""
        self._write(correlation_id, agent, "assistant_text", text=text, session_id=session_id)

    def tool_use(
        self,
        correlation_id: str,
        agent: str,
        *,
        tool_use_id: str,
        tool_name: str,
        target_field: str,
        tool_input: Any,
    ) -> None:
        """Records a tool call the agent dispatched."""
        self._write(
            correlation_id,
            agent,
            "tool_use",
            tool_use_id=tool_use_id,
            tool_name=tool_name,
            target_field=target_field,
            tool_input=tool_input,
        )

    def tool_result(
        self,
        correlation_id: str,
        agent: str,
        *,
        tool_use_id: str,
        tool_name: str,
        target_field: str,
        is_error: bool,
        output: str,
    ) -> None:
        """Records the result that came back for a previously dispatched tool call."""
        self._write(
            correlation_id,
            agent,
            "tool_result",
            tool_use_id=tool_use_id,
            tool_name=tool_name,
            target_field=target_field,
            is_error=is_error,
            output=output,
        )

    def retry(self, correlation_id: str, agent: str, *, attempt: int, attempts: int, error: str) -> None:
        """Records a self-correction turn triggered by a schema/validation failure."""
        self._write(correlation_id, agent, "retry", attempt=attempt, attempts=attempts, error=error)

    def session_end(
        self,
        correlation_id: str,
        agent: str,
        *,
        is_error: bool,
        session_id: str | None = None,
        stop_reason: str | None = None,
        result: Any = None,
        error: str | None = None,
    ) -> None:
        """Records the final outcome of the session/tool call."""
        self._write(
            correlation_id,
            agent,
            "session_end",
            session_id=session_id,
            stop_reason=stop_reason,
            is_error=is_error,
            result=result,
            error=error,
        )
