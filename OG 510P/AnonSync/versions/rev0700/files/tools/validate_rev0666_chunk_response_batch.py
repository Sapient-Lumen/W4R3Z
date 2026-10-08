#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_VALIDATOR = "rev0666 chunk response batch package validator passed"
EXPECTED_CTEST = "100% tests passed, 0 tests failed out of 27"
EXPECTED_SELFTEST = "anonsync_core sync domain model selftest passed=158 failed=0"
ACTIVE_BINARY = "bin/rev0666/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
OLD_ACTIVE_BINARY = "bin/rev0665/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
CAPABILITY_MANIFEST = "gateway/rev0648-cpp-ledger-backend-capabilities.json"
AUDIT = ROOT / "audit/rev0666-chunk-response-batch-audit.json"
MANIFEST = ROOT / "schema/rev0666/slim-cube-manifest.json"

REQUIRED_CURRENT_FILES = [
    "README.md",
    "cpp/anonsync_core/README.md",
    "cpp/anonsync_core/include/anonsync_core.hpp",
    "cpp/anonsync_core/src/sync_domain.cpp",
    ACTIVE_BINARY,
    "bin/HISTORY.md",
    "docs/0001-cpp-core-gameplan.md",
    "docs/0003-next-risk-register.md",
    "docs/0056-rev0666-chunk-response-batch.md",
    "audit/rev0666-chunk-response-batch-audit.json",
    "audit/rev0666-chunk-response-batch-source.patch",
    "audit/logs/rev0666-release-o0-configure.log",
    "audit/logs/rev0666-release-o0-build.log",
    "audit/logs/rev0666-release-o0-ctest.log",
    "audit/logs/rev0666-chunk-response-batch-selftest.log",
    "audit/logs/rev0666-narrow-asan-ubsan-sync-domain-build.log",
    "audit/logs/rev0666-narrow-asan-ubsan-sync-domain-selftest.log",
    "audit/logs/rev0666-binary-sha256.txt",
    "audit/logs/rev0666-binary-ldd.txt",
    "audit/logs/rev0666-chunk-response-batch-package-validator.log",
    "tools/validate_rev0666_chunk_response_batch.py",
]

