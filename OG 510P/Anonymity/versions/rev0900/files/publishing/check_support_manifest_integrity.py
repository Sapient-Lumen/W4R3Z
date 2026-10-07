#!/usr/bin/env python3
"""Fail-closed digest and path-base validation for nested support manifests.

This guards the seam where a top-level MANIFEST can be internally correct while
an artifact-local support_manifest.json carries stale per-file digest claims.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import pathlib
import sys
from typing import Any

ALLOWED_BASES = {"artifact_root", "paper_root", "repo_root"}

# High-volume worked-example JSON artifacts are intended to be machine-read, not
# human-edited.  Keep them canonical/compact so rebuilds do not reintroduce
# megabytes of whitespace-only archive mass.
COMPACT_WORKED_EXAMPLE_JSON = {
    "example_public_request_response_packet_refresh_response_menus.json",
    "example_public_request_response_packet_refresh_response_packet_closure_verdicts.json",
    "example_public_request_response_packet_refresh_response_packets.json",
    "example_question_routes.json",
    "example_series_spine.json",
}


POINTER_FORMAT = "worked-example-json-payload-pointer-v1"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def logical_manifest_target_bytes(manifest_path: pathlib.Path, entry: dict[str, Any], target: pathlib.Path) -> tuple[bytes, list[dict[str, Any]], dict[str, Any]]:
    """Return logical bytes for a support-manifest row.

    For ordinary rows the logical bytes are the target bytes.  For Paper17
    payload-pointer rows, the manifest-level sha256 intentionally remains the
    digest of the decompressed JSON payload so historical readers and packet cuts
    can keep addressing the original logical artifact path.
    """
    data = target.read_bytes()
    diagnostics: list[dict[str, Any]] = []
    metadata: dict[str, Any] = {"storage_kind": "inline"}
    try:
        pointer = json.loads(data)
    except Exception:
        return data, diagnostics, metadata
    if not (isinstance(pointer, dict) and pointer.get("offloaded_payload_pointer") is True):
        return data, diagnostics, metadata
    metadata = {"storage_kind": "offloaded_payload_pointer", "payload_path": pointer.get("payload_path")}
    raw_path = entry.get("path")
    if pointer.get("pointer_format") != POINTER_FORMAT:
        diagnostics.append({"problem": "payload-pointer-format-mismatch", "path": raw_path, "actual": pointer.get("pointer_format"), "expected": POINTER_FORMAT})
    if pointer.get("logical_path") != raw_path:
        diagnostics.append({"problem": "payload-pointer-logical-path-mismatch", "path": raw_path, "logical_path": pointer.get("logical_path")})
    if pointer.get("encoding") != "gzip-json-utf8-mtime0":
        diagnostics.append({"problem": "payload-pointer-encoding-mismatch", "path": raw_path, "encoding": pointer.get("encoding")})
    payload_rel = str(pointer.get("payload_path", ""))
    payload_path = (manifest_path.parent / payload_rel).resolve()
    try:
        payload_path.relative_to(manifest_path.parent.resolve())
    except Exception:
        diagnostics.append({"problem": "payload-path-escapes-artifact-root", "path": raw_path, "payload_path": payload_rel})
        return data, diagnostics, metadata
    if not payload_path.exists() or not payload_path.is_file():
        diagnostics.append({"problem": "payload-file-missing", "path": raw_path, "payload_path": payload_rel})
        return data, diagnostics, metadata
    payload_bytes = payload_path.read_bytes()
    if sha256_bytes(payload_bytes) != pointer.get("payload_sha256"):
        diagnostics.append({"problem": "payload-storage-sha256-mismatch", "path": raw_path, "payload_path": payload_rel, "declared": pointer.get("payload_sha256"), "actual": sha256_bytes(payload_bytes)})
    try:
        logical = gzip.decompress(payload_bytes)
    except Exception as exc:  # noqa: BLE001
        diagnostics.append({"problem": "payload-gzip-decompress-failed", "path": raw_path, "payload_path": payload_rel, "detail": str(exc)})
        return data, diagnostics, metadata
    if sha256_bytes(logical) != pointer.get("logical_sha256"):
        diagnostics.append({"problem": "payload-logical-sha256-mismatch", "path": raw_path, "declared": pointer.get("logical_sha256"), "actual": sha256_bytes(logical)})
    try:
        if len(logical) != int(pointer.get("logical_bytes", -1)):
            diagnostics.append({"problem": "payload-logical-bytes-mismatch", "path": raw_path, "declared": pointer.get("logical_bytes"), "actual": len(logical)})
    except Exception:
        diagnostics.append({"problem": "payload-logical-bytes-malformed", "path": raw_path, "declared": pointer.get("logical_bytes")})
    return logical, diagnostics, metadata


def canonical_json_byte_pair_from_bytes(data: bytes) -> tuple[bytes, bytes]:
    obj = json.loads(data.decode("utf-8"))
    compact = (json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    pretty = (json.dumps(obj, indent=2, sort_keys=True) + "\n").encode("utf-8")
    return compact, pretty


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def relpath(path: pathlib.Path, root: pathlib.Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def infer_repo_relative_path(manifest_path: pathlib.Path, entry_path: str, root: pathlib.Path) -> str:
    resolved = (manifest_path.parent / entry_path).resolve()
    return relpath(resolved, root)


def expected_repo_relative_path(manifest_path: pathlib.Path, entry: dict[str, Any], root: pathlib.Path) -> str | None:
    """Return the repo-relative path implied by explicit base semantics.

    Existing manifests historically used paths relative to the artifact root,
    including ../README.md for paper-root helpers.  The rev0805 contract keeps
    backward-compatible `path` values but requires explicit `base` and
    `repo_relative_path` fields so new validators do not guess the base.
    """
    base = entry.get("base")
    raw = entry.get("path")
    if not isinstance(raw, str):
        return None
    artifact_root = manifest_path.parent.resolve()
    paper_root = artifact_root.parent
    if base == "artifact_root":
        return relpath(artifact_root / raw, root)
    if base == "paper_root":
        # Accept both the old ../ helper spelling and a normalized paper-root spelling.
        normalized = raw[3:] if raw.startswith("../") else raw
        return relpath(paper_root / normalized, root)
    if base == "repo_root":
        return pathlib.PurePosixPath(raw).as_posix()
    return None


def check_manifest(root: pathlib.Path, manifest_path: pathlib.Path) -> dict[str, Any]:
    rel_manifest = relpath(manifest_path, root)
    try:
        manifest = load_json(manifest_path)
    except Exception as exc:  # noqa: BLE001 - report fail-closed diagnostic
        return {
            "manifest": rel_manifest,
            "status": "fail",
            "manifest_id": "",
            "file_count": 0,
            "failures": [{"path": rel_manifest, "problem": "manifest-json-load-failed", "detail": str(exc)}],
            "warnings": [],
        }

    failures: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    seen_paths: set[str] = set()
    compact_json_checked = 0
    compact_json_savings_bytes = 0
    payload_pointer_rows = 0
    payload_pointer_logical_bytes = 0
    payload_pointer_storage_bytes = 0

    files = manifest.get("files", [])
    if not isinstance(files, list):
        failures.append({"path": rel_manifest, "problem": "files-not-list"})
        files = []

    for index, entry in enumerate(files):
        if not isinstance(entry, dict):
            failures.append({"index": index, "problem": "entry-not-object"})
            continue
        raw_path = entry.get("path")
        declared_sha = entry.get("sha256")
        base = entry.get("base")
        repo_rel = entry.get("repo_relative_path")
        if not isinstance(raw_path, str) or not raw_path:
            failures.append({"index": index, "problem": "missing-path"})
            continue
        if raw_path in seen_paths:
            failures.append({"index": index, "path": raw_path, "problem": "duplicate-path"})
        seen_paths.add(raw_path)
        if not isinstance(declared_sha, str) or len(declared_sha) != 64:
            failures.append({"index": index, "path": raw_path, "problem": "missing-or-malformed-sha256", "declared": declared_sha})
            continue
        if base not in ALLOWED_BASES:
            failures.append({"index": index, "path": raw_path, "problem": "missing-or-invalid-base", "base": base})
        implied_rel = expected_repo_relative_path(manifest_path, entry, root)
        inferred_rel = infer_repo_relative_path(manifest_path, raw_path, root)
        if repo_rel is None:
            failures.append({"index": index, "path": raw_path, "problem": "missing-repo-relative-path", "inferred_repo_relative_path": inferred_rel})
            repo_rel = implied_rel or inferred_rel
        elif not isinstance(repo_rel, str) or not repo_rel:
            failures.append({"index": index, "path": raw_path, "problem": "malformed-repo-relative-path", "repo_relative_path": repo_rel})
            repo_rel = implied_rel or inferred_rel
        if implied_rel is not None and repo_rel != implied_rel:
            failures.append({"index": index, "path": raw_path, "problem": "base-repo-relative-path-mismatch", "base": base, "repo_relative_path": repo_rel, "expected": implied_rel})
        if implied_rel is None and repo_rel != inferred_rel:
            warnings.append({"index": index, "path": raw_path, "problem": "legacy-inferred-path-differs", "repo_relative_path": repo_rel, "legacy_inferred": inferred_rel})
        target_rel = repo_rel if isinstance(repo_rel, str) else inferred_rel
        try:
            target = (root / target_rel).resolve()
            target.relative_to(root.resolve())
        except Exception:
            failures.append({"index": index, "path": raw_path, "problem": "resolved-path-escapes-root", "repo_relative_path": target_rel})
            continue
        if not target.exists() or not target.is_file():
            failures.append({"index": index, "path": raw_path, "problem": "resolved-file-missing", "repo_relative_path": target_rel})
            continue
        logical_bytes, pointer_diagnostics, storage_metadata = logical_manifest_target_bytes(manifest_path, entry, target)
        for diagnostic in pointer_diagnostics:
            failures.append({"index": index, "repo_relative_path": target_rel, **diagnostic})
        if storage_metadata.get("storage_kind") == "offloaded_payload_pointer":
            payload_pointer_rows += 1
            payload_pointer_logical_bytes += len(logical_bytes)
            try:
                payload_pointer_storage_bytes += int(entry.get("storage_bytes") or 0)
            except Exception:
                pass
        actual_sha = sha256_bytes(logical_bytes)
        if actual_sha != declared_sha:
            failures.append({"index": index, "path": raw_path, "problem": "sha256-mismatch", "repo_relative_path": target_rel, "declared": declared_sha, "actual": actual_sha, **storage_metadata})
        if base == "artifact_root" and raw_path in COMPACT_WORKED_EXAMPLE_JSON:
            compact_json_checked += 1
            try:
                compact_bytes, pretty_bytes = canonical_json_byte_pair_from_bytes(logical_bytes)
                compact_json_savings_bytes += max(0, len(pretty_bytes) - len(compact_bytes))
                if logical_bytes != compact_bytes:
                    failures.append({
                        "index": index,
                        "path": raw_path,
                        "problem": "compact-json-canonicality-mismatch",
                        "repo_relative_path": target_rel,
                        "actual_bytes": len(logical_bytes),
                        "canonical_compact_bytes": len(compact_bytes),
                        "pretty_equivalent_bytes": len(pretty_bytes),
                        **storage_metadata,
                    })
            except Exception as exc:  # noqa: BLE001 - fail closed with path-local detail
                failures.append({"index": index, "path": raw_path, "problem": "compact-json-check-failed", "detail": str(exc)})

    return {
        "manifest": rel_manifest,
        "status": "pass" if not failures else "fail",
        "manifest_id": manifest.get("manifest_id", "") if isinstance(manifest, dict) else "",
        "file_count": len(files),
        "compact_json_checked": compact_json_checked,
        "compact_json_savings_bytes": compact_json_savings_bytes,
        "payload_pointer_rows": payload_pointer_rows,
        "payload_pointer_logical_bytes": payload_pointer_logical_bytes,
        "payload_pointer_storage_bytes": payload_pointer_storage_bytes,
        "payload_pointer_hot_path_bytes_saved": max(0, payload_pointer_logical_bytes - payload_pointer_storage_bytes),
        "failures": failures,
        "warnings": warnings,
    }


def check(root: pathlib.Path, manifests: list[str] | None = None) -> dict[str, Any]:
    release = load_json(root / "RELEASE_MANIFEST.json")
    if manifests:
        manifest_paths = [(root / item).resolve() for item in manifests]
    else:
        manifest_paths = sorted(p.resolve() for p in root.rglob("support_manifest.json") if p.is_file())
    results = [check_manifest(root, path) for path in manifest_paths]
    failed = [item for item in results if item["status"] == "fail"]
    return {
        "status": "pass" if not failed else "fail",
        "generated_for_revision": release["revision"],
        "checked_bundle": release["bundle"],
        "publication_authorized": False,
        "checked_root": ".",
        "checked_manifest_count": len(results),
        "manifests": results,
        "summary": {
            "checks_passed": len(results) - len(failed),
            "checks_failed": len(failed),
            "file_rows_checked": sum(item.get("file_count", 0) for item in results),
            "failure_count": sum(len(item.get("failures", [])) for item in results),
            "warning_count": sum(len(item.get("warnings", [])) for item in results),
            "compact_json_checked": sum(item.get("compact_json_checked", 0) for item in results),
            "compact_json_savings_bytes": sum(item.get("compact_json_savings_bytes", 0) for item in results),
            "payload_pointer_rows": sum(item.get("payload_pointer_rows", 0) for item in results),
            "payload_pointer_logical_bytes": sum(item.get("payload_pointer_logical_bytes", 0) for item in results),
            "payload_pointer_storage_bytes": sum(item.get("payload_pointer_storage_bytes", 0) for item in results),
            "payload_pointer_hot_path_bytes_saved": sum(item.get("payload_pointer_hot_path_bytes_saved", 0) for item in results),
        },
        "fail_closed_rule": "If nested support-manifest integrity fails, default to no publication and repair or regenerate the local support manifest before trusting artifact claims; high-volume worked-example JSON must remain canonical/compact rather than whitespace-bloated.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--manifest", action="append", default=None, help="Optional repo-relative support_manifest.json path. May be repeated.")
    parser.add_argument("--write-report", default="")
    args = parser.parse_args()

    root = pathlib.Path(args.root).resolve()
    report = check(root, args.manifest)
    text = json.dumps(report, indent=2) + "\n"
    if args.write_report:
        out = (root / args.write_report).resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    sys.stdout.write(text)
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
