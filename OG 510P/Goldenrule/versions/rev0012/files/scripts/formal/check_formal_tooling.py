#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    strict = str(sys.argv[1]).lower() == "strict" if len(sys.argv) > 1 else False

    root = Path(__file__).resolve().parents[2]
    out = root / "artifacts" / "formal" / "tooling.json"
    out.parent.mkdir(parents=True, exist_ok=True)

    has_z3_cmd = shutil.which("z3") is not None
    has_cvc5_cmd = shutil.which("cvc5") is not None
    has_z3_py = importlib.util.find_spec("z3") is not None

    payload = {
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "strict": strict,
        "tools": {
            "z3_command": has_z3_cmd,
            "z3_python": has_z3_py,
            "cvc5_command": has_cvc5_cmd,
        },
    }
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"formal-tools: wrote {out}")

    available = has_z3_cmd or has_z3_py or has_cvc5_cmd
    if strict and not available:
        print("formal-tools: strict mode requires at least one solver (z3/cvc5)", file=sys.stderr)
        return 1

    state = "available" if available else "not-installed"
    print(f"formal-tools: {state}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
