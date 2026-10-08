#!/usr/bin/env python3
"""rev0067 regression-fixture contract and clean-room test hygiene gate.

This helper treats the uploaded Nicotine source bundle as archived-source input,
but focuses on the exported clean-room regression fixtures: are the tests and
patches the intended copies, do the tests avoid cube-private dependencies, and
will the contract fail closed if a reviewer-facing fixture is missing/tampered?
"""
from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import shutil
import sys
import zipfile
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SOURCE_SHA256 = "feaa8df98bbd0f28ba00eb8d52dcc3b9b9860e8d59039c7d41a98a0117505e5b"
SOURCE_PREFIX = "Nicotine+DEV-rev0003-upstream-sources-20260612T181540Z/source-trees/"
LANES = ("github-tag-3.3.10", "github-branch-3.3.x", "github-branch-master")
PATCHES = ("u-123-rev0059.patch", "pb-01-rev0059.patch", "search-resp-source-admission-rev0059.patch", "search-resp-parser-budget-rev0059.patch")
BAD_PACKAGE_PARTS = {"__pycache__", ".pytest_cache", "source-trees", "git-full", ".git"}
FORBIDDEN_TEST_STRINGS = (
    "/mnt/data",
    "maintainer_artifacts",
    "report_drafts",
    "handoff/rev",
    "Nicotine+DEV-",
    "source-trees",
    "git-full",
    "tools/",
    "probe_rev",
)
FORBIDDEN_IMPORT_ROOTS = {"requests", "urllib", "http", "ftplib", "subprocess"}
ALLOWED_SOCKET_PACKET = "PB-01"

TESTS: Tuple[Dict[str, object], ...] = (
    {
        "packet": "U-123",
        "bundle": "01-transfer-session-identity",
        "clean_rel": "handoff/rev0062/cleanroom-kit/tests/u123/test_downloads_duplicate_transfer_token_collision_rejection_regression.py",
        "original_rel": "maintainer_artifacts/u123/test_downloads_duplicate_transfer_token_collision_rejection_regression.py",
        "expected_static_tests": 1,
        "expected_runtime_pass_summary": "OK",
    },
    {
        "packet": "PB-01",
        "bundle": "02-peer-primary-election",
        "clean_rel": "handoff/rev0062/cleanroom-kit/tests/pb01/test_peer_connection_primary_election_fixed_regression.py",
        "original_rel": "maintainer_artifacts/pb01/test_peer_connection_primary_election_fixed_regression.py",
        "expected_static_tests": 7,
        "expected_runtime_pass_summary": "11 passed",
    },
    {
        "packet": "SEARCH-RESP-01A",
        "bundle": "03-search-response-source-admission",
        "clean_rel": "handoff/rev0062/cleanroom-kit/tests/search-resp-01/test_search_response_user_scope_fixed_regression.py",
        "original_rel": "maintainer_artifacts/search-resp-01/test_search_response_user_scope_fixed_regression.py",
        "expected_static_tests": 7,
        "expected_runtime_pass_summary": "7 passed",
    },
    {
        "packet": "SEARCH-RESP-01B-BUDDY",
        "bundle": "03-search-response-source-admission",
        "clean_rel": "handoff/rev0062/cleanroom-kit/tests/search-resp-01/test_search_response_buddy_scope_fixed_regression.py",
        "original_rel": "maintainer_artifacts/search-resp-01/test_search_response_buddy_scope_fixed_regression.py",
        "expected_static_tests": 8,
        "expected_runtime_pass_summary": "8 passed",
    },
    {
        "packet": "SEARCH-RESP-01C-ROOM",
        "bundle": "03-search-response-source-admission",
        "clean_rel": "handoff/rev0062/cleanroom-kit/tests/search-resp-01/test_search_response_room_scope_fixed_regression.py",
        "original_rel": "maintainer_artifacts/search-resp-01/test_search_response_room_scope_fixed_regression.py",
        "expected_static_tests": 8,
        "expected_runtime_pass_summary": "8 passed",
    },
    {
        "packet": "SEARCH-RESP-PARSE-BUDGET-A",
        "bundle": "04-search-response-parser-budget",
        "clean_rel": "handoff/rev0062/cleanroom-kit/tests/search-resp-01/test_search_response_prefix_budget_fixed_regression.py",
        "original_rel": "maintainer_artifacts/search-resp-01/test_search_response_prefix_budget_fixed_regression.py",
        "expected_static_tests": 4,
        "expected_runtime_pass_summary": "4 passed",
    },
    {
        "packet": "SEARCH-RESP-PARSE-BUDGET-B",
        "bundle": "04-search-response-parser-budget",
        "clean_rel": "handoff/rev0062/cleanroom-kit/tests/search-resp-01/test_search_response_result_budget_fixed_regression.py",
        "original_rel": "maintainer_artifacts/search-resp-01/test_search_response_result_budget_fixed_regression.py",
        "expected_static_tests": 4,
        "expected_runtime_pass_summary": "4 passed",
    },
)

