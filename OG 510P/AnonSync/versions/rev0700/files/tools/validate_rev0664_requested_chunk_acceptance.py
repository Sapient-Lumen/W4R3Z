#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_VALIDATOR = "rev0664 requested chunk acceptance package validator passed"
EXPECTED_CTEST = "100% tests passed, 0 tests failed out of 27"
EXPECTED_SELFTEST = "anonsync_core sync domain model selftest passed=145 failed=0"
ACTIVE_BINARY = "bin/rev0664/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
OLD_ACTIVE_BINARY = "bin/rev0663/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
CAPABILITY_MANIFEST = "gateway/rev0648-cpp-ledger-backend-capabilities.json"
AUDIT = ROOT / "audit/rev0664-requested-chunk-acceptance-audit.json"
MANIFEST = ROOT / "schema/rev0664/slim-cube-manifest.json"

REQUIRED_CURRENT_FILES = [
    "README.md",
    "cpp/anonsync_core/README.md",
    "cpp/anonsync_core/include/anonsync_core.hpp",
    "cpp/anonsync_core/src/sync_domain.cpp",
    ACTIVE_BINARY,
    "bin/HISTORY.md",
    "docs/0001-cpp-core-gameplan.md",
    "docs/0003-next-risk-register.md",
    "docs/0054-rev0664-requested-chunk-acceptance.md",
    "audit/rev0664-requested-chunk-acceptance-audit.json",
    "audit/rev0664-requested-chunk-acceptance-source.patch",
    "audit/logs/rev0664-release-o0-configure.log",
    "audit/logs/rev0664-release-o0-build.log",
    "audit/logs/rev0664-release-o0-ctest.log",
    "audit/logs/rev0664-requested-chunk-acceptance-selftest.log",
    "audit/logs/rev0664-narrow-asan-ubsan-sync-domain-build.log",
    "audit/logs/rev0664-narrow-asan-ubsan-sync-domain-selftest.log",
    "audit/logs/rev0664-binary-sha256.txt",
    "audit/logs/rev0664-binary-ldd.txt",
    "audit/logs/rev0664-requested-chunk-acceptance-package-validator.log",
    "tools/validate_rev0664_requested_chunk_acceptance.py",
]

REQUIRED_PHRASES = {
    "README.md": [
        "C++ peer-to-peer file synchronization system",
        "Rev0664",
        "requested peer-chunk acceptance",
        "accept_sync_requested_chunk",
        "bind peer chunk responses back to verified request-plan evidence",
        "not yet",
    ],
    "cpp/anonsync_core/README.md": [
        "anonsync_core rev0664",
        "SyncRequestedChunkAcceptanceResult",
        "accept_sync_requested_chunk",
        "request-bound peer chunk response acceptance",
        "sync-chunk-receipt:v1:",
    ],
    "cpp/anonsync_core/include/anonsync_core.hpp": [
        "struct SyncRequestedChunkAcceptanceResult",
        "std::string request_idempotency_key;",
        "bool request_evidence_checked = false;",
        "accept_sync_requested_chunk",
    ],
    "cpp/anonsync_core/src/sync_domain.cpp": [
        "bool chunk_ranges_equal",
        "bool chunk_range_is_selected",
        "SyncValidationResult accept_sync_requested_chunk",
        "requested chunk acceptance request plan does not match verified inspection/options evidence",
        "requested chunk acceptance rejects peer bytes for chunks outside the selected request batch",
        "requested chunk acceptance binds peer chunk bytes to verified request-plan evidence before writing",
    ],
    "docs/0054-rev0664-requested-chunk-acceptance.md": [
        "requested chunk acceptance",
        "peer response acceptance",
        "`accept_sync_requested_chunk`",
        "caller-mutated request metadata",
        "does not run a peer session",
    ],
    "docs/0001-cpp-core-gameplan.md": [
        "request-bound peer chunk response acceptance",
        "accept_sync_requested_chunk",
    ],
    "docs/0003-next-risk-register.md": [
        "Next risk register after rev0664",
        "request-bound peer chunk response acceptance",
        "accept_sync_requested_chunk",
    ],
    "bin/HISTORY.md": [
        "rev0664",
        "requested chunk acceptance seam",
        "rev0663: historical source/audit only",
    ],
    "audit/rev0664-requested-chunk-acceptance-audit.json": [
        "requested-chunk-acceptance",
        "fixed_by_accept_sync_requested_chunk",
        "fixed_by_rebuilding_expected_plan_from_inspection_and_options",
    ],
}


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def assert_exists() -> None:
    missing = [path for path in REQUIRED_CURRENT_FILES if not (ROOT / path).exists()]
    if missing:
        raise AssertionError("missing required rev0664 files: " + ", ".join(missing))
    if (ROOT / OLD_ACTIVE_BINARY).exists():
        raise AssertionError("rev0664 package must not carry the rev0663 active binary")


