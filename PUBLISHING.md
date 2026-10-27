# Guide: Publishing `labs-agent-lib` to PyPI

This package is a [uv workspace](https://docs.astral.sh/uv/concepts/projects/workspaces/) member within `candidate-match-agent`. 
* It has its own `pyproject.toml`, version, and dependencies.
* **Crucial:** Run all commands from the **repository root** (`candidate-match-agent/`), not the package folder. Build artifacts will always generate in the root `dist/` directory.

## 0. Prerequisites
* `uv` installed.
* Accounts on PyPI and TestPyPI with project-scoped API tokens.
* Export your tokens as environment variables to keep them out of your shell history:

```bash
export UV_PUBLISH_TOKEN_TESTPYPI="pypi-...your-testpypi-token..."
export UV_PUBLISH_TOKEN_PYPI="pypi-...your-pypi-token..."
```

## 1. Pre-Publication Checklist
1. Ensure all tests pass with 100% coverage:
   ```bash
   cd packages/labs-agent-lib
   uv run pytest
   cd ../..
   ```
2. **Bump the version** in `packages/labs-agent-lib/pyproject.toml`. (PyPI strictly requires a new version number for every upload).
3. *(Optional)* Tag the release in git:
   ```bash
   git tag labs-agent-lib-v0.3.0
   git push origin labs-agent-lib-v0.3.0
   ```

## 2. Build the Package
From the repository root, run:

```bash
uv build --package labs-agent-lib
```
Verify that the `dist/` folder contains only the `.tar.gz` and `.whl` files for the version you intend to publish. Delete older files if necessary.

## 3. Publish to TestPyPI (Mandatory Pre-Check)
Always publish to TestPyPI first to validate metadata and dependencies.

```bash
export UV_PUBLISH_TOKEN="pypi-..."

uv publish \
  --publish-url [https://test.pypi.org/legacy/](https://test.pypi.org/legacy/) \
  dist/labs_agent_lib-0.2.0*
```
*(Alternatively, pass the token directly: 
`uv publish --publish-url https://test.pypi.org/legacy/ --token pypi-.. dist/labs_agent_lib-0.3.0*`)*

### 3.1 Verify TestPyPI Installation
Because TestPyPI lacks all third-party dependencies, pull the package from TestPyPI and dependencies from the real PyPI:

```bash
uv venv /tmp/check-labs-agent-lib
cd /tmp/check-labs-agent-lib

uv pip install \
  --index-url [https://test.pypi.org/simple/](https://test.pypi.org/simple/) \
  --extra-index-url [https://pypi.org/simple/](https://pypi.org/simple/) \
  labs-agent-lib

uv run python -c "from labs_agent_lib import get_logger, get_settings; print('OK')"
```
*If this fails, fix the code, bump the version again (e.g., `0.2.1`), and repeat steps 1-3.*

## 4. Publish to Production PyPI
Once TestPyPI verification passes:

```bash
export UV_PUBLISH_TOKEN="$UV_PUBLISH_TOKEN_PYPI"

uv publish dist/labs_agent_lib-0.1.0*
```

### 4.1 Verify Production Installation
```bash
uv venv /tmp/check-labs-agent-lib-real
cd /tmp/check-labs-agent-lib-real
uv pip install labs-agent-lib
uv run python -c "from labs_agent_lib import get_logger, get_settings; print('OK')"
```

## 5. Using the Package
Install it in other projects using `uv` or `pip`:

```bash
uv add labs-agent-lib
# OR
pip install labs-agent-lib
```
```python
from labs_agent_lib import get_logger, get_settings, get_agent_environment
from labs_agent_lib.file_reader import extract_text
```
> **Note:** As per the README's "Known limitation", `settings` is currently coupled to the `candidate_match_agent` namespace (environment variable prefix). `logger`, `file_reader`, and `agent_environment` are fully reusable.

## 6. Quick Update Workflow Summary
1. Update code in `packages/labs-agent-lib/src/labs_agent_lib/`.
2. Bump `version` in `packages/labs-agent-lib/pyproject.toml`.
3. `cd packages/labs-agent-lib && uv run pytest && cd ../..`
4. `rm -rf dist` (clear old artifacts).
5. `uv build --package labs-agent-lib`
6. Publish to TestPyPI, verify, then publish to PyPI.