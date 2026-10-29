"""Centralized logging setup for the whole app (coordinators, subagent task events, MCP tools).

Usage: `logger = get_logger(__name__)` at module level, then `logger.debug/info/warning/error(...)`.
Verbosity is controlled by AgentSettings.log_level (LABS_RESUME_AGENT_LOG_LEVEL) - set it to DEBUG to
see every step (tool calls, per-task progress) or leave it at INFO to only see the high-level
phases (task started/done, final results). Logs go to stderr, not stdout: mcp_server.py runs as
an MCP stdio subprocess, and anything printed to stdout there would corrupt the MCP protocol.
"""

import logging
import sys

from labs_agent_lib.agent_settings import get_agent_settings

_configured_roots: set[str] = set()


def _configure(root_name: str) -> None:
    if root_name in _configured_roots:
        return
    root = logging.getLogger(root_name)
    root.setLevel(get_agent_settings().log_level.value)
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)-8s %(name)s: %(message)s"))
    root.addHandler(handler)
    root.propagate = False
    _configured_roots.add(root_name)


def get_logger(name: str) -> logging.Logger:
    """Return a logger in the caller's package hierarchy; pass __name__ from the call site.

    The top-level package segment of `name` is configured as its own logging root on first
    use, so each consuming project gets its level/handler without hardcoding its package name.
    """
    _configure(name.split(".", 1)[0])
    return logging.getLogger(name)