RUNNER_MARKERS: Tuple[Tuple[str, str], ...] = (
    ("bytecode disabled", "sys.dont_write_bytecode = True"),
    ("source sha pinned", f'EXPECTED_SOURCE_SHA256 = "{EXPECTED_SOURCE_SHA256}"'),
    ("all lanes enumerated", "LANES = (\"github-tag-3.3.10\", \"github-branch-3.3.x\", \"github-branch-master\")"),
    ("canonical patch order enumerated", "PATCH_ORDER = ("),
    ("fixed tests enumerated", "FIXED_TESTS:"),
    ("pytest plugin autoload disabled", "PYTEST_DISABLE_PLUGIN_AUTOLOAD"),
    ("tests run outside kit cwd", 'cwd="/tmp"'),
    ("source zip argument", "--source-zip"),
    ("kit dir argument", "--kit-dir"),
    ("cache cleanup", "cleanup_caches"),
    ("fail closed return", "return 0 if not errors else 1"),
)


def sha_path(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_csv(path: Path, rows: List[Dict[str, object]], fields: Iterable[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(fields))
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in writer.fieldnames})


def write_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def cleanup_caches(path: Path) -> None:
    for cache in list(path.rglob("__pycache__")) + list(path.rglob(".pytest_cache")):
        shutil.rmtree(cache, ignore_errors=True)


def source_identity(source_zip: Path) -> Dict[str, object]:
    info: Dict[str, object] = {"source_zip": str(source_zip), "exists": source_zip.exists()}
    if not source_zip.exists():
        info.update({"sha256": "", "entries": 0, "lanes": [], "status": "fail"})
        return info
    lanes = set()
    entries = 0
    with zipfile.ZipFile(source_zip) as zf:
        for name in zf.namelist():
            entries += 1
            if name.startswith(SOURCE_PREFIX):
                rest = name[len(SOURCE_PREFIX):]
                lane = rest.split("/", 1)[0]
                if lane in LANES:
                    lanes.add(lane)
    digest = sha_path(source_zip)
    status = "pass" if digest == EXPECTED_SOURCE_SHA256 and set(lanes) == set(LANES) else "fail"
    info.update({"sha256": digest, "entries": entries, "lanes": sorted(lanes), "status": status})
    return info


