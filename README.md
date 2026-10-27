# labs-agent-lib

Shared utilities extracted from [`candidate-match-agent`](https://github.com/albertbolanoss/candidate-match-agent) for
building Claude-agent-based projects:

- `labs_agent_lib.settings` — a `pydantic-settings` `Settings` model (gateway provider, log level, Portkey/Anthropic
  credentials, prompt-caching toggle).
- `labs_agent_lib.logger` — centralized stderr logging, configured from `Settings.log_level`.
- `labs_agent_lib.file_reader` — extracts plain text from `.pdf`, `.docx`, `.txt`, `.md`, and `.markdown` files.
- `labs_agent_lib.agent_environment` — builds the `ClaudeAgentOptions.env` dict (base URL, API key, custom headers)
  for the configured provider.

## Known limitation (v0.1.0)

This is a first extraction, not yet a fully generic library:

- `Settings` reads environment variables under the `CANDIDATE_MATCH_AGENT_` prefix and still carries
  `candidate-match-agent`-specific fields (`resume_dir`, `resume_poll_interval_seconds`,
  `resume_max_files_per_batch`).
- `logger`'s root logger name is hardcoded to `candidate_match_agent`, so `get_logger(__name__)` only attaches
  the shared handler/level for loggers under that namespace.

Projects other than `candidate-match-agent` can still install and use `file_reader` and `agent_environment` as-is,
but `settings`/`logger` will need the prefix/root-name to be made configurable before they're truly reusable
elsewhere. Tracked as follow-up work.

## Install

```bash
uv add labs-agent-lib
# or
pip install labs-agent-lib
```

## Usage

```python
from labs_agent_lib import get_logger, get_settings, get_agent_environment
from labs_agent_lib.file_reader import extract_text

logger = get_logger(__name__)
settings = get_settings()
env = get_agent_environment(settings)
text = extract_text("resume.pdf")
```

## Development

```bash
uv sync
uv run pytest
```
