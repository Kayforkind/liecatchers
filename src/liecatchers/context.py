from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from liecatchers.types import Contract


@dataclass
class SensorContext:
    workdir: Path
    run_start: float
    contract: Contract = field(default_factory=Contract)
    fail_demo: bool = False

    def liecatcher_dir(self) -> Path:
        return self.workdir / ".liecatcher"

    def load_json(self, rel: str) -> Any | None:
        path = self.workdir / rel
        if not path.is_file():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8-sig"))
        except json.JSONDecodeError:
            return None

    def read_text(self, rel: str) -> str | None:
        path = self.workdir / rel
        if not path.is_file():
            return None
        return path.read_text(encoding="utf-8-sig")

    def git_diff_paths(self) -> set[str]:
        staged = self.liecatcher_dir() / "diff_paths.txt"
        if staged.is_file():
            return {
                line.strip().replace("\\", "/")
                for line in staged.read_text(encoding="utf-8").splitlines()
                if line.strip()
            }
        try:
            proc = subprocess.run(
                ["git", "diff", "--name-only", "HEAD"],
                cwd=self.workdir,
                capture_output=True,
                text=True,
                check=False,
                timeout=10,
            )
            if proc.returncode != 0:
                return set()
            return {
                line.strip().replace("\\", "/")
                for line in proc.stdout.splitlines()
                if line.strip()
            }
        except (OSError, subprocess.TimeoutExpired):
            return set()

    def path_matches(self, path: str, patterns: list[str]) -> bool:
        normalized = path.replace("\\", "/").lstrip("./")
        for pattern in patterns:
            p = pattern.replace("\\", "/").rstrip("/")
            if normalized == p or normalized.startswith(p + "/") or normalized.startswith(p):
                return True
            if p.endswith("**") and normalized.startswith(p[:-2]):
                return True
        return False


PATH_RE = re.compile(
    r"(?:`|/|^|\s)([\w./\\-]+\.(?:py|ts|tsx|js|jsx|md|json|toml|yml|yaml|lock|gyp|node))(?:`|\s|$|,)",
    re.MULTILINE,
)


def extract_mentioned_paths(text: str) -> set[str]:
    found: set[str] = set()
    for match in PATH_RE.finditer(text):
        found.add(match.group(1).replace("\\", "/").lstrip("./"))
    return found


def load_contract(workdir: Path) -> Contract:
    path = workdir / ".liecatcher" / "contract.json"
    if not path.is_file():
        return Contract()
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    return Contract(
        declared_paths=list(data.get("declared_paths", ["src/", "tests/"])),
        declared_commands=list(data.get("declared_commands", ["pytest"])),
        declared_suites=list(data.get("declared_suites", ["pytest"])),
        native_deps=list(data.get("native_deps", [])),
    )


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
