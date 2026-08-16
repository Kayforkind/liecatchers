# Windows setup

1. Install [uv](https://docs.astral.sh/uv/).
2. `git clone https://github.com/kazimrmerchant/liecatchers.git`
3. `cd liecatchers`
4. `uv sync --extra dev`
5. `uv run liecatcher run --fail-demo` → expect exit code **1**
6. `uv run pytest`

## Common errors

- **`liecatcher` not found** — use `uv run liecatcher` or install editable.
- **All sensors skip** — run `liecatcher init` and fill `.liecatcher/contract.json`.
- **git unavailable** — provide `.liecatcher/diff_paths.txt` for scope/fanfic fixtures.