def assert_phrases() -> None:
    for rel, phrases in REQUIRED_PHRASES.items():
        text = (ROOT / rel).read_text(errors="replace")
        for phrase in phrases:
            if phrase not in text:
                raise AssertionError(f"required phrase missing from {rel}: {phrase}")


def assert_logs() -> None:
    ctest = (ROOT / "audit/logs/rev0664-release-o0-ctest.log").read_text(errors="replace")
    if EXPECTED_CTEST not in ctest:
        raise AssertionError("release ctest summary missing")
    selftest = (ROOT / "audit/logs/rev0664-requested-chunk-acceptance-selftest.log").read_text(errors="replace")
    if EXPECTED_SELFTEST not in selftest:
        raise AssertionError("sync-domain selftest summary missing")
    asan = (ROOT / "audit/logs/rev0664-narrow-asan-ubsan-sync-domain-selftest.log").read_text(errors="replace")
    if EXPECTED_SELFTEST not in asan:
        raise AssertionError("narrow asan/ubsan selftest summary missing")
    validator_log = (ROOT / "audit/logs/rev0664-requested-chunk-acceptance-package-validator.log").read_text(errors="replace")
    if EXPECTED_VALIDATOR not in validator_log:
        raise AssertionError("package validator log missing expected pass line")


def assert_audit() -> None:
    audit = json.loads(AUDIT.read_text())
    if audit.get("revision_id") != "rev0664" or audit.get("parent_revision") != "rev0663":
        raise AssertionError("audit revision lineage mismatch")
    if audit.get("product_mission") != "cxx-p2p-file-sync":
        raise AssertionError("audit product mission mismatch")
    if audit.get("active_binary") != ACTIVE_BINARY:
        raise AssertionError("audit active binary mismatch")
    if audit.get("active_binary_sha256") != sha_file(ROOT / ACTIVE_BINARY):
        raise AssertionError("audit active binary sha mismatch")
    if not audit.get("cxx_behavior_changed"):
        raise AssertionError("rev0664 must claim C++ behavior changed")
    required_api = {
        "SyncRequestedChunkAcceptanceResult added for request-bound peer chunk response acceptance evidence",
        "accept_sync_requested_chunk added to rebuild and compare chunk request plan evidence before staging peer bytes",
        "requested chunk acceptance rejects caller-mutated request plans, already-complete staged transfers, empty request batches, and unrequested response chunks",
        "requested chunk acceptance delegates accepted bytes to write_sync_staged_chunk so receipt reuse and completion semantics stay centralized",
    }
    missing_api = required_api - set(audit.get("cxx_api_changed", []))
    if missing_api:
        raise AssertionError("audit missing API changes: " + ", ".join(sorted(missing_api)))
    findings = audit.get("audit_findings", {})
    if findings.get("peer_response_path_was_not_bound_to_request_plan_evidence") != "fixed_by_accept_sync_requested_chunk":
        raise AssertionError("audit must record requested chunk acceptance fix")
    if findings.get("lower_level_chunk_writer_could_accept_any_valid_manifest_chunk") != "kept_as_primitive_but_wrapped_by_request_bound_acceptance_api":
        raise AssertionError("audit must record chunk writer wrapper discipline")
    if findings.get("caller_mutated_request_plan_could_precede_peer_response_staging") != "fixed_by_rebuilding_expected_plan_from_inspection_and_options":
        raise AssertionError("audit must record rebuilt request evidence")
    validation = audit.get("validation", {})
    if validation.get("release_ctest_summary") != EXPECTED_CTEST:
        raise AssertionError("audit ctest summary mismatch")
    if validation.get("sync_domain_selftest_summary") != EXPECTED_SELFTEST:
        raise AssertionError("audit sync-domain selftest summary mismatch")
    if validation.get("narrow_asan_ubsan_selftest_summary") != EXPECTED_SELFTEST:
        raise AssertionError("audit narrow asan/ubsan selftest summary mismatch")


