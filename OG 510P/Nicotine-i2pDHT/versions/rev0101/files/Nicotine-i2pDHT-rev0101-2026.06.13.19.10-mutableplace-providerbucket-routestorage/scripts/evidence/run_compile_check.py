#!/usr/bin/env python3
"""Deterministic compile hygiene check for the baby cube.

This avoids relying on compileall's cache-writing behavior in constrained
cloudtainers. It walks the active Python surfaces and py_compile-checks each
file without producing persistent bytecode.
"""
from __future__ import annotations

import json
import tempfile
import py_compile
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[2]
ACTIVE_DIRS = (ROOT / "src", ROOT / "tests", ROOT / "scripts")
SKIP_PARTS = {"__pycache__", ".pytest_cache"}
REPORT_PATH = ROOT / "artifacts" / "process" / "compile_check.json"


def iter_python_files() -> Iterable[Path]:
    for base in ACTIVE_DIRS:
        if not base.exists():
            continue
        for path in sorted(base.rglob("*.py")):
            if any(part in SKIP_PARTS for part in path.parts):
                continue
            yield path


def main() -> int:
    files = list(iter_python_files())
    failures: list[dict[str, str]] = []
    for path in files:
        try:
            with tempfile.NamedTemporaryFile(prefix="i2p_dht_compile_", suffix=".pyc") as tmp:
                py_compile.compile(str(path), cfile=tmp.name, doraise=True)
        except (py_compile.PyCompileError, OSError) as exc:
            failures.append({"path": str(path.relative_to(ROOT)), "error": str(exc)})

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "schema": "i2p_dht_lab.compile_check.v1",
        "revision": (ROOT / "VERSION").read_text(encoding="utf-8").strip(),
        "checked_files": len(files),
        "status": "pass" if not failures else "fail",
        "failures": failures,
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if failures:
        print(f"compile check fail: {len(failures)} failures; wrote {REPORT_PATH.relative_to(ROOT)}")
        return 1
    print(f"compile check pass: {len(files)} files; wrote {REPORT_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
