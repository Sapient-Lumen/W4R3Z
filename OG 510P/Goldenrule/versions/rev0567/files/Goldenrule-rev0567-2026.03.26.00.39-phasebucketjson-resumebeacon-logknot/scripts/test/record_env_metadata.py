#!/usr/bin/env python3
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def _run(cmd: list[str]) -> str:
    try:
        return subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: scripts/test/record_env_metadata.py <mode> <out_json>", file=sys.stderr)
        return 2

    mode = sys.argv[1]
    out = Path(sys.argv[2]).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    root = Path(__file__).resolve().parents[2]
    rust_exec = root / "tools" / "rust_exec.sh"

    payload = {
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "mode": mode,
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "python": platform.python_version(),
        },
        "toolchain": {
            "cargo": _run([str(rust_exec), "cargo", "--version"]),
            "rustc": _run([str(rust_exec), "rustc", "--version"]),
            "git": _run(["git", "--version"]),
        },
    }

    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"env-metadata: wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
