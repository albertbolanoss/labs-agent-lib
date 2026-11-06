"""Prompt log: one audit line per outbound LLM request attempt - "what we asked the model".

Complements the agent transcript (the full play-by-play of a session). The prompt log is
a flat, append-only index meant for quick search/filtering across runs; see a consuming
project's `documentation/prompt_log_and_agent_transcript.md` for the full design and how
`correlation_id` ties multiple services together.
"""

from typing import Any

from ._jsonl_writer import append_jsonl, file_stem_for, utc_now_iso


class PromptLogWriter:
    """Appends one line per LLM call attempt to `{prompt_log_dir}/{file_stem}.jsonl`.

    `settings` only needs `observability_enabled: bool` and `prompt_log_dir: str`
    attributes - any project's own settings object works, no shared schema required.
    `service` names the calling project in every record (e.g. `"talent_distiller_agent"`).
    Pass `key_by_agent=True` when multiple agents can log under the same `correlation_id`
    concurrently, so each gets its own file instead of interleaving writes.
    """

    def __init__(self, settings: Any, *, service: str, key_by_agent: bool = False) -> None:
        self.settings = settings
        self.service = service
        self.key_by_agent = key_by_agent

    def log_prompt(
        self,
        *,
        correlation_id: str,
        agent: str,
        model: str,
        system_prompt_name: str,
        user_prompt: str,
        attempt: int = 1,
    ) -> None:
        """Records one outbound prompt. No-ops when `settings.observability_enabled` is `False`."""
        if not self.settings.observability_enabled:
            return

        record: dict[str, Any] = {
            "timestamp": utc_now_iso(),
            "correlation_id": correlation_id,
            "service": self.service,
            "agent": agent,
            "event": "prompt",
            "model": model,
            "system_prompt_name": system_prompt_name,
            "user_prompt": user_prompt,
            "attempt": attempt,
        }
        file_stem = file_stem_for(correlation_id, agent if self.key_by_agent else None)
        append_jsonl(self.settings.prompt_log_dir, file_stem, record)
