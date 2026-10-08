#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parent
    manifest = root / "PUBLIC_TRACE_HANDOFF_MANIFEST.json"
    gate = root / "tools" / "public_trace_handoff_archive_gate.py"
    if not manifest.exists():
        print(
            "ERROR: PUBLIC_TRACE_HANDOFF_MANIFEST.json missing next to VERIFY_HANDOFF.py; "
            "this launcher is intended for extracted public-trace handoff archives.",
            file=sys.stderr,
        )
        return 2
    if not gate.exists():
        print("ERROR: bundled handoff gate missing: " + str(gate), file=sys.stderr)
        return 2
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    cmd = [sys.executable, str(gate), "--strict", "--no-write"]
    proc = subprocess.run(cmd, cwd=root, env=env)
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