REQUIRED_PHRASES = {
    "README.md": [
        "C++ peer-to-peer file synchronization system",
        "Rev0666",
        "batch response-envelope acceptance",
        "SyncChunkResponseBatchEnvelope",
        "accept_sync_chunk_response_batch_envelope",
        "sync-chunk-response-batch:v1:",
        "not yet",
    ],
    "cpp/anonsync_core/README.md": [
        "anonsync_core rev0666",
        "SyncChunkResponseBatchEnvelope",
        "build_sync_chunk_response_batch_envelope",
        "accept_sync_chunk_response_batch_envelope",
        "batch response-envelope-bound chunk acceptance",
    ],
    "cpp/anonsync_core/include/anonsync_core.hpp": [
        "struct SyncChunkResponseBatchEnvelope",
        "std::string batch_idempotency_key;",
        "struct SyncChunkResponseBatchAcceptanceResult",
        "bool batch_envelope_checked = false;",
        "build_sync_chunk_response_batch_envelope",
        "accept_sync_chunk_response_batch_envelope",
    ],
    "cpp/anonsync_core/src/sync_domain.cpp": [
        "chunk_response_batch_envelope_idempotency_key",
        "SyncValidationResult build_sync_chunk_response_batch_envelope",
        "SyncValidationResult accept_sync_chunk_response_batch_envelope",
        "chunk response batch envelope response chunks must be an ordered unique subset of the request batch",
        "chunk response batch acceptance rejects forged batch ids before staging peer bytes",
        "chunk response batch acceptance preflights the batch envelope and writes all selected peer chunks through receipt-backed acceptance",
    ],
    "docs/0056-rev0666-chunk-response-batch.md": [
        "chunk response batch",
        "`SyncChunkResponseBatchEnvelope`",
        "`build_sync_chunk_response_batch_envelope`",
        "`accept_sync_chunk_response_batch_envelope`",
        "batch-level replay/cross-response confusion",
        "still does not run a real or fake peer session",
    ],
    "docs/0001-cpp-core-gameplan.md": [
        "batch response-envelope-bound peer chunk acceptance",
        "accept_sync_chunk_response_batch_envelope",
    ],
    "docs/0003-next-risk-register.md": [
        "Next risk register after rev0666",
        "SyncChunkResponseBatchEnvelope",
        "accept_sync_chunk_response_batch_envelope",
    ],
    "bin/HISTORY.md": [
        "rev0666",
        "chunk response batch seam",
        "rev0665: historical source/audit only",
    ],
    "audit/rev0666-chunk-response-batch-audit.json": [
        "chunk-response-batch",
        "fixed_by_SyncChunkResponseBatchEnvelope",
        "fixed_by_sync_chunk_response_batch_v1_idempotency_key",
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
        raise AssertionError("missing required rev0666 files: " + ", ".join(missing))
    if (ROOT / OLD_ACTIVE_BINARY).exists():
        raise AssertionError("rev0666 package must not carry the rev0665 active binary")


def assert_phrases() -> None:
    for rel, phrases in REQUIRED_PHRASES.items():
        text = (ROOT / rel).read_text(errors="replace")
        for phrase in phrases:
            if phrase not in text:
                raise AssertionError(f"required phrase missing from {rel}: {phrase}")


def assert_logs() -> None:
    ctest = (ROOT / "audit/logs/rev0666-release-o0-ctest.log").read_text(errors="replace")
    if EXPECTED_CTEST not in ctest:
        raise AssertionError("release ctest summary missing")
    selftest = (ROOT / "audit/logs/rev0666-chunk-response-batch-selftest.log").read_text(errors="replace")
    if EXPECTED_SELFTEST not in selftest:
        raise AssertionError("sync-domain selftest summary missing")
    asan = (ROOT / "audit/logs/rev0666-narrow-asan-ubsan-sync-domain-selftest.log").read_text(errors="replace")
    if EXPECTED_SELFTEST not in asan:
        raise AssertionError("narrow asan/ubsan selftest summary missing")
    validator_log = ROOT / "audit/logs/rev0666-chunk-response-batch-package-validator.log"
    if validator_log.exists() and EXPECTED_VALIDATOR not in validator_log.read_text(errors="replace"):
        raise AssertionError("package validator log exists but is missing expected pass line")


def assert_audit() -> None:
    audit = json.loads(AUDIT.read_text())
    if audit.get("revision_id") != "rev0666" or audit.get("parent_revision") != "rev0665":
        raise AssertionError("audit revision lineage mismatch")
    if audit.get("product_mission") != "cxx-p2p-file-sync":
        raise AssertionError("audit product mission mismatch")
    if audit.get("active_binary") != ACTIVE_BINARY:
        raise AssertionError("audit active binary mismatch")
    if audit.get("active_binary_sha256") != sha_file(ROOT / ACTIVE_BINARY):
        raise AssertionError("audit active binary sha mismatch")
    if not audit.get("cxx_behavior_changed"):
        raise AssertionError("rev0666 must claim C++ behavior changed")
    required_api = {
        "SyncChunkResponseBatchEnvelope added for network-facing multi-chunk response evidence",
        "SyncChunkResponseBatchAcceptanceResult added for batch-level verification and per-chunk acceptance evidence",
        "build_sync_chunk_response_batch_envelope added to construct deterministic sync-chunk-response-batch:v1 evidence for ordered selected response chunks",
        "accept_sync_chunk_response_batch_envelope added to rebuild request and batch evidence before staging multiple peer chunks",
        "chunk response batch acceptance rejects duplicate response chunks, out-of-order response chunks, forged batch ids, mismatched counts/totals, and byte hash mismatches before disk writes",
    }
    missing_api = required_api - set(audit.get("cxx_api_changed", []))
    if missing_api:
        raise AssertionError("audit missing API changes: " + ", ".join(sorted(missing_api)))
    findings = audit.get("audit_findings", {})
    if findings.get("multi_chunk_peer_responses_were_not_explicitly_modeled") != "fixed_by_SyncChunkResponseBatchEnvelope":
        raise AssertionError("audit must record explicit batch response fix")
    if findings.get("future_session_layer_would_have_to_invent_batch_ids") != "fixed_by_sync_chunk_response_batch_v1_idempotency_key":
        raise AssertionError("audit must record batch commitment key fix")
    if findings.get("duplicate_or_out_of_order_response_chunks_were_a_session_layer_hazard") != "fixed_by_ordered_unique_response_subset_validation":
        raise AssertionError("audit must record ordered unique subset validation")
    validation = audit.get("validation", {})
    if validation.get("release_ctest_summary") != EXPECTED_CTEST:
        raise AssertionError("audit ctest summary mismatch")
    if validation.get("sync_domain_selftest_summary") != EXPECTED_SELFTEST:
        raise AssertionError("audit sync-domain selftest summary mismatch")
    if validation.get("narrow_asan_ubsan_selftest_summary") != EXPECTED_SELFTEST:
        raise AssertionError("audit narrow asan/ubsan selftest summary mismatch")


def assert_binary_sha() -> None:
    line = (ROOT / "audit/logs/rev0666-binary-sha256.txt").read_text().strip().split()
    if len(line) < 2:
        raise AssertionError("binary sha256 log malformed")
    expected_sha, rel = line[0], line[1]
    if rel != ACTIVE_BINARY:
        raise AssertionError("binary sha256 log points at wrong active binary")
    if sha_file(ROOT / ACTIVE_BINARY) != expected_sha:
        raise AssertionError("active binary sha256 mismatch")


def assert_manifest() -> None:
    manifest = json.loads(MANIFEST.read_text())
    if manifest.get("revision_id") != "rev0666" or manifest.get("parent_revision") != "rev0665":
        raise AssertionError("rev0666 manifest lineage mismatch")
    if manifest.get("manifest_kind") != "code-bearing-chunk-response-batch":
        raise AssertionError("rev0666 manifest kind mismatch")
    if manifest.get("product_mission") != "cxx-p2p-file-sync":
        raise AssertionError("rev0666 product mission tag mismatch")
    if manifest.get("codename") != "chunk-response-batch":
        raise AssertionError("rev0666 codename mismatch")
    if manifest.get("active_binary") != ACTIVE_BINARY:
        raise AssertionError("active binary should be rev0666")
    if manifest.get("capability_manifest") != CAPABILITY_MANIFEST:
        raise AssertionError("capability manifest should remain rev0648-bound until sync-ledger capabilities change")
    rows = manifest.get("files", [])
    if manifest.get("file_count") != len(rows):
        raise AssertionError("manifest file_count mismatch")
    files = {item.get("path"): item for item in rows}
    missing = sorted(path for path in REQUIRED_CURRENT_FILES if path not in files)
    if missing:
        raise AssertionError("rev0666 manifest missing paths: " + ", ".join(missing))
    if OLD_ACTIVE_BINARY in files:
        raise AssertionError("manifest must not include old rev0665 active binary")
    if "schema/rev0666/slim-cube-manifest.json" not in set(manifest.get("excluded_mutable_evidence", [])):
        raise AssertionError("manifest must exclude itself")
    for path, item in files.items():
        full = ROOT / path
        if not full.exists():
            raise AssertionError("manifest path missing from package: " + path)
        if item.get("sha256") != sha_file(full):
            raise AssertionError("manifest sha mismatch for " + path)
        if item.get("size_bytes") != full.stat().st_size:
            raise AssertionError("manifest size mismatch for " + path)


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
