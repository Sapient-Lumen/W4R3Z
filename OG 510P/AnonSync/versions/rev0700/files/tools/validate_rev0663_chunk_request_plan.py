#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_VALIDATOR = "rev0663 chunk request plan package validator passed"
EXPECTED_CTEST = "100% tests passed, 0 tests failed out of 27"
EXPECTED_SELFTEST = "anonsync_core sync domain model selftest passed=141 failed=0"
ACTIVE_BINARY = "bin/rev0663/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
OLD_ACTIVE_BINARY = "bin/rev0662/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
CAPABILITY_MANIFEST = "gateway/rev0648-cpp-ledger-backend-capabilities.json"
AUDIT = ROOT / "audit/rev0663-chunk-request-plan-audit.json"
MANIFEST = ROOT / "schema/rev0663/slim-cube-manifest.json"

REQUIRED_CURRENT_FILES = [
    "README.md",
    "cpp/anonsync_core/README.md",
    "cpp/anonsync_core/include/anonsync_core.hpp",
    "cpp/anonsync_core/src/sync_domain.cpp",
    ACTIVE_BINARY,
    "bin/HISTORY.md",
    "docs/0001-cpp-core-gameplan.md",
    "docs/0003-next-risk-register.md",
    "docs/0053-rev0663-chunk-request-plan.md",
    "audit/rev0663-chunk-request-plan-audit.json",
    "audit/rev0663-chunk-request-plan-source.patch",
    "audit/logs/rev0663-release-o0-configure.log",
    "audit/logs/rev0663-release-o0-build.log",
    "audit/logs/rev0663-release-o0-ctest.log",
    "audit/logs/rev0663-chunk-request-plan-selftest.log",
    "audit/logs/rev0663-narrow-asan-ubsan-sync-domain-build.log",
    "audit/logs/rev0663-narrow-asan-ubsan-sync-domain-selftest.log",
    "audit/logs/rev0663-binary-sha256.txt",
    "audit/logs/rev0663-binary-ldd.txt",
    "audit/logs/rev0663-chunk-request-plan-package-validator.log",
    "tools/validate_rev0663_chunk_request_plan.py",
]

