#!/usr/bin/env python3
"""Add portable replay commands beside historical OCF benchmark commands.

The benchmark records intentionally preserve the original command line used for
measurement, including /opt/pyvenv/bin/python3.  Those commands are poor replay
instructions for archive consumers.  This script adds explicit portable replay
fields while preserving the original measurements and command provenance.
"""
from __future__ import annotations

import json
import shlex
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
AUDIT_JSON = ROOT / "AUDIT" / "OCF_PORTABLE_REPLAY_COMMANDS_REV0832.json"
AUDIT_MD = ROOT / "AUDIT" / "OCF_PORTABLE_REPLAY_COMMANDS_REV0832.md"
BENCH_FILES = [
    "sources/ocf_llm/examples/resolver_bench_v1.json",
    "sources/ocf_llm/examples/resolver_bench_v2.json",
    "sources/ocf_llm/examples/resolver_bench_v3.json",
    "sources/ocf_llm/examples/runtime_gate_bench_v1.json",
]
PREFIXABLE_PATH_PREFIXES = ("tools/", "examples/", "profiles/")


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _target_for_row(row: dict[str, Any]) -> dict[str, Any]:
    result = row.get("result")
    if isinstance(result, dict) and "cmd" in result:
        return result
    return row


def portableize(cmd: str, base: str) -> str:
    parts = shlex.split(cmd)
    if not parts:
        raise ValueError("empty command")
    if parts[0] != "/opt/pyvenv/bin/python3":
        raise ValueError(f"unexpected historical interpreter: {parts[0]!r}")
    parts[0] = "python3"
    if base == "sources/ocf_llm":
        rewritten: list[str] = []
        for idx, token in enumerate(parts):
            if idx == 0:
                rewritten.append(token)
                continue
            if token.startswith("-") or token.startswith("sources/ocf_llm/") or token.startswith("/"):
                rewritten.append(token)
                continue
            if token.startswith(PREFIXABLE_PATH_PREFIXES):
                rewritten.append("sources/ocf_llm/" + token)
            else:
                rewritten.append(token)
        parts = rewritten
    return shlex.join(parts)


def command_path_checks(portable_cmd: str) -> list[dict[str, Any]]:
    parts = shlex.split(portable_cmd)
    checks: list[dict[str, Any]] = []
    for idx, token in enumerate(parts[1:], start=1):
        if token.startswith("-"):
            continue
        if token.startswith("sources/ocf_llm/"):
            path = ROOT / token
            checks.append({
                "argument_index": idx,
                "path": token,
                "exists": path.exists(),
                "kind": "dir" if path.is_dir() else "file" if path.is_file() else "missing",
            })
    return checks


def iter_command_targets(root: Path = ROOT):
    for rel_path in BENCH_FILES:
        path = root / rel_path
        data = json.loads(path.read_text(encoding="utf-8"))
        base = str(data.get("base") or ".")
        rows = data.get("rows") or []
        if not isinstance(rows, list):
            continue
        for idx, row in enumerate(rows):
            if not isinstance(row, dict):
                continue
            target = _target_for_row(row)
            cmd = target.get("cmd")
            if isinstance(cmd, str) and cmd.startswith("/opt/pyvenv/bin/python3"):
                yield rel_path, path, data, rows, idx, row, target, base, cmd


def apply(root: Path = ROOT) -> dict[str, Any]:
    changed_files: set[str] = set()
    rows_out: list[dict[str, Any]] = []
    loaded: dict[str, dict[str, Any]] = {}

    for rel_path, path, data, rows, idx, row, target, base, cmd in iter_command_targets(root):
        portable_cmd = portableize(cmd, base)
        target["portable_cmd"] = portable_cmd
        target["portable_cwd"] = "."
        target["portable_replay_added"] = "rev0832"
        target["historical_cmd_preserved"] = True
        checks = command_path_checks(portable_cmd)
        rows_out.append({
            "file": rel_path,
            "row_index": idx,
            "row_id": row.get("id") or row.get("abom") or row.get("about") or str(idx),
            "base": base,
            "historical_cmd": cmd,
            "portable_cwd": ".",
            "portable_cmd": portable_cmd,
            "path_checks": checks,
            "missing_path_count": sum(1 for c in checks if not c["exists"]),
        })
        loaded[rel_path] = data
        changed_files.add(rel_path)

    for rel_path in sorted(changed_files):
        path = root / rel_path
        path.write_text(json.dumps(loaded[rel_path], indent=2, sort_keys=False) + "\n", encoding="utf-8")

    data = build_audit(root)
    AUDIT_JSON.parent.mkdir(parents=True, exist_ok=True)
    AUDIT_JSON.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    AUDIT_MD.write_text(render_markdown(data), encoding="utf-8")
    return data


