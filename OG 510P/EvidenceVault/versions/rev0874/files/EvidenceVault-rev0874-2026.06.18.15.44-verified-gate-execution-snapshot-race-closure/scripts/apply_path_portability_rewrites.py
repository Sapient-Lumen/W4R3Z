#!/usr/bin/env python3
"""Rewrite safe cloud/container absolute path references to shipped relative paths.

This is intentionally conservative: it rewrites only references whose trailing
path components resolve to exactly one file shipped inside the current archive.
References with no shipped target, or with ambiguous shipped targets, are left
unchanged and remain surfaced by the absolute-path audit.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
JSON_OUT = ROOT / "AUDIT" / "PATH_PORTABILITY_REWRITE_REV0830.json"
MD_OUT = ROOT / "AUDIT" / "PATH_PORTABILITY_REWRITE_REV0830.md"
PATH_RE = re.compile(r"/(?:mnt/data|home/oai)/[^\s\"'\)\]\}\,<`]+")
ALLOW_PREFIXES = ("sources/", "certs/curated/", "artifacts/curated/")
SKIP_DIR_PARTS = {".git", "__pycache__"}
SKIP_REL = {
    "AUDIT/ABSOLUTE_PATH_REFERENCE_AUDIT.json",
    "AUDIT/ABSOLUTE_PATH_REFERENCE_AUDIT.md",
    "AUDIT/PATH_NORMALIZATION_PATCH_REV0829.json",
    "AUDIT/PATH_NORMALIZATION_PATCH_REV0829.md",
    "AUDIT/PATH_PORTABILITY_REWRITE_REV0830.json",
    "AUDIT/PATH_PORTABILITY_REWRITE_REV0830.md",
    "scripts/apply_path_portability_rewrites.py",
    "scripts/build_absolute_path_reference_audit.py",
    "scripts/validate_absolute_path_reference_audit.py",
    "scripts/validate_path_portability_rewrite.py",
}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def iter_all_files(root: Path = ROOT):
    for path in sorted(root.rglob("*")):
        if any(part in SKIP_DIR_PARTS for part in path.parts):
            continue
        if path.is_file():
            yield path


def iter_candidate_text_files(root: Path = ROOT):
    for path in iter_all_files(root):
        r = rel(path)
        if r in SKIP_REL:
            continue
        if not r.startswith(ALLOW_PREFIXES):
            continue
        try:
            path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        yield path


def build_suffix_index(root: Path = ROOT, max_components: int = 8) -> dict[int, dict[str, list[str]]]:
    suffix_maps: dict[int, dict[str, list[str]]] = {
        k: defaultdict(list) for k in range(1, max_components + 1)
    }
    for path in iter_all_files(root):
        r = rel(path)
        parts = r.split("/")
        for k in range(1, min(max_components, len(parts)) + 1):
            suffix_maps[k]["/".join(parts[-k:])].append(r)
    return suffix_maps


def best_shipped_target(abs_ref: str, suffix_maps: dict[int, dict[str, list[str]]], max_components: int = 8) -> tuple[str | None, int, str]:
    parts = abs_ref.strip("/").split("/")
    if parts[:2] == ["mnt", "data"]:
        rest = parts[2:]
    elif parts[:2] == ["home", "oai"]:
        rest = parts[2:]
    else:
        rest = parts
    best_hits: list[str] = []
    best_k = 0
    best_suffix = ""
    for k in range(1, min(max_components, len(rest)) + 1):
        suffix = "/".join(rest[-k:])
        hits = suffix_maps[k].get(suffix, [])
        if hits:
            best_hits = hits
            best_k = k
            best_suffix = suffix
    if len(best_hits) == 1:
        return best_hits[0], best_k, best_suffix
    if len(best_hits) > 1:
        return None, best_k, best_suffix
    return None, 0, ""


def plan_rewrites(root: Path = ROOT) -> dict[str, Any]:
    suffix_maps = build_suffix_index(root)
    rows: list[dict[str, Any]] = []
    external_or_unresolved: list[dict[str, Any]] = []
    ambiguous: list[dict[str, Any]] = []
    summary = Counter()
    for path in iter_candidate_text_files(root):
        r = rel(path)
        text = path.read_text(encoding="utf-8")
        matches = PATH_RE.findall(text)
        if not matches:
            continue
        file_replacements: dict[tuple[str, str], int] = Counter()
        file_external: Counter[str] = Counter()
        file_ambiguous: Counter[str] = Counter()
        for match in matches:
            target, suffix_components, matched_suffix = best_shipped_target(match, suffix_maps)
            if target is not None:
                file_replacements[(match, target)] += 1
            elif suffix_components:
                file_ambiguous[match] += 1
            else:
                file_external[match] += 1
        if file_replacements:
            rows.append({
                "path": r,
                "old_sha256": sha256(path),
                "replacement_count": sum(file_replacements.values()),
                "unique_replacement_count": len(file_replacements),
                "replacements": [
                    {"from": old, "to": new, "count": count}
                    for (old, new), count in sorted(file_replacements.items())
                ],
            })
            summary["files_with_rewrites"] += 1
            summary["rewrite_reference_count"] += sum(file_replacements.values())
            summary["unique_rewrite_pairs"] += len(file_replacements)
        if file_external:
            external_or_unresolved.append({
                "path": r,
                "reference_count": sum(file_external.values()),
                "references": [
                    {"reference": ref, "count": count}
                    for ref, count in sorted(file_external.items())
                ],
            })
            summary["unresolved_reference_count"] += sum(file_external.values())
            summary["files_with_unresolved_references"] += 1
        if file_ambiguous:
            ambiguous.append({
                "path": r,
                "reference_count": sum(file_ambiguous.values()),
                "references": [
                    {"reference": ref, "count": count}
                    for ref, count in sorted(file_ambiguous.items())
                ],
            })
            summary["ambiguous_reference_count"] += sum(file_ambiguous.values())
            summary["files_with_ambiguous_references"] += 1
    return {
        "version": 1,
        "revision_context": "rev0830-session-patch-over-rev0829-over-rev0826",
        "mode": "planned_or_applied_safe_unique_suffix_rewrites",
        "policy": {
            "rewritten_when": "absolute cloud/container path has exactly one shipped relative target by longest suffix match",
            "left_unchanged_when": "no shipped target is found, or suffix match is ambiguous",
            "candidate_prefixes": list(ALLOW_PREFIXES),
            "regex": PATH_RE.pattern,
        },
        "summary": {
            "files_with_rewrites": summary["files_with_rewrites"],
            "rewrite_reference_count": summary["rewrite_reference_count"],
            "unique_rewrite_pairs": summary["unique_rewrite_pairs"],
            "files_with_unresolved_references": summary["files_with_unresolved_references"],
            "unresolved_reference_count": summary["unresolved_reference_count"],
            "files_with_ambiguous_references": summary["files_with_ambiguous_references"],
            "ambiguous_reference_count": summary["ambiguous_reference_count"],
        },
        "rows": rows,
        "unresolved_or_external_rows": external_or_unresolved,
        "ambiguous_rows": ambiguous,
        "applier": "scripts/apply_path_portability_rewrites.py",
        "validator": "scripts/validate_path_portability_rewrite.py",
    }


def apply_plan(plan: dict[str, Any], root: Path = ROOT) -> dict[str, Any]:
    for row in plan["rows"]:
        path = root / row["path"]
        text = path.read_text(encoding="utf-8")
        for repl in row["replacements"]:
            text = text.replace(repl["from"], repl["to"])
        path.write_text(text, encoding="utf-8")
        row["new_sha256"] = sha256(path)
    plan["mode"] = "applied_safe_unique_suffix_rewrites"
    return plan


def render_markdown(plan: dict[str, Any]) -> str:
    s = plan["summary"]
    lines = [
        "# Path portability rewrite rev0830",
        "",
        "This surface records concrete content rewrites from build-host absolute paths to shipped archive-relative paths. It is deliberately limited to references whose trailing path components resolve to exactly one file in the archive.",
        "",
        f"- Mode: `{plan['mode']}`",
        f"- Files rewritten: **{s['files_with_rewrites']}**",
        f"- Absolute references rewritten: **{s['rewrite_reference_count']}**",
        f"- Unique old→new pairs: **{s['unique_rewrite_pairs']}**",
        f"- Unresolved/external references left unchanged: **{s['unresolved_reference_count']}** in **{s['files_with_unresolved_references']}** files",
        f"- Ambiguous references left unchanged: **{s['ambiguous_reference_count']}** in **{s['files_with_ambiguous_references']}** files",
        "",
        "## Why this is safe enough for a patch",
        "",
        "The old references were host coordinates such as `/mnt/data/...`. The new references name payload files shipped inside this archive. The rewrite does not alter referenced artifact digests; it only replaces non-portable coordinates when a unique shipped target exists.",
        "",
        "## Rewritten files",
        "",
        "| Path | Refs rewritten | Unique pairs | New SHA-256 |",
        "| --- | ---: | ---: | --- |",
    ]
    for row in plan["rows"]:
        new_sha = row.get("new_sha256", "not-yet-applied")
        lines.append(f"| `{row['path']}` | {row['replacement_count']} | {row['unique_replacement_count']} | `{new_sha}` |")
    lines.extend([
        "",
        "## Remaining unresolved/external references",
        "",
        "| Path | References | Sample |",
        "| --- | ---: | --- |",
    ])
    for row in plan["unresolved_or_external_rows"]:
        sample = "<br>".join(f"`{entry['reference']}` × {entry['count']}" for entry in row["references"][:4])
        lines.append(f"| `{row['path']}` | {row['reference_count']} | {sample} |")
    lines.extend([
        "",
        "## Remaining ambiguous references",
        "",
        "| Path | References | Sample |",
        "| --- | ---: | --- |",
    ])
    for row in plan["ambiguous_rows"]:
        sample = "<br>".join(f"`{entry['reference']}` × {entry['count']}" for entry in row["references"][:4])
        lines.append(f"| `{row['path']}` | {row['reference_count']} | {sample} |")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="rewrite safe references and emit ledger")
    args = parser.parse_args()
    plan = plan_rewrites(ROOT)
    if args.apply:
        plan = apply_plan(plan, ROOT)
        JSON_OUT.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        MD_OUT.write_text(render_markdown(plan), encoding="utf-8")
    print(
        "path-portability-rewrite: "
        f"{'APPLIED' if args.apply else 'PLANNED'} "
        f"{plan['summary']['rewrite_reference_count']} refs in {plan['summary']['files_with_rewrites']} files; "
        f"left {plan['summary']['unresolved_reference_count']} unresolved and "
        f"{plan['summary']['ambiguous_reference_count']} ambiguous"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
