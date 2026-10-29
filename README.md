# labs-agent-lib

Shared utilities extracted from [`candidate-match-agent`](https://github.com/albertbolanoss/candidate-match-agent) for
building Claude-agent-based projects:

- `labs_agent_lib.agent_settings` — a `pydantic-settings` `AgentSettings` model (gateway provider, log level, Portkey/Anthropic
  credentials, prompt-caching toggle).
- `labs_agent_lib.logger` — centralized stderr logging, configured from `AgentSettings.log_level`.
- `labs_agent_lib.file_reader` — extracts plain text from `.pdf`, `.docx`, `.txt`, `.md`, and `.markdown` files.
- `labs_agent_lib.agent_environment` — builds the `ClaudeAgentOptions.env` dict (base URL, API key, custom headers)
  for the configured provider.

## Install

```bash
uv add labs-agent-lib
# or
pip install labs-agent-lib
```

## Configuration

`AgentSettings` reads from your project's own `.env` file (or real environment variables), with every key
prefixed `LABS_AGENT_LIB_`:

| Env var | Default | Description |
| --- | --- | --- |
| `LABS_AGENT_LIB_PROVIDER` | `portkey` | Gateway to route through: `portkey` or `anthropic`. |
| `LABS_AGENT_LIB_LOG_LEVEL` | `INFO` | `DEBUG`, `INFO`, `WARNING`, or `ERROR`. |
| `LABS_AGENT_LIB_PORTKEY_BASE_URL` | `https://portkeygateway.perficient.com` | Portkey gateway base URL. |
| `LABS_AGENT_LIB_PORTKEY_API_KEY` | `""` | Portkey API key (secret). |
| `LABS_AGENT_LIB_PORTKEY_VIRTUAL` | `""` | Provider/credential alias from the Portkey dashboard (e.g. `aws-bedrock-use2`). |
| `LABS_AGENT_LIB_ANTHROPIC_BASE_URL` | `https://api.anthropic.com` | Anthropic API base URL. |
| `LABS_AGENT_LIB_ANTHROPIC_API_KEY` | `""` | Anthropic API key (secret). |
| `LABS_AGENT_LIB_DISABLE_PROMPT_CACHING` | `false` | Disable Anthropic prompt caching, e.g. while iterating on a system prompt. |

Example `.env`:

```dotenv
LABS_AGENT_LIB_PROVIDER=anthropic
LABS_AGENT_LIB_ANTHROPIC_API_KEY=sk-ant-...
```

## Usage

```python
from labs_agent_lib import get_logger, get_agent_settings, get_agent_environment
from labs_agent_lib.file_reader import extract_text

logger = get_logger(__name__)
settings = get_agent_settings()
env = get_agent_environment(settings)
text = extract_text("resume.pdf")
```

## Development

```bash
uv sync
uv run pytest
```