def assert_binary_sha() -> None:
    line = (ROOT / "audit/logs/rev0664-binary-sha256.txt").read_text().strip().split()
    if len(line) < 2:
        raise AssertionError("binary sha256 log malformed")
    expected_sha, rel = line[0], line[1]
    if rel != ACTIVE_BINARY:
        raise AssertionError("binary sha256 log points at wrong active binary")
    if sha_file(ROOT / ACTIVE_BINARY) != expected_sha:
        raise AssertionError("active binary sha256 mismatch")


def assert_manifest() -> None:
    manifest = json.loads(MANIFEST.read_text())
    if manifest.get("revision_id") != "rev0664" or manifest.get("parent_revision") != "rev0663":
        raise AssertionError("rev0664 manifest lineage mismatch")
    if manifest.get("manifest_kind") != "code-bearing-requested-chunk-acceptance":
        raise AssertionError("rev0664 manifest kind mismatch")
    if manifest.get("product_mission") != "cxx-p2p-file-sync":
        raise AssertionError("rev0664 product mission tag mismatch")
    if manifest.get("codename") != "requested-chunk-acceptance":
        raise AssertionError("rev0664 codename mismatch")
    if manifest.get("active_binary") != ACTIVE_BINARY:
        raise AssertionError("active binary should be rev0664")
    if manifest.get("capability_manifest") != CAPABILITY_MANIFEST:
        raise AssertionError("capability manifest should remain rev0648 until ledger schema changes")
    rows = manifest.get("files", [])
    if manifest.get("file_count") != len(rows):
        raise AssertionError("manifest file_count mismatch")
    by_path = {row["path"]: row for row in rows}
    for path in REQUIRED_CURRENT_FILES:
        if path not in by_path:
            raise AssertionError(f"rev0664 file missing from manifest: {path}")
    if OLD_ACTIVE_BINARY in by_path:
        raise AssertionError("manifest must not include old rev0663 active binary")
    if "schema/rev0664/slim-cube-manifest.json" not in set(manifest.get("excluded_mutable_evidence", [])):
        raise AssertionError("manifest must exclude itself")
    for row in rows:
        rel = row["path"]
        p = ROOT / rel
        if not p.exists():
            raise AssertionError(f"manifest file missing on disk: {rel}")
        data = p.read_bytes()
        if len(data) != row["size_bytes"]:
            raise AssertionError(f"manifest size mismatch: {rel}")
        if hashlib.sha256(data).hexdigest() != row["sha256"]:
            raise AssertionError(f"manifest sha mismatch: {rel}")


def main() -> None:
    assert_exists()
    assert_phrases()
    assert_logs()
    assert_audit()
    assert_binary_sha()
    assert_manifest()
    print(EXPECTED_VALIDATOR)


if __name__ == "__main__":
    main()
