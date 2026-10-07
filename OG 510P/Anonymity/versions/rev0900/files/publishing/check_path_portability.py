#!/usr/bin/env python3
"""Check archive path portability across common filesystems and zip readers.

This guard is intentionally stricter than Python/pathlib existence checks.  It
looks for path names that are valid on the current POSIX filesystem but fragile
for reviewers on case-insensitive filesystems, Windows zip extractors, or Unicode
normalizing filesystems.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import unicodedata
from collections import defaultdict
from typing import Any

FORBIDDEN_CHARS = set('<>:"\\|?*')
RESERVED_WINDOWS_NAMES = {
    "CON", "PRN", "AUX", "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}
MAX_PATH_BYTES = 260
MAX_COMPONENT_BYTES = 240
MAX_COMPONENT_CHARS = 240
CONTROL_RE = re.compile(r"[\x00-\x1f\x7f]")


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def repo_files(root: pathlib.Path) -> list[str]:
    return sorted(p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file())


def manifest_json_files(root: pathlib.Path) -> list[str]:
    try:
        data = load_json(root / "MANIFEST.json")
    except FileNotFoundError:
        return []
    files = data.get("files", [])
    return [str(item) for item in files] if isinstance(files, list) else []


def manifest_sha256_paths(root: pathlib.Path) -> list[str]:
    path = root / "MANIFEST.sha256"
    if not path.exists():
        return []
    out: list[str] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        if "  " in line:
            out.append(line.split("  ", 1)[1])
        else:
            out.append(line)
    return out


def base_without_extension(component: str) -> str:
    # Windows reserved names are reserved even when followed by an extension.
    return component.split(".", 1)[0].upper()


def path_findings(rel: str) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    encoded_path_len = len(rel.encode("utf-8"))
    if rel.startswith("/"):
        findings.append({"category": "absolute_path", "path": rel})
    if "\\" in rel:
        findings.append({"category": "backslash_separator_or_escape", "path": rel})
    if rel in {"", "."} or "//" in rel:
        findings.append({"category": "empty_path_component", "path": rel})
    if encoded_path_len > MAX_PATH_BYTES:
        findings.append({"category": "path_too_long", "path": rel, "path_bytes": encoded_path_len, "max_path_bytes": MAX_PATH_BYTES})
    if CONTROL_RE.search(rel):
        findings.append({"category": "control_character", "path": rel})
    if any(ch in FORBIDDEN_CHARS for ch in rel):
        chars = sorted({ch for ch in rel if ch in FORBIDDEN_CHARS})
        findings.append({"category": "windows_forbidden_character", "path": rel, "characters": chars})
    if unicodedata.normalize("NFC", rel) != rel:
        findings.append({"category": "not_unicode_nfc", "path": rel})
    for component in rel.split("/"):
        comp_bytes = len(component.encode("utf-8"))
        if component in {"", ".", ".."}:
            findings.append({"category": "unsafe_component", "path": rel, "component": component})
        if component.endswith(" ") or component.endswith("."):
            findings.append({"category": "trailing_space_or_dot_component", "path": rel, "component": component})
        if component.startswith(" "):
            findings.append({"category": "leading_space_component", "path": rel, "component": component})
        if len(component) > MAX_COMPONENT_CHARS or comp_bytes > MAX_COMPONENT_BYTES:
            findings.append({"category": "component_too_long", "path": rel, "component": component, "component_chars": len(component), "component_bytes": comp_bytes, "max_component_bytes": MAX_COMPONENT_BYTES})
        if base_without_extension(component) in RESERVED_WINDOWS_NAMES:
            findings.append({"category": "windows_reserved_component", "path": rel, "component": component})
    return findings


def collision_rows(paths: list[str], normalizer) -> list[dict[str, Any]]:
    buckets: dict[str, list[str]] = defaultdict(list)
    for rel in paths:
        buckets[normalizer(rel)].append(rel)
    return [{"normalized": key, "paths": vals} for key, vals in sorted(buckets.items()) if len(vals) > 1]


def check(root: pathlib.Path) -> dict[str, Any]:
    release = load_json(root / "RELEASE_MANIFEST.json")
    paths = repo_files(root)
    manifest_paths = manifest_json_files(root)
    sha_paths = manifest_sha256_paths(root)
    findings: list[dict[str, Any]] = []
    for rel in paths:
        findings.extend(path_findings(rel))

    exact_duplicates = sorted({p for p in paths if paths.count(p) > 1})
    manifest_duplicates = sorted({p for p in manifest_paths if manifest_paths.count(p) > 1})
    sha_duplicates = sorted({p for p in sha_paths if sha_paths.count(p) > 1})
    nfc_collisions = collision_rows(paths, lambda p: unicodedata.normalize("NFC", p))
    casefold_collisions = collision_rows(paths, lambda p: unicodedata.normalize("NFC", p).casefold())
    manifest_sorted = manifest_paths == sorted(manifest_paths)
    sha_sorted = sha_paths == sorted(sha_paths)

    if exact_duplicates:
        findings.append({"category": "duplicate_repo_paths", "paths": exact_duplicates[:20], "count": len(exact_duplicates)})
    if manifest_duplicates:
        findings.append({"category": "duplicate_manifest_json_paths", "paths": manifest_duplicates[:20], "count": len(manifest_duplicates)})
    if sha_duplicates:
        findings.append({"category": "duplicate_manifest_sha256_paths", "paths": sha_duplicates[:20], "count": len(sha_duplicates)})
    for row in nfc_collisions[:20]:
        findings.append({"category": "unicode_nfc_collision", **row})
    for row in casefold_collisions[:20]:
        findings.append({"category": "casefold_collision", **row})
    if not manifest_sorted:
        findings.append({"category": "manifest_json_not_sorted"})
    if not sha_sorted:
        findings.append({"category": "manifest_sha256_not_sorted"})

    max_path = max((len(p.encode("utf-8")), p) for p in paths) if paths else (0, "")
    max_component = max(((len(c.encode("utf-8")), c, p) for p in paths for c in p.split("/")), default=(0, "", ""))
    summary = {
        "checks_failed": len(findings),
        "path_count": len(paths),
        "manifest_json_path_count": len(manifest_paths),
        "manifest_sha256_path_count": len(sha_paths),
        "max_path_bytes": max_path[0],
        "max_path": max_path[1],
        "max_component_bytes": max_component[0],
        "max_component": max_component[1],
        "max_component_path": max_component[2],
        "nfc_collision_count": len(nfc_collisions),
        "casefold_collision_count": len(casefold_collisions),
        "manifest_json_sorted": manifest_sorted,
        "manifest_sha256_sorted": sha_sorted,
        "policy": {
            "max_path_bytes": MAX_PATH_BYTES,
            "max_component_bytes": MAX_COMPONENT_BYTES,
            "max_component_chars": MAX_COMPONENT_CHARS,
            "windows_reserved_names_rejected": True,
            "windows_forbidden_characters_rejected": ''.join(sorted(FORBIDDEN_CHARS)),
            "unicode_normalization": "NFC",
            "casefold_collision_free": True,
        },
    }
    return {
        "status": "pass" if not findings else "fail",
        "generated_for_revision": release["revision"],
        "checked_bundle": release["bundle"],
        "publication_authorized": False,
        "checked_root": ".",
        "path_policy": summary["policy"],
        "findings": findings[:100],
        "summary": summary,
        "fail_closed_rule": "If path portability fails, default to no publication and rename or quarantine fragile paths before building a public zip.",
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
    print(text, end="")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
