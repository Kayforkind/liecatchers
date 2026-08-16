# Contributing to liecatchers

## Adding a sensor

1. Create `src/liecatchers/sensors/<name>.py` with `def run(ctx: SensorContext) -> SensorResult`.
2. Register it in `src/liecatchers/sensors/__init__.py` (`REGISTRY` + `DESCRIPTIONS`).
3. Add a fail path to `fixtures/fail_demo/` and a pass path to `fixtures/clean/` (or a dedicated fixture).
4. Extend `tests/test_cli.py` or add a focused test.
5. Run `uv run pytest` and `uv run liecatcher run --fail-demo` (expect exit 1).

## AI assistance

AI coding agents may help draft code. Every contribution must be reviewed by a human who can explain the change. Do not add `Co-authored-by` lines for LLMs. Disclose AI assistance in the PR body if the change is non-trivial.

## Style

- Sensors import only `liecatchers.context` / `liecatchers.types` (and stdlib). No cross-sensor imports.
- Prefer falsifiable evidence dicts over prose-only reasons.
- Windows path normalization: use `/` in evidence.
