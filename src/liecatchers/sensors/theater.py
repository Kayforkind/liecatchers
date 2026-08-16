from __future__ import annotations

import re
import time

from liecatchers.context import SensorContext
from liecatchers.types import SensorResult

PATCH_RE = re.compile(
    r"""(?:mock\.patch|unittest\.mock\.patch|patch)\(\s*['"]([^'"]+)['"]""",
    re.MULTILINE,
)


def run(ctx: SensorContext) -> SensorResult:
    started = time.perf_counter()
    tests_dir = ctx.workdir / "tests"
    if tests_dir.is_dir():
        test_files = list(tests_dir.rglob("test_*.py")) + list(tests_dir.rglob("*_test.py"))
    else:
        test_files = list(ctx.workdir.glob("test_*.py"))

    if not test_files:
        return SensorResult(
            name="theater",
            verdict="skip",
            reason="no test files found",
            evidence={"suspicious_patches": []},
            duration_ms=int((time.perf_counter() - started) * 1000),
            status="heuristic",
        )

    suspicious: list[dict] = []
    for path in test_files:
        text = path.read_text(encoding="utf-8-sig", errors="ignore")
        stem = path.stem
        unit = stem[5:] if stem.startswith("test_") else stem.replace("_test", "")
        for match in PATCH_RE.finditer(text):
            target = match.group(1)
            if unit and (f".{unit}" in target or target.endswith(unit) or f"/{unit}" in target):
                suspicious.append(
                    {
                        "test_file": str(path.relative_to(ctx.workdir)).replace("\\", "/"),
                        "target": target,
                        "unit_under_test": unit,
                    }
                )

    coverage_meta = ctx.load_json(".liecatcher/coverage.json") or {}
    coverage_pct = coverage_meta.get("percent")

    if suspicious and (coverage_pct is None or float(coverage_pct) >= 80):
        return SensorResult(
            name="theater",
            verdict="fail",
            reason="coverage theater: mock.patch targets the unit under test",
            evidence={
                "coverage_pct": coverage_pct,
                "suspicious_patches": suspicious,
            },
            duration_ms=int((time.perf_counter() - started) * 1000),
            status="heuristic",
        )

    return SensorResult(
        name="theater",
        verdict="pass",
        reason="no suspicious same-unit mock.patch patterns",
        evidence={"coverage_pct": coverage_pct, "suspicious_patches": suspicious},
        duration_ms=int((time.perf_counter() - started) * 1000),
        status="heuristic",
    )