REQUIRED_PHRASES = {
    "README.md": [
        "C++ peer-to-peer file synchronization system",
        "Rev0663",
        "chunk request planning",
        "build_sync_chunk_request_plan",
        "sync-chunk-request:v1:",
        "not yet",
    ],
    "cpp/anonsync_core/README.md": [
        "anonsync_core rev0663",
        "SyncChunkRequestPlanOptions",
        "SyncChunkRequestPlanResult",
        "build_sync_chunk_request_plan",
        "sync-chunk-request:v1:",
    ],
    "cpp/anonsync_core/include/anonsync_core.hpp": [
        "struct SyncChunkRequestPlanOptions",
        "struct SyncChunkRequestPlanResult",
        "std::vector<SyncChunkRange> chunks_to_request;",
        "build_sync_chunk_request_plan",
    ],
    "cpp/anonsync_core/src/sync_domain.cpp": [
        "chunk_request_plan_idempotency_key",
        "manifest_missing_chunks_in_manifest_order",
        "SyncValidationResult build_sync_chunk_request_plan",
        "chunk request plan turns verified partial inspection into a bounded missing-chunk request batch",
        "chunk request plan rejects forged missing chunks not present in manifest order",
    ],
    "docs/0053-rev0663-chunk-request-plan.md": [
        "deterministic chunk request planning",
        "which missing manifest chunks should be requested",
        "`sync-chunk-request:v1:`",
        "does not send chunk requests to a peer",
    ],
    "docs/0001-cpp-core-gameplan.md": [
        "chunk request planning",
        "build_sync_chunk_request_plan",
    ],
    "docs/0003-next-risk-register.md": [
        "Next risk register after rev0663",
        "deterministic chunk request planning",
        "build_sync_chunk_request_plan",
    ],
    "bin/HISTORY.md": [
        "rev0663",
        "chunk request planning seam",
        "rev0662: historical source/audit only",
    ],
    "audit/rev0663-chunk-request-plan-audit.json": [
        "chunk-request-plan",
        "fixed_by_build_sync_chunk_request_plan",
        "fixed_by_inspection_evidence_revalidation",
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
        raise AssertionError("missing required rev0663 files: " + ", ".join(missing))
    if (ROOT / OLD_ACTIVE_BINARY).exists():
        raise AssertionError("rev0663 package must not carry the rev0662 active binary")


def assert_phrases() -> None:
    for rel, phrases in REQUIRED_PHRASES.items():
        text = (ROOT / rel).read_text(errors="replace")
        for phrase in phrases:
            if phrase not in text:
                raise AssertionError(f"required phrase missing from {rel}: {phrase}")


def assert_logs() -> None:
    ctest = (ROOT / "audit/logs/rev0663-release-o0-ctest.log").read_text(errors="replace")
    if EXPECTED_CTEST not in ctest:
        raise AssertionError("release ctest summary missing")
    selftest = (ROOT / "audit/logs/rev0663-chunk-request-plan-selftest.log").read_text(errors="replace")
    if EXPECTED_SELFTEST not in selftest:
        raise AssertionError("sync-domain selftest summary missing")
    asan = (ROOT / "audit/logs/rev0663-narrow-asan-ubsan-sync-domain-selftest.log").read_text(errors="replace")
    if EXPECTED_SELFTEST not in asan:
        raise AssertionError("narrow asan/ubsan selftest summary missing")
    validator_log = (ROOT / "audit/logs/rev0663-chunk-request-plan-package-validator.log").read_text(errors="replace")
    if EXPECTED_VALIDATOR not in validator_log:
        raise AssertionError("package validator log missing expected pass line")


def assert_audit() -> None:
    audit = json.loads(AUDIT.read_text())
    if audit.get("revision_id") != "rev0663" or audit.get("parent_revision") != "rev0662":
        raise AssertionError("audit revision lineage mismatch")
    if audit.get("product_mission") != "cxx-p2p-file-sync":
        raise AssertionError("audit product mission mismatch")
    if audit.get("active_binary") != ACTIVE_BINARY:
        raise AssertionError("audit active binary mismatch")
    if audit.get("active_binary_sha256") != sha_file(ROOT / ACTIVE_BINARY):
        raise AssertionError("audit active binary sha mismatch")
    if not audit.get("cxx_behavior_changed"):
        raise AssertionError("rev0663 must claim C++ behavior changed")
    required_api = {
        "SyncChunkRequestPlanOptions added for max_chunks_per_request and max_bytes_per_request",
        "SyncChunkRequestPlanResult added for deterministic request evidence, selected chunks, selected bytes, and remaining-work state",
        "build_sync_chunk_request_plan added to convert receipt-checked staged-transfer inspection into bounded peer chunk request batches",
        "chunk request planning rejects forged missing chunks, mismatched inspection keys, inconsistent receipt counts, and too-small byte budgets",
    }
    missing_api = required_api - set(audit.get("cxx_api_changed", []))
    if missing_api:
        raise AssertionError("audit missing API changes: " + ", ".join(sorted(missing_api)))
    findings = audit.get("audit_findings", {})
    if findings.get("verified_missing_chunks_had_no_scheduler_request_boundary") != "fixed_by_build_sync_chunk_request_plan":
        raise AssertionError("audit must record chunk request boundary fix")
    if findings.get("caller_side_chunk_batching_could_trust_forged_inspection_state") != "fixed_by_inspection_evidence_revalidation":
        raise AssertionError("audit must record inspection evidence revalidation")
    if findings.get("request_budgeting_needed_fail_closed_semantics") != "fixed_by_budgeted_manifest_ordered_chunk_selection":
        raise AssertionError("audit must record budgeted manifest-order selection")
    validation = audit.get("validation", {})
    if validation.get("release_ctest_summary") != EXPECTED_CTEST:
        raise AssertionError("audit ctest summary mismatch")
    if validation.get("sync_domain_selftest_summary") != EXPECTED_SELFTEST:
        raise AssertionError("audit sync-domain selftest summary mismatch")
    if validation.get("narrow_asan_ubsan_selftest_summary") != EXPECTED_SELFTEST:
        raise AssertionError("audit narrow asan/ubsan selftest summary mismatch")


def assert_binary_sha() -> None:
    line = (ROOT / "audit/logs/rev0663-binary-sha256.txt").read_text().strip().split()
    if len(line) < 2:
        raise AssertionError("binary sha256 log malformed")
    expected_sha, rel = line[0], line[1]
    if rel != ACTIVE_BINARY:
        raise AssertionError("binary sha256 log points at wrong active binary")
    if sha_file(ROOT / ACTIVE_BINARY) != expected_sha:
        raise AssertionError("active binary sha256 mismatch")


def assert_manifest() -> None:
    manifest = json.loads(MANIFEST.read_text())
    if manifest.get("revision_id") != "rev0663" or manifest.get("parent_revision") != "rev0662":
        raise AssertionError("rev0663 manifest lineage mismatch")
    if manifest.get("manifest_kind") != "code-bearing-chunk-request-plan":
        raise AssertionError("rev0663 manifest kind mismatch")
    if manifest.get("product_mission") != "cxx-p2p-file-sync":
        raise AssertionError("rev0663 product mission tag mismatch")
    if manifest.get("codename") != "chunk-request-plan":
        raise AssertionError("rev0663 codename mismatch")
    if manifest.get("active_binary") != ACTIVE_BINARY:
        raise AssertionError("active binary should be rev0663")
    if manifest.get("capability_manifest") != CAPABILITY_MANIFEST:
        raise AssertionError("capability manifest should remain rev0648 until ledger schema changes")
    rows = manifest.get("files", [])
    if manifest.get("file_count") != len(rows):
        raise AssertionError("manifest file_count mismatch")
    by_path = {row["path"]: row for row in rows}
    for path in REQUIRED_CURRENT_FILES:
        if path not in by_path:
            raise AssertionError(f"rev0663 file missing from manifest: {path}")
    if OLD_ACTIVE_BINARY in by_path:
        raise AssertionError("manifest must not include old rev0662 active binary")
    if "schema/rev0663/slim-cube-manifest.json" not in set(manifest.get("excluded_mutable_evidence", [])):
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
