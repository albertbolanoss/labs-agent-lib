"""Shared prompt-log / agent-transcript JSONL writers for Claude-agent-based projects.

Each consuming project supplies its own settings object (just needs
`observability_enabled`, `prompt_log_dir`, `agent_transcript_dir`) and a `service` name;
see `PromptLogWriter`/`AgentTranscriptWriter` for the full contract.
"""

from .agent_transcript import AgentTranscriptWriter
from .prompt_log import PromptLogWriter

__all__ = ["AgentTranscriptWriter", "PromptLogWriter"]
