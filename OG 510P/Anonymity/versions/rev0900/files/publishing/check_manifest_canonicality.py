#!/usr/bin/env python3
"""Check canonical manifest formatting, order, and cross-surface agreement."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import sys
from typing import Any

SHA_LINE_RE = re.compile(r"^[0-9a-f]{64}  [^\n\r]+$")
HEX_RE = re.compile(r"^[0-9a-f]{64}$")
ALLOWED_UNLISTED = {"MANIFEST.sha256"}


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def tree_files(root: pathlib.Path) -> list[str]:
    return sorted(p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file())


def parse_sha_manifest(path: pathlib.Path) -> tuple[list[dict[str, str]], list[dict[str, Any]]]:
    entries: list[dict[str, str]] = []
    failures: list[dict[str, Any]] = []
    raw = path.read_text(encoding="utf-8")
    if raw and not raw.endswith("\n"):
        failures.append({"category": "manifest_sha256_missing_final_lf", "path": "MANIFEST.sha256"})
    for line_no, line in enumerate(raw.splitlines(), 1):
        if not line:
            failures.append({"category": "manifest_sha256_blank_line", "line": line_no})
            continue
        if not SHA_LINE_RE.match(line):
            failures.append({"category": "manifest_sha256_line_not_canonical", "line": line_no, "line_text": line[:180]})
            continue
        digest, rel = line.split("  ", 1)
        entries.append({"sha256": digest, "path": rel})
    return entries, failures


def safe_manifest_path(rel: str) -> bool:
    return bool(rel) and not rel.startswith(("/", "./", "../")) and "\\" not in rel and "/../" not in rel and not rel.endswith("/")


def check(root: pathlib.Path) -> dict[str, Any]:
    release = load_json(root / "RELEASE_MANIFEST.json")
    failures: list[dict[str, Any]] = []
    manifest_path = root / "MANIFEST.json"
    sha_path = root / "MANIFEST.sha256"

    try:
        manifest = load_json(manifest_path)
    except Exception as exc:
        manifest = {}
        failures.append({"category": "manifest_json_parse_failure", "detail": str(exc)})

    files = manifest.get("files", []) if isinstance(manifest, dict) else []
    if set(manifest.keys()) != {"files"} if isinstance(manifest, dict) else True:
        failures.append({"category": "manifest_json_unexpected_keys", "keys": sorted(manifest.keys()) if isinstance(manifest, dict) else []})
    if not isinstance(files, list) or not all(isinstance(x, str) for x in files):
        failures.append({"category": "manifest_json_files_not_string_array"})
        files = [str(x) for x in files] if isinstance(files, list) else []

    expected_json_text = json.dumps({"files": files}, indent=2) + "\n"
    try:
        actual_json_text = manifest_path.read_text(encoding="utf-8")
        if actual_json_text != expected_json_text:
            failures.append({"category": "manifest_json_not_canonical_pretty_serialization"})
    except Exception as exc:
        failures.append({"category": "manifest_json_read_failure", "detail": str(exc)})

    if files != sorted(files):
        failures.append({"category": "manifest_json_files_not_sorted"})
    duplicates = sorted({p for p in files if files.count(p) > 1})
    if duplicates:
        failures.append({"category": "manifest_json_duplicate_paths", "paths": duplicates[:50], "count": len(duplicates)})
    unsafe = sorted(p for p in files if not safe_manifest_path(p))
    if unsafe:
        failures.append({"category": "manifest_json_unsafe_paths", "paths": unsafe[:50], "count": len(unsafe)})

    actual_tree = tree_files(root)
    missing_from_json = sorted(set(actual_tree) - set(files))
    extra_in_json = sorted(set(files) - set(actual_tree))
    if missing_from_json:
        failures.append({"category": "manifest_json_missing_tree_files", "paths": missing_from_json[:50], "count": len(missing_from_json)})
    if extra_in_json:
        failures.append({"category": "manifest_json_lists_absent_files", "paths": extra_in_json[:50], "count": len(extra_in_json)})

    sha_entries, sha_failures = parse_sha_manifest(sha_path)
    failures.extend(sha_failures)
    sha_paths = [entry["path"] for entry in sha_entries]
    sha_digests = [entry["sha256"] for entry in sha_entries]
    if sha_paths != sorted(sha_paths):
        failures.append({"category": "manifest_sha256_paths_not_sorted"})
    sha_dupes = sorted({p for p in sha_paths if sha_paths.count(p) > 1})
    if sha_dupes:
        failures.append({"category": "manifest_sha256_duplicate_paths", "paths": sha_dupes[:50], "count": len(sha_dupes)})
    sha_unsafe = sorted(p for p in sha_paths if not safe_manifest_path(p))
    if sha_unsafe:
        failures.append({"category": "manifest_sha256_unsafe_paths", "paths": sha_unsafe[:50], "count": len(sha_unsafe)})
    malformed_digests = [digest for digest in sha_digests if not HEX_RE.match(digest)]
    if malformed_digests:
        failures.append({"category": "manifest_sha256_malformed_digests", "count": len(malformed_digests)})

    expected_sha_paths = sorted(p for p in files if p not in ALLOWED_UNLISTED)
    if sha_paths != expected_sha_paths:
        failures.append({
            "category": "manifest_sha256_path_set_mismatch",
            "missing_from_sha256": sorted(set(expected_sha_paths) - set(sha_paths))[:50],
            "extra_in_sha256": sorted(set(sha_paths) - set(expected_sha_paths))[:50],
        })

    mismatches: list[dict[str, str]] = []
    for entry in sha_entries:
        rel = entry["path"]
        path = root / rel
        if not path.exists():
            continue
        actual = sha256_file(path)
        if actual != entry["sha256"]:
            mismatches.append({"path": rel, "expected": entry["sha256"], "actual": actual})
    if mismatches:
        failures.append({"category": "manifest_sha256_digest_mismatch", "mismatches": mismatches[:20], "count": len(mismatches)})

    checks = [
        {"name": "manifest_json_canonical_shape", "status": "pass" if not any(f["category"].startswith("manifest_json") and f["category"] not in {"manifest_json_missing_tree_files", "manifest_json_lists_absent_files"} for f in failures) else "fail"},
        {"name": "manifest_json_matches_tree", "status": "pass" if not missing_from_json and not extra_in_json else "fail"},
        {"name": "manifest_sha256_canonical_shape", "status": "pass" if not any(f["category"].startswith("manifest_sha256") and f["category"] != "manifest_sha256_digest_mismatch" for f in failures) else "fail"},
        {"name": "manifest_sha256_digests_match", "status": "pass" if not mismatches else "fail"},
    ]
    return {
        "status": "pass" if not failures else "fail",
        "generated_for_revision": release["revision"],
        "checked_bundle": release["bundle"],
        "publication_authorized": False,
        "manifest_json": "MANIFEST.json",
        "manifest_sha256": "MANIFEST.sha256",
        "allowed_unlisted_paths": sorted(ALLOWED_UNLISTED),
        "checks": checks,
        "failures": failures[:100],
        "summary": {
            "checks_failed": len(failures),
            "manifest_json_file_count": len(files),
            "tree_file_count": len(actual_tree),
            "manifest_sha256_entry_count": len(sha_entries),
            "allowed_unlisted_count": len(ALLOWED_UNLISTED),
            "digest_mismatch_count": len(mismatches),
            "duplicate_json_path_count": len(duplicates),
            "duplicate_sha256_path_count": len(sha_dupes),
        },
        "fail_closed_rule": "If manifest canonicality fails, default to no publication and regenerate MANIFEST.json/MANIFEST.sha256 through the canonical rebuild path before packaging.",
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
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
