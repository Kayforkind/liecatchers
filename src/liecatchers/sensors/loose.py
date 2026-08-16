from __future__ import annotations

import json
import time
from pathlib import Path

from liecatchers.context import SensorContext
from liecatchers.types import SensorResult

UNPINNED_MARKERS = ("@latest", "latest", "*")


def _scan_obj(obj, path: str, hits: list[dict]) -> None:
    if isinstance(obj, dict):
        for key, value in obj.items():
            _scan_obj(value, f"{path}.{key}" if path else key, hits)
    elif isinstance(obj, list):
        for i, value in enumerate(obj):
            _scan_obj(value, f"{path}[{i}]", hits)
    elif isinstance(obj, str):
        lower = obj.lower().strip()
        if lower in UNPINNED_MARKERS or lower.endswith("@latest") or "@latest" in lower:
            hits.append({"path": path, "spec": obj, "reason": "unpinned_latest"})
        elif lower.startswith(">=") or lower.startswith("^") or lower.startswith("~"):
            # soft pin — note but do not fail alone for day-1
            pass
        elif lower.startswith("@") and "/" in lower and "@" not in lower[1:]:
            # npm scoped package without version in a bare string like "@scope/pkg"
            hits.append({"path": path, "spec": obj, "reason": "missing_version"})


def run(ctx: SensorContext) -> SensorResult:
    started = time.perf_counter()
    candidates = [
        ".liecatcher/launch.json",
        ".cursor/mcp.json",
        "mcp.json",
    ]
    hits: list[dict] = []
    scanned: list[str] = []
    for rel in candidates:
        path = ctx.workdir / rel
        if not path.is_file():
            continue
        scanned.append(rel)
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
        except json.JSONDecodeError:
            continue
        _scan_obj(data, rel, hits)

    if not scanned:
        return SensorResult(
            name="loose",
            verdict="skip",
            reason="no launch/mcp manifests found",
            evidence={"launch_manifests": [], "unpinned_entries": []},
            duration_ms=int((time.perf_counter() - started) * 1000),
        )

    if hits:
        return SensorResult(
            name="loose",
            verdict="fail",
            reason=f"{len(hits)} unpinned launch/MCP entries",
            evidence={
                "launch_manifests": scanned,
                "unpinned_entries": hits,
                "note": "hash-drift check deferred (skip in v0.1)",
            },
            duration_ms=int((time.perf_counter() - started) * 1000),
        )
    return SensorResult(
        name="loose",
        verdict="pass",
        reason="no @latest / missing-version markers in manifests",
        evidence={"launch_manifests": scanned, "unpinned_entries": []},
        duration_ms=int((time.perf_counter() - started) * 1000),
    )
