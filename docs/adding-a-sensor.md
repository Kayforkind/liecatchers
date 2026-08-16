# Adding a sensor

1. Implement `run(ctx) -> SensorResult` in `src/liecatchers/sensors/<name>.py`.
2. Register in `REGISTRY` and `DESCRIPTIONS`.
3. Keep evidence typed (dicts of paths, hashes, lists) — not only freeform strings.
4. Add fail_demo coverage so `liecatcher run --fail-demo` still exits 1 for the right reasons.
5. Document the lie in one README table row.