def build_audit(root: Path = ROOT) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for rel_path in BENCH_FILES:
        path = root / rel_path
        data = json.loads(path.read_text(encoding="utf-8"))
        base = str(data.get("base") or ".")
        for idx, row in enumerate(data.get("rows") or []):
            if not isinstance(row, dict):
                continue
            target = _target_for_row(row)
            cmd = target.get("cmd")
            if not (isinstance(cmd, str) and cmd.startswith("/opt/pyvenv/bin/python3")):
                continue
            portable_cmd = target.get("portable_cmd")
            checks = command_path_checks(str(portable_cmd or "")) if isinstance(portable_cmd, str) else []
            rows.append({
                "file": rel_path,
                "row_index": idx,
                "row_id": row.get("id") or row.get("abom") or row.get("about") or str(idx),
                "base": base,
                "historical_cmd": cmd,
                "portable_cwd": target.get("portable_cwd"),
                "portable_cmd": portable_cmd,
                "has_portable_cmd": isinstance(portable_cmd, str) and portable_cmd.startswith("python3 "),
                "has_private_interpreter_in_portable_cmd": isinstance(portable_cmd, str) and "/opt/pyvenv" in portable_cmd,
                "path_checks": checks,
                "missing_path_count": sum(1 for c in checks if not c["exists"]),
            })
    by_file = Counter(row["file"] for row in rows)
    return {
        "version": 1,
        "revision_context": "rev0832-session-patch-over-rev0831-over-rev0826",
        "status": "portable_replay_fields_present" if rows and all(row["has_portable_cmd"] and not row["has_private_interpreter_in_portable_cmd"] and row["missing_path_count"] == 0 for row in rows) else "portable_replay_fields_incomplete",
        "purpose": "Preserve historical OCF benchmark commands while adding archive-root portable replay commands for consumers.",
        "summary": {
            "benchmark_files_checked": len(BENCH_FILES),
            "historical_private_interpreter_commands": len(rows),
            "portable_commands_present": sum(1 for row in rows if row["has_portable_cmd"]),
            "portable_commands_with_private_interpreter": sum(1 for row in rows if row["has_private_interpreter_in_portable_cmd"]),
            "portable_commands_with_missing_paths": sum(1 for row in rows if row["missing_path_count"]),
            "files_touched": len(by_file),
        },
        "commands_by_file": [{"file": f, "command_count": by_file[f]} for f in sorted(by_file)],
        "rows": rows,
        "builder": "scripts/add_ocf_portable_replay_commands.py",
        "validator": "scripts/validate_ocf_portable_replay_commands.py",
    }


def render_markdown(data: dict[str, Any]) -> str:
    s = data["summary"]
    lines = [
        "# OCF portable replay command patch (rev0832)",
        "",
        "Historical benchmark commands are retained unchanged, but every `/opt/pyvenv/bin/python3` command now has an archive-root portable replay command beside it.",
        "",
        f"- Status: `{data['status']}`",
        f"- Historical private-interpreter commands: **{s['historical_private_interpreter_commands']}**",
        f"- Portable commands present: **{s['portable_commands_present']}**",
        f"- Portable commands with missing checked paths: **{s['portable_commands_with_missing_paths']}**",
        "",
        "## Commands by file",
        "",
        "| File | Commands |",
        "| --- | ---: |",
    ]
    for row in data["commands_by_file"]:
        lines.append(f"| `{row['file']}` | {row['command_count']} |")
    lines.extend([
        "",
        "## Sample mappings",
        "",
        "| File | Row | Portable command |",
        "| --- | --- | --- |",
    ])
    for row in data["rows"][:8]:
        lines.append(f"| `{row['file']}` | `{row['row_id']}` | `{row['portable_cmd']}` |")
    lines.extend([
        "",
        "## Interpretation",
        "",
        "This is not a re-benchmark. The original timing command remains as measurement provenance. The new field is a consumer replay affordance that avoids the private virtualenv path and resolves checked archive paths from the archive root.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    data = apply(ROOT)
    print(
        "ocf-portable-replay-commands: OK "
        f"({data['summary']['portable_commands_present']} portable commands)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
