#!/usr/bin/env python3
"""Build an audit of path/reference strings that remain structurally suspect.

This is deliberately narrower than the cloud absolute-path audit.  It looks for
portable-but-still-suspicious path shapes that can break replay or mislead a
reader: serialized Python objects embedded in path values and benchmark command
records pinned to a private virtualenv interpreter.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
JSON_OUT = ROOT / "AUDIT" / "PATH_REFERENCE_SHAPE_AUDIT.json"
MD_OUT = ROOT / "AUDIT" / "PATH_REFERENCE_SHAPE_AUDIT.md"
SKIP_DIR_PARTS = {".git", "__pycache__"}
SKIP_REL = {
    "AUDIT/PATH_REFERENCE_SHAPE_AUDIT.json",
    "AUDIT/PATH_REFERENCE_SHAPE_AUDIT.md",
    "AUDIT/RESIDUAL_PATH_PORTABILITY_REWRITE_REV0831.json",
    "AUDIT/RESIDUAL_PATH_PORTABILITY_REWRITE_REV0831.md",
    "scripts/apply_residual_path_portability_rewrites.py",
    "scripts/validate_residual_path_portability_rewrite.py",
    "scripts/build_path_reference_shape_audit.py",
    "scripts/validate_path_reference_shape_audit.py",
    "AUDIT/OCF_PORTABLE_REPLAY_COMMANDS_REV0832.json",
    "AUDIT/OCF_PORTABLE_REPLAY_COMMANDS_REV0832.md",
    "scripts/add_ocf_portable_replay_commands.py",
    "scripts/validate_ocf_portable_replay_commands.py",
    "AUDIT/OCF_TRACE_REGENERATION_REV0832.json",
    "AUDIT/OCF_TRACE_REGENERATION_REV0832.md",
    "scripts/regenerate_ocf_trace_rev0832.py",
    "scripts/validate_ocf_trace_regeneration_rev0832.py",
}
BENCHMARK_FILES_WITH_PORTABLE_REPLAY = {
    "sources/ocf_llm/examples/resolver_bench_v1.json",
    "sources/ocf_llm/examples/resolver_bench_v2.json",
    "sources/ocf_llm/examples/resolver_bench_v3.json",
    "sources/ocf_llm/examples/runtime_gate_bench_v1.json",
}
SERIALIZED_OBJECT_PATH_RE = re.compile(
    r"(?P<value>[A-Za-z0-9_./:-]+/\{['\"]kind['\"]:\s*['\"]file['\"],\s*['\"]path['\"]:\s*['\"][^\n\r]+?\})"
)
ABSOLUTE_PYTHON_COMMAND_RE = re.compile(r"/opt/pyvenv/bin/python3(?:\s+[^\n\r\"]{0,240})?")


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def iter_text_files(root: Path = ROOT):
    for path in sorted(root.rglob("*")):
        if any(part in SKIP_DIR_PARTS for part in path.parts):
            continue
        if not path.is_file():
            continue
        r = rel(path)
        if r in SKIP_REL:
            continue
        try:
            path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        yield path


def family_for_path(r: str) -> str:
    parts = r.split("/")
    if len(parts) >= 3 and parts[0] == "sources":
        return f"sources/{parts[1]}"
    if len(parts) >= 3 and parts[0] in {"artifacts", "certs"} and parts[1] == "curated":
        return f"{parts[0]}/curated/{parts[2]}"
    if len(parts) >= 2:
        return "/".join(parts[:2])
    return parts[0]


def snippet(value: str, limit: int = 220) -> str:
    compact = " ".join(value.strip().split())
    return compact if len(compact) <= limit else compact[: limit - 1] + "…"


def line_for_offset(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def build(root: Path = ROOT) -> dict[str, Any]:
    global ROOT
    old_root = ROOT
    ROOT = root
    try:
        rows: list[dict[str, Any]] = []
        for path in iter_text_files(ROOT):
            r = rel(path)
            text = path.read_text(encoding="utf-8")
            findings: list[dict[str, Any]] = []
            for m in SERIALIZED_OBJECT_PATH_RE.finditer(text):
                findings.append({
                    "kind": "serialized_object_embedded_in_path_value",
                    "line": line_for_offset(text, m.start()),
                    "sample": snippet(m.group("value")),
                    "risk": "path value appears to contain a serialized Python mapping instead of a plain file path",
                    "suggested_action": "re-run the producing resolver or add a corrected trace; do not silently reinterpret historical fail-closed output",
                })
            skip_mitigated_benchmark_cmds = (
                r in BENCHMARK_FILES_WITH_PORTABLE_REPLAY
                and '"portable_cmd"' in text
                and '"portable_replay_added": "rev0832"' in text
            )
            if not skip_mitigated_benchmark_cmds:
                for m in ABSOLUTE_PYTHON_COMMAND_RE.finditer(text):
                    findings.append({
                        "kind": "absolute_virtualenv_python_command",
                        "line": line_for_offset(text, m.start()),
                        "sample": snippet(m.group(0)),
                        "risk": "benchmark/replay command is pinned to a private virtualenv path",
                        "suggested_action": "keep as historical measurement metadata or add a separate portable replay command using python3",
                    })
            if findings:
                counts = Counter(f["kind"] for f in findings)
                rows.append({
                    "path": r,
                    "family": family_for_path(r),
                    "finding_count": len(findings),
                    "finding_counts": dict(sorted(counts.items())),
                    "findings": findings[:80],
                })
        rows.sort(key=lambda row: (row["family"], row["path"]))
        total_counts = Counter()
        family_counts = Counter()
        for row in rows:
            family_counts[row["family"]] += row["finding_count"]
            for k, v in row["finding_counts"].items():
                total_counts[k] += v
        return {
            "version": 1,
            "revision_context": "rev0831-session-patch-over-rev0830-over-rev0826",
            "status": "shape_anomalies_surfaced" if rows else "no_known_path_shape_anomalies_found",
            "purpose": "Surface remaining path/reference strings that are portable enough to avoid cloud absolute paths but still risky for replay or interpretation.",
            "summary": {
                "files_scanned_as_utf8_text": sum(1 for _ in iter_text_files(ROOT)),
                "files_with_shape_anomalies": len(rows),
                "shape_anomaly_count": sum(row["finding_count"] for row in rows),
                "finding_counts": dict(sorted(total_counts.items())),
                "families_with_shape_anomalies": len(family_counts),
            },
            "summary_by_family": [
                {"family": fam, "finding_count": family_counts[fam]}
                for fam in sorted(family_counts)
            ],
            "rows": rows,
            "builder": "scripts/build_path_reference_shape_audit.py",
            "validator": "scripts/validate_path_reference_shape_audit.py",
        }
    finally:
        ROOT = old_root


def render_markdown(data: dict[str, Any]) -> str:
    s = data["summary"]
    lines = [
        "# Path reference shape audit",
        "",
        "This audit catches path/reference strings that are no longer cloud absolute paths but still look structurally unsafe for replay or interpretation.",
        "",
        f"- Status: `{data['status']}`",
        f"- UTF-8 text files scanned: **{s['files_scanned_as_utf8_text']}**",
        f"- Files with shape anomalies: **{s['files_with_shape_anomalies']}**",
        f"- Shape anomalies: **{s['shape_anomaly_count']}**",
        "",
        "## Finding counts",
        "",
        "| Finding kind | Count |",
        "| --- | ---: |",
    ]
    for kind, count in s["finding_counts"].items():
        lines.append(f"| `{kind}` | {count} |")
    if not s["finding_counts"]:
        lines.append("| none | 0 |")
    lines.extend([
        "",
        "## By family/area",
        "",
        "| Family/area | Findings |",
        "| --- | ---: |",
    ])
    for row in data["summary_by_family"]:
        lines.append(f"| `{row['family']}` | {row['finding_count']} |")
    lines.extend([
        "",
        "## Files with findings",
        "",
        "| Path | Findings | Examples |",
        "| --- | ---: | --- |",
    ])
    for row in data["rows"]:
        examples = "<br>".join(f"line {f['line']}: `{f['kind']}` — `{f['sample']}`" for f in row["findings"][:5])
        lines.append(f"| `{row['path']}` | {row['finding_count']} | {examples} |")
    lines.extend([
        "",
        "## Interpretation",
        "",
        "Serialized-object path findings indicate producer bugs or failed resolver coercions. Rev0832 regenerates the known SIC/RTM trace that carried this issue.",
        "",
        "Historical `/opt/pyvenv` benchmark commands are not treated as active shape anomalies when the same record carries rev0832 `portable_cmd` replay fields; see `AUDIT/OCF_PORTABLE_REPLAY_COMMANDS_REV0832.*`.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    data = build(ROOT)
    JSON_OUT.parent.mkdir(parents=True, exist_ok=True)
    JSON_OUT.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MD_OUT.write_text(render_markdown(data), encoding="utf-8")
    print(
        "path-reference-shape-audit-build: OK "
        f"({data['summary']['files_with_shape_anomalies']} files, {data['summary']['shape_anomaly_count']} findings)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
