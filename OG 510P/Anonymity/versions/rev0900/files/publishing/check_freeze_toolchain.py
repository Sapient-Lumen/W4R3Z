#!/usr/bin/env python3
"""Report local TeX toolchain availability for freeze-lane compile gates.

This is an informational, non-authorizing surface.  Toolchain absence is not an
archive-integrity failure, but it keeps the current clean-compile publication
gate pending until a TeX-equipped environment refreshes the witness.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import shutil
import subprocess
import sys
import hashlib
from typing import Any


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def version_record_for(command: str) -> dict[str, str]:
    path = shutil.which(command)
    if not path:
        return {"version_line": "", "version_output_sha256": ""}
    try:
        proc = subprocess.run([command, "--version"], text=True, capture_output=True, timeout=5)
        output = proc.stdout if proc.stdout else proc.stderr
    except Exception:
        output = ""
    return {
        "version_line": output.splitlines()[0][:200] if output.splitlines() else "",
        "version_output_sha256": hashlib.sha256(output.encode("utf-8", errors="replace")).hexdigest() if output else "",
    }


def check(root: pathlib.Path) -> dict[str, Any]:
    release = load_json(root / "RELEASE_MANIFEST.json")
    commands = []
    for command in ["pdflatex", "latexmk"]:
        path = shutil.which(command)
        version_record = version_record_for(command)
        commands.append({
            "command": command,
            "available": bool(path),
            "path": path or "",
            "version_line": version_record["version_line"],
            "version_output_sha256": version_record["version_output_sha256"],
        })
    any_available = any(row["available"] for row in commands)
    return {
        "status": "pass",
        "generated_for_revision": release["revision"],
        "checked_bundle": release["bundle"],
        "publication_authorized": False,
        "toolchain_gate_status": "available" if any_available else "unavailable",
        "commands": commands,
        "summary": {
            "available_command_count": sum(1 for row in commands if row["available"]),
            "checked_command_count": len(commands),
            "fingerprinted_command_count": sum(1 for row in commands if row["available"] and row.get("version_output_sha256")),
            "publication_blocking_when_compile_witness_not_current": not any_available,
        },
        "fail_closed_rule": "If no TeX command is available, the archive may still be coherent, but the current publication compile gate cannot be closed here.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--write-report", default="")
    args = parser.parse_args()
    root = pathlib.Path(args.root).resolve()
    report = check(root)
    text = json.dumps(report, indent=2) + "\n"
    if args.write_report:
        out = root / args.write_report
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
