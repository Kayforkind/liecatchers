from __future__ import annotations

import hashlib
import time
from pathlib import Path

from liecatchers.context import SensorContext
from liecatchers.types import SensorResult

LOCKFILES = ("uv.lock", "package-lock.json", "pnpm-lock.yaml", "poetry.lock", "Cargo.lock")


def _hash_lockfiles(root: Path) -> str:
    h = hashlib.sha256()
    found = False
    for name in LOCKFILES:
        path = root / name
        if path.is_file():
            found = True
            h.update(name.encode())
            h.update(path.read_bytes())
    return h.hexdigest() if found else ""


def run(ctx: SensorContext) -> SensorResult:
    started = time.perf_counter()
    baseline_file = ctx.liecatcher_dir() / "baseline.lock"
    current = _hash_lockfiles(ctx.workdir)
    if not current:
        return SensorResult(
            name="sneak",
            verdict="skip",
            reason="no lockfiles present",
            evidence={"current_hash": "", "baseline_hash": None},
            duration_ms=int((time.perf_counter() - started) * 1000),
        )

    if not baseline_file.is_file():
        return SensorResult(
            name="sneak",
            verdict="skip",
            reason="no .liecatcher/baseline.lock to compare",
            evidence={"current_hash": current, "baseline_hash": None},
            duration_ms=int((time.perf_counter() - started) * 1000),
        )

    baseline = baseline_file.read_text(encoding="utf-8").strip()
    if baseline != current:
        return SensorResult(
            name="sneak",
            verdict="fail",
            reason="lockfile hash drifted from baseline",
            evidence={
                "baseline_hash": baseline,
                "current_hash": current,
                "lockfiles_changed": True,
            },
            duration_ms=int((time.perf_counter() - started) * 1000),
        )
    return SensorResult(
        name="sneak",
        verdict="pass",
        reason="lockfile hash matches baseline",
        evidence={
            "baseline_hash": baseline,
            "current_hash": current,
            "lockfiles_changed": False,
        },
        duration_ms=int((time.perf_counter() - started) * 1000),
    )