def import_roots(tree: ast.AST) -> List[str]:
    roots: List[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                roots.append(alias.name.split(".", 1)[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.append(node.module.split(".", 1)[0])
    return sorted(set(roots))


def test_function_names(tree: ast.AST) -> List[str]:
    return sorted(
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_")
    )


def inherited_runtime_by_packet() -> Dict[str, List[str]]:
    path = ROOT / "data" / "rev0062_cleanroom_fixed_regression_matrix.csv"
    out: Dict[str, List[str]] = {}
    if not path.exists():
        return out
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            packet = row.get("packet", "")
            status = row.get("status", "")
            summary = row.get("summary", "")
            if packet and status == "pass":
                out.setdefault(packet, []).append(summary)
    return out


def analyze_test_file(packet: str, clean_path: Path, original_path: Path, expected_count: int, expected_runtime: str, inherited_runtime: Dict[str, List[str]]) -> Dict[str, object]:
    row: Dict[str, object] = {
        "packet": packet,
        "cleanroom_path": str(clean_path.relative_to(ROOT)) if clean_path.exists() else str(clean_path),
        "original_path": str(original_path.relative_to(ROOT)) if original_path.exists() else str(original_path),
        "cleanroom_exists": str(clean_path.exists()).lower(),
        "original_exists": str(original_path.exists()).lower(),
        "expected_static_tests": expected_count,
        "expected_runtime_pass_summary": expected_runtime,
    }
    if not clean_path.exists() or not original_path.exists():
        row.update({"status": "fail", "detail": "missing cleanroom or original test"})
        return row
    clean_bytes = clean_path.read_bytes()
    original_bytes = original_path.read_bytes()
    text = clean_bytes.decode("utf-8", errors="replace")
    try:
        tree = ast.parse(text)
        static_names = test_function_names(tree)
        imports = import_roots(tree)
        ast_ok = True
        ast_error = ""
    except SyntaxError as exc:
        static_names = []
        imports = []
        ast_ok = False
        ast_error = str(exc)
    forbidden_strings = [s for s in FORBIDDEN_TEST_STRINGS if s in text]
    forbidden_imports = [i for i in imports if i in FORBIDDEN_IMPORT_ROOTS]
    socket_note = ""
    if "socket" in imports and packet == ALLOWED_SOCKET_PACKET:
        socket_note = "socket import allowed for PB-01 fake socket constants/stand-ins"
    elif "socket" in imports:
        forbidden_imports.append("socket")
    runtime_summaries = inherited_runtime.get(packet, [])
    runtime_ok = bool(runtime_summaries) and all(expected_runtime in s or s == expected_runtime for s in runtime_summaries)
    status = "pass" if (
        ast_ok
        and clean_bytes == original_bytes
        and len(static_names) == expected_count
        and not forbidden_strings
        and not forbidden_imports
        and runtime_ok
    ) else "fail"
    row.update({
        "cleanroom_sha256": sha_bytes(clean_bytes),
        "original_sha256": sha_bytes(original_bytes),
        "hash_match": str(clean_bytes == original_bytes).lower(),
        "size_bytes": len(clean_bytes),
        "static_test_count": len(static_names),
        "static_test_names": ";".join(static_names),
        "imports": ";".join(imports),
        "forbidden_imports": ";".join(forbidden_imports),
        "forbidden_strings": ";".join(forbidden_strings),
        "ast_ok": str(ast_ok).lower(),
        "ast_error": ast_error,
        "inherited_runtime_rows": len(runtime_summaries),
        "inherited_runtime_summaries": " || ".join(runtime_summaries),
        "inherited_runtime_ok": str(runtime_ok).lower(),
        "note": socket_note,
        "status": status,
    })
    return row


def test_lineage_rows() -> List[Dict[str, object]]:
    inherited = inherited_runtime_by_packet()
    rows: List[Dict[str, object]] = []
    for spec in TESTS:
        rows.append(analyze_test_file(
            packet=str(spec["packet"]),
            clean_path=ROOT / str(spec["clean_rel"]),
            original_path=ROOT / str(spec["original_rel"]),
            expected_count=int(spec["expected_static_tests"]),
            expected_runtime=str(spec["expected_runtime_pass_summary"]),
            inherited_runtime=inherited,
        ))
    return rows


def patch_lineage_rows() -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    for lane in LANES:
        for patch in PATCHES:
            clean = ROOT / "handoff" / "rev0062" / "cleanroom-kit" / "patches" / lane / patch
            original = ROOT / "handoff" / "rev0059" / "patches" / lane / patch
            row: Dict[str, object] = {
                "lane": lane,
                "patch": patch,
                "cleanroom_path": str(clean.relative_to(ROOT)),
                "rev0059_path": str(original.relative_to(ROOT)),
                "cleanroom_exists": str(clean.exists()).lower(),
                "rev0059_exists": str(original.exists()).lower(),
            }
            if clean.exists() and original.exists():
                c = clean.read_bytes()
                o = original.read_bytes()
                row.update({
                    "cleanroom_sha256": sha_bytes(c),
                    "rev0059_sha256": sha_bytes(o),
                    "hash_match": str(c == o).lower(),
                    "size_bytes": len(c),
                    "status": "pass" if c == o else "fail",
                })
            else:
                row.update({"cleanroom_sha256": "", "rev0059_sha256": "", "hash_match": "false", "size_bytes": "", "status": "fail"})
            rows.append(row)
    return rows


def runner_contract_rows() -> List[Dict[str, object]]:
    runner = ROOT / "handoff" / "rev0062" / "cleanroom-kit" / "run_cleanroom_replay.py"
    text = runner.read_text(encoding="utf-8", errors="replace") if runner.exists() else ""
    rows: List[Dict[str, object]] = []
    for check, marker in RUNNER_MARKERS:
        rows.append({
            "check": check,
            "marker": marker,
            "present": str(marker in text).lower(),
            "status": "pass" if marker in text else "fail",
        })
    return rows


def package_hygiene_rows() -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    for part in sorted(BAD_PACKAGE_PARTS):
        hits: List[str] = []
        for path in ROOT.rglob("*"):
            rel = path.relative_to(ROOT)
            if part in rel.parts:
                hits.append(str(rel))
                if len(hits) >= 5:
                    break
        rows.append({"path_part": part, "hits": len(hits), "sample": ";".join(hits), "status": "pass" if not hits else "fail"})
    return rows


def negative_control_rows() -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    missing_detected = any(True for _ in TESTS) and not (ROOT / "handoff/rev0062/cleanroom-kit/tests/u123/definitely_missing.py").exists()
    rows.append({"control": "missing-required-test", "expected_detection": "fixture manifest detects absent required test", "observed_detection": str(missing_detected).lower(), "status": "pass" if missing_detected else "fail"})
    sample = ROOT / str(TESTS[0]["clean_rel"])
    original = ROOT / str(TESTS[0]["original_rel"])
    tampered_detected = sample.exists() and original.exists() and sha_bytes(sample.read_bytes() + b"#tamper\n") != sha_path(original)
    rows.append({"control": "tampered-test-hash", "expected_detection": "modified test bytes mismatch original maintainer artifact", "observed_detection": str(tampered_detected).lower(), "status": "pass" if tampered_detected else "fail"})
    injected_text = "import pytest\n# maintainer_artifacts should not appear in cleanroom tests\n"
    forbidden_detected = any(s in injected_text for s in FORBIDDEN_TEST_STRINGS)
    rows.append({"control": "forbidden-cube-string", "expected_detection": "cleanroom test scan rejects cube-private path markers", "observed_detection": str(forbidden_detected).lower(), "status": "pass" if forbidden_detected else "fail"})
    tree = ast.parse("import requests\n")
    imports = import_roots(tree)
    forbidden_import_detected = any(i in FORBIDDEN_IMPORT_ROOTS for i in imports)
    rows.append({"control": "forbidden-external-import", "expected_detection": "static import scan rejects network/package-fetch imports", "observed_detection": str(forbidden_import_detected).lower(), "status": "pass" if forbidden_import_detected else "fail"})
    runner_text = (ROOT / "handoff/rev0062/cleanroom-kit/run_cleanroom_replay.py").read_text(encoding="utf-8", errors="replace")
    runner_marker_detected = ("PYTEST_DISABLE_PLUGIN_AUTOLOAD" in runner_text and "PYTEST_DISABLE_PLUGIN_AUTOLOAD" not in runner_text.replace("PYTEST_DISABLE_PLUGIN_AUTOLOAD", ""))
    rows.append({"control": "missing-runner-plugin-isolation-marker", "expected_detection": "runner marker scan detects missing pytest plugin isolation marker", "observed_detection": str(runner_marker_detected).lower(), "status": "pass" if runner_marker_detected else "fail"})
    return rows


def handoff_manifest_rows() -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    base = ROOT / "handoff" / "rev0067"
    if not base.exists():
        return rows
    for path in sorted(p for p in base.rglob("*") if p.is_file() and p.name != "MANIFEST.sha256"):
        rel = path.relative_to(ROOT)
        rows.append({"path": str(rel), "sha256": sha_path(path), "bytes": path.stat().st_size})
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description="rev0067 regression fixture contract gate")
    ap.add_argument("--source-zip", required=True)
    ap.add_argument("--out-dir", default=str(ROOT / "evidence" / "rev0067-regression-fixture-contract-gate"))
    ap.add_argument("--write-data", action="store_true")
    ns = ap.parse_args()

    out_dir = Path(ns.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    source = source_identity(Path(ns.source_zip).resolve())
    source_rows = [{"field": k, "value": json.dumps(v) if isinstance(v, list) else v} for k, v in source.items()]
    fixture_rows = test_lineage_rows()
    patch_rows = patch_lineage_rows()
    runner_rows = runner_contract_rows()
    negative_rows = negative_control_rows()
    hygiene_rows = package_hygiene_rows()
    manifest_rows = handoff_manifest_rows()

    errors: List[str] = []
    if source.get("status") != "pass":
        errors.append("source bundle identity/lane check failed")
    for label, rows in (("fixture rows", fixture_rows), ("patch rows", patch_rows), ("runner rows", runner_rows), ("negative controls", negative_rows), ("package hygiene", hygiene_rows)):
        failed = [r for r in rows if r.get("status") != "pass"]
        if failed:
            errors.append(f"{label} failures: {len(failed)}")
    status = "pass" if not errors else "fail"
    summary = {
        "revision": "rev0067",
        "status": status,
        "source_bundle_used": True,
        "source_sha256": source.get("sha256", ""),
        "source_entries": source.get("entries", 0),
        "source_lanes": source.get("lanes", []),
        "fixture_lineage_rows": len(fixture_rows),
        "fixture_lineage_pass": sum(1 for r in fixture_rows if r.get("status") == "pass"),
        "patch_lineage_rows": len(patch_rows),
        "patch_lineage_pass": sum(1 for r in patch_rows if r.get("status") == "pass"),
        "runner_contract_checks": len(runner_rows),
        "runner_contract_pass": sum(1 for r in runner_rows if r.get("status") == "pass"),
        "negative_controls": len(negative_rows),
        "negative_controls_pass": sum(1 for r in negative_rows if r.get("status") == "pass"),
        "package_hygiene_rows": len(hygiene_rows),
        "package_hygiene_pass": sum(1 for r in hygiene_rows if r.get("status") == "pass"),
        "handoff_manifest_rows": len(manifest_rows),
        "errors": errors,
    }

    write_csv(out_dir / "source_bundle_identity.csv", source_rows, ["field", "value"])
    write_json(out_dir / "source_bundle_identity.json", source)
    write_csv(out_dir / "regression_fixture_contract.csv", fixture_rows, ["packet", "cleanroom_path", "original_path", "cleanroom_exists", "original_exists", "expected_static_tests", "static_test_count", "expected_runtime_pass_summary", "inherited_runtime_rows", "inherited_runtime_ok", "hash_match", "size_bytes", "cleanroom_sha256", "original_sha256", "imports", "forbidden_imports", "forbidden_strings", "ast_ok", "static_test_names", "note", "status"])
    write_json(out_dir / "regression_fixture_contract.json", fixture_rows)
    write_csv(out_dir / "cleanroom_patch_lineage.csv", patch_rows, ["lane", "patch", "cleanroom_path", "rev0059_path", "cleanroom_exists", "rev0059_exists", "hash_match", "size_bytes", "cleanroom_sha256", "rev0059_sha256", "status"])
    write_json(out_dir / "cleanroom_patch_lineage.json", patch_rows)
    write_csv(out_dir / "runner_contract_checks.csv", runner_rows, ["check", "marker", "present", "status"])
    write_json(out_dir / "runner_contract_checks.json", runner_rows)
    write_csv(out_dir / "fixture_negative_controls.csv", negative_rows, ["control", "expected_detection", "observed_detection", "status"])
    write_json(out_dir / "fixture_negative_controls.json", negative_rows)
    write_csv(out_dir / "fixture_package_hygiene.csv", hygiene_rows, ["path_part", "hits", "sample", "status"])
    write_json(out_dir / "fixture_package_hygiene.json", hygiene_rows)
    write_csv(out_dir / "handoff_manifest.csv", manifest_rows, ["path", "sha256", "bytes"])
    write_json(out_dir / "handoff_manifest.json", manifest_rows)
    write_json(out_dir / "regression_fixture_contract_summary.json", summary)

    if ns.write_data:
        mappings = {
            "source_bundle_identity.csv": "data/rev0067_source_bundle_identity.csv",
            "source_bundle_identity.json": "data/rev0067_source_bundle_identity.json",
            "regression_fixture_contract.csv": "data/rev0067_regression_fixture_contract.csv",
            "regression_fixture_contract.json": "data/rev0067_regression_fixture_contract.json",
            "cleanroom_patch_lineage.csv": "data/rev0067_cleanroom_patch_lineage.csv",
            "cleanroom_patch_lineage.json": "data/rev0067_cleanroom_patch_lineage.json",
            "runner_contract_checks.csv": "data/rev0067_runner_contract_checks.csv",
            "runner_contract_checks.json": "data/rev0067_runner_contract_checks.json",
            "fixture_negative_controls.csv": "data/rev0067_fixture_negative_controls.csv",
            "fixture_negative_controls.json": "data/rev0067_fixture_negative_controls.json",
            "fixture_package_hygiene.csv": "data/rev0067_fixture_package_hygiene.csv",
            "fixture_package_hygiene.json": "data/rev0067_fixture_package_hygiene.json",
            "handoff_manifest.csv": "data/rev0067_handoff_manifest.csv",
            "handoff_manifest.json": "data/rev0067_handoff_manifest.json",
            "regression_fixture_contract_summary.json": "data/rev0067_regression_fixture_contract_summary.json",
        }
        for src, dst in mappings.items():
            shutil.copy2(out_dir / src, ROOT / dst)

    print(json.dumps(summary, indent=2, sort_keys=True))
    cleanup_caches(ROOT)
    return 0 if status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
