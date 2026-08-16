from __future__ import annotations

import json
import time
from pathlib import Path

from liecatchers.context import SensorContext
from liecatchers.types import SensorResult

KNOWN_NATIVE = ("sharp", "node-sass", "better-sqlite3", "sqlite3")


def _declared_native(ctx: SensorContext) -> list[str]:
    deps = list(ctx.contract.native_deps)
    pkg = ctx.workdir / "package.json"
    if pkg.is_file():
        data = json.loads(pkg.read_text(encoding="utf-8-sig"))
        all_deps = {}
        all_deps.update(data.get("dependencies") or {})
        all_deps.update(data.get("devDependencies") or {})
        for name in KNOWN_NATIVE:
            if name in all_deps and name not in deps:
                deps.append(name)
    return deps


def _native_present(root: Path, dep: str) -> dict:
    base = root / "node_modules" / dep
    binding = base / "binding.gyp"
    release = base / "build" / "Release"
    nodes = list(release.glob("*.node")) if release.is_dir() else []
    # Also accept a marker file for fixtures
    marker = base / "build" / "Release" / f"{dep}.node"
    present = binding.is_file() or bool(nodes) or marker.is_file()
    return {
        "binding_gyp": binding.is_file(),
        "node_files": [str(p) for p in nodes] + ([str(marker)] if marker.is_file() else []),
        "present": present,
    }


def run(ctx: SensorContext) -> SensorResult:
    started = time.perf_counter()
    deps = _declared_native(ctx)
    if not deps:
        return SensorResult(
            name="hollow",
            verdict="skip",
            reason="no known native deps declared",
            evidence={"native_deps_declared": []},
            duration_ms=int((time.perf_counter() - started) * 1000),
        )

    npm_exit = (ctx.load_json(".liecatcher/exit_codes.json") or {}).get("npm", 0)
    artifacts = {dep: _native_present(ctx.workdir, dep) for dep in deps}
    missing = [d for d, info in artifacts.items() if not info["present"]]

    if npm_exit == 0 and missing:
        return SensorResult(
            name="hollow",
            verdict="fail",
            reason=f"npm looks green but native bits missing: {missing}",
            evidence={
                "native_deps_declared": deps,
                "native_artifacts": artifacts,
                "npm_exit_code": npm_exit,
            },
            duration_ms=int((time.perf_counter() - started) * 1000),
        )
    return SensorResult(
        name="hollow",
        verdict="pass",
        reason="native artifacts present for declared deps",
        evidence={
            "native_deps_declared": deps,
            "native_artifacts": artifacts,
            "npm_exit_code": npm_exit,
        },
        duration_ms=int((time.perf_counter() - started) * 1000),
    )
