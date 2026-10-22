#!/usr/bin/env python3
"""Small shared helpers for Foundry fixture checks.

The older checkers remain intentionally standalone. Newer checks use this module
so the harness can grow without copy/pasting root discovery, JSON loading, ISO
parsing, and runner behavior in every new specimen.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
import json
import runpy
import sys
from typing import Iterable, Any

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def parse_time(value: str | None) -> datetime | None:
    if not value or not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def require_sha256(value: str | None) -> bool:
    return isinstance(value, str) and value.startswith("sha256:") and len(value) > len("sha256:")


def fail(errors: Iterable[str]) -> None:
    errors = list(errors)
    if errors:
        for err in errors:
            print(err)
        sys.exit(1)


def run_check_scripts(script_names: Iterable[str]) -> None:
    for script in script_names:
        path = ROOT / "tools" / script
        try:
            runpy.run_path(str(path), run_name="__main__")
        except SystemExit as exc:
            code = exc.code if isinstance(exc.code, int) else 1
            if code:
                sys.exit(code)
