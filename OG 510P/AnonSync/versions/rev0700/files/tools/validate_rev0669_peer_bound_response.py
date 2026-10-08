#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_VALIDATOR = "rev0669 peer-bound response package validator passed"
EXPECTED_CTEST = "100% tests passed, 0 tests failed out of 27"
EXPECTED_SELFTEST = "anonsync_core sync domain model selftest passed=180 failed=0"
ACTIVE_BINARY = "bin/rev0669/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
OLD_ACTIVE_BINARY = "bin/rev0668/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
CAPABILITY_MANIFEST = "gateway/rev0648-cpp-ledger-backend-capabilities.json"
AUDIT = ROOT / "audit/rev0669-peer-bound-response-audit.json"
MANIFEST = ROOT / "schema/rev0669/slim-cube-manifest.json"

REQUIRED_CURRENT_FILES = [
    "README.md",
    "cpp/anonsync_core/README.md",
    "cpp/anonsync_core/include/anonsync_core.hpp",
    "cpp/anonsync_core/src/sync_domain.cpp",
    ACTIVE_BINARY,
    "bin/HISTORY.md",
    "docs/0001-cpp-core-gameplan.md",
    "docs/0003-next-risk-register.md",
    "docs/0059-rev0669-peer-bound-response.md",
    "audit/rev0669-peer-bound-response-audit.json",
    "audit/rev0669-peer-bound-response-source.patch",
    "audit/logs/rev0669-release-o0-configure.log",
    "audit/logs/rev0669-release-o0-build.log",
    "audit/logs/rev0669-release-o0-ctest.log",
    "audit/logs/rev0669-peer-bound-response-selftest.log",
    "audit/logs/rev0669-narrow-asan-ubsan-sync-domain-build.log",
    "audit/logs/rev0669-narrow-asan-ubsan-sync-domain-selftest.log",
    "audit/logs/rev0669-binary-sha256.txt",
    "audit/logs/rev0669-binary-ldd.txt",
    "audit/logs/rev0669-peer-bound-response-package-validator.log",
    "tools/validate_rev0669_peer_bound_response.py",
]

REQUIRED_PHRASES = {
    "README.md": [
        "C++ peer-to-peer file synchronization system",
        "Rev0669",
        "peer-bound batch response acceptance",
        "SyncPeerChunkResponseBatchEnvelope",
        "accept_sync_peer_chunk_response_batch_envelope",
        "sync-peer-chunk-response-batch:v1",
        "not yet",
    ],
    "cpp/anonsync_core/README.md": [
        "anonsync_core rev0669",
        "SyncPeerChunkResponseBatchEnvelope",
        "SyncPeerChunkResponseBatchAcceptanceResult",
        "build_sync_peer_chunk_response_batch_envelope",
        "accept_sync_peer_chunk_response_batch_envelope",
        "peer-bound response acceptance",
    ],
    "cpp/anonsync_core/include/anonsync_core.hpp": [
        "struct SyncPeerChunkResponseBatchEnvelope",
        "struct SyncPeerChunkResponseBatchAcceptanceResult",
        "build_sync_peer_chunk_response_batch_envelope",
        "accept_sync_peer_chunk_response_batch_envelope",
        "std::string schedule_idempotency_key;",
        "std::string peer_request_idempotency_key;",
    ],
    "cpp/anonsync_core/src/sync_domain.cpp": [
        "SyncValidationResult build_sync_peer_chunk_response_batch_envelope",
        "SyncValidationResult accept_sync_peer_chunk_response_batch_envelope",
        "sync-peer-chunk-response-batch:v1:",
        "peer chunk response batch acceptance assignment is not present in the peer schedule",
        "peer-bound response acceptance rejects a batch replayed against another scheduled peer assignment",
        "peer-bound response envelope builder rejects assignments not present in the verified peer schedule",
        "validate_peer_chunk_schedule_for_request",
    ],
    "docs/0059-rev0669-peer-bound-response.md": [
        "peer-bound response acceptance",
        "`SyncPeerChunkResponseBatchEnvelope`",
        "`SyncPeerChunkResponseBatchAcceptanceResult`",
        "`build_sync_peer_chunk_response_batch_envelope`",
        "`accept_sync_peer_chunk_response_batch_envelope`",
        "Cross-peer replay is rejected",
        "still does not run a real peer protocol",
    ],
    "docs/0001-cpp-core-gameplan.md": [
        "Current rev0669 product slice",
        "build_sync_peer_chunk_response_batch_envelope",
        "accept_sync_peer_chunk_response_batch_envelope",
        "peer-bound response acceptance",
    ],
    "docs/0003-next-risk-register.md": [
        "Next risk register after rev0669",
        "SyncPeerChunkResponseBatchEnvelope",
        "accept_sync_peer_chunk_response_batch_envelope",
    ],
    "bin/HISTORY.md": [
        "rev0669",
        "peer-bound response acceptance seam",
        "rev0668: historical source/audit only",
    ],
    "audit/rev0669-peer-bound-response-audit.json": [
        "peer-bound-response",
        "fixed_by_sync_peer_chunk_response_batch_envelope",
        "fixed_by_assignment_subset_and_peer_envelope_check",
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
        raise AssertionError("missing required rev0669 files: " + ", ".join(missing))
    if (ROOT / OLD_ACTIVE_BINARY).exists():
        raise AssertionError("rev0669 package must not carry the rev0668 active binary")


def assert_phrases() -> None:
    for rel, phrases in REQUIRED_PHRASES.items():
        text = (ROOT / rel).read_text(errors="replace")
        for phrase in phrases:
            if phrase not in text:
                raise AssertionError(f"required phrase missing from {rel}: {phrase}")


def assert_logs() -> None:
    ctest = (ROOT / "audit/logs/rev0669-release-o0-ctest.log").read_text(errors="replace")
    if EXPECTED_CTEST not in ctest:
        raise AssertionError("release ctest summary missing")
    selftest = (ROOT / "audit/logs/rev0669-peer-bound-response-selftest.log").read_text(errors="replace")
    if EXPECTED_SELFTEST not in selftest:
        raise AssertionError("sync-domain selftest summary missing")
    asan = (ROOT / "audit/logs/rev0669-narrow-asan-ubsan-sync-domain-selftest.log").read_text(errors="replace")
    if EXPECTED_SELFTEST not in asan:
        raise AssertionError("narrow asan/ubsan selftest summary missing")
    validator_log = ROOT / "audit/logs/rev0669-peer-bound-response-package-validator.log"
    if validator_log.exists() and EXPECTED_VALIDATOR not in validator_log.read_text(errors="replace"):
        raise AssertionError("package validator log exists but is missing expected pass line")


def assert_audit() -> None:
    audit = json.loads(AUDIT.read_text())
    if audit.get("revision_id") != "rev0669" or audit.get("parent_revision") != "rev0668":
        raise AssertionError("audit revision lineage mismatch")
    if audit.get("product_mission") != "cxx-p2p-file-sync":
        raise AssertionError("audit product mission mismatch")
    if audit.get("active_binary") != ACTIVE_BINARY:
        raise AssertionError("audit active binary mismatch")
    if audit.get("active_binary_sha256") != sha_file(ROOT / ACTIVE_BINARY):
        raise AssertionError("audit active binary sha mismatch")
    if not audit.get("cxx_behavior_changed"):
        raise AssertionError("rev0669 must claim C++ behavior changed")
    required_api = {
        "SyncPeerChunkResponseBatchEnvelope added to bind one response batch to a peer schedule and per-peer sync-peer-chunk-request:v1 assignment",
        "SyncPeerChunkResponseBatchAcceptanceResult added to expose request, schedule, assignment, and peer-envelope checks before receipt-backed writes",
        "build_sync_peer_chunk_response_batch_envelope added to derive sync-peer-chunk-response-batch:v1 evidence from request, schedule, assignment, and response chunks",
        "accept_sync_peer_chunk_response_batch_envelope added to rebuild request evidence, validate peer schedule/assignment evidence, reject cross-peer replay, and delegate only verified bytes to batch acceptance",
        "sync-domain selftest extended with peer-bound envelope creation, scheduled assignment acceptance, cross-peer replay rejection, and forged assignment rejection",
    }
    missing_api = required_api - set(audit.get("cxx_api_changed", []))
    if missing_api:
        raise AssertionError("audit missing API changes: " + ", ".join(sorted(missing_api)))
    findings = audit.get("audit_findings", {})
    if findings.get("scheduled_peer_work_was_not_bound_to_response_acceptance") != "fixed_by_sync_peer_chunk_response_batch_envelope":
        raise AssertionError("audit must record peer-bound envelope fix")
    if findings.get("cross_peer_replay_could_reuse_a_valid_global_batch") != "fixed_by_assignment_subset_and_peer_envelope_check":
        raise AssertionError("audit must record cross-peer replay fix")
    if findings.get("forged_assignment_needed_fail_closed_builder") != "fixed_by_assignment_must_appear_in_schedule":
        raise AssertionError("audit must record forged assignment rejection")
    validation = audit.get("validation", {})
    if validation.get("release_ctest_summary") != EXPECTED_CTEST:
        raise AssertionError("audit ctest summary mismatch")
    if validation.get("sync_domain_selftest_summary") != EXPECTED_SELFTEST:
        raise AssertionError("audit sync-domain selftest summary mismatch")
    if validation.get("narrow_asan_ubsan_selftest_summary") != EXPECTED_SELFTEST:
        raise AssertionError("audit narrow asan/ubsan selftest summary mismatch")


def assert_binary_sha() -> None:
    line = (ROOT / "audit/logs/rev0669-binary-sha256.txt").read_text().strip().split()
    if len(line) < 2:
        raise AssertionError("binary sha256 log malformed")
    expected_sha, rel = line[0], line[1]
    if rel != ACTIVE_BINARY:
        raise AssertionError("binary sha256 log points at wrong active binary")
    if sha_file(ROOT / ACTIVE_BINARY) != expected_sha:
        raise AssertionError("active binary sha256 mismatch")


def assert_manifest() -> None:
    manifest = json.loads(MANIFEST.read_text())
    if manifest.get("revision_id") != "rev0669" or manifest.get("parent_revision") != "rev0668":
        raise AssertionError("rev0669 manifest lineage mismatch")
    if manifest.get("manifest_kind") != "code-bearing-peer-bound-response":
        raise AssertionError("rev0669 manifest kind mismatch")
    if manifest.get("product_mission") != "cxx-p2p-file-sync":
        raise AssertionError("rev0669 product mission tag mismatch")
    if manifest.get("codename") != "peer-bound-response":
        raise AssertionError("rev0669 codename mismatch")
    if manifest.get("active_binary") != ACTIVE_BINARY:
        raise AssertionError("active binary should be rev0669")
    if manifest.get("capability_manifest") != CAPABILITY_MANIFEST:
        raise AssertionError("capability manifest should remain rev0648-bound until sync-ledger capabilities change")
    rows = manifest.get("files", [])
    if manifest.get("file_count") != len(rows):
        raise AssertionError("manifest file_count mismatch")
    files = {item.get("path"): item for item in rows}
    missing = sorted(path for path in REQUIRED_CURRENT_FILES if path not in files)
    if missing:
        raise AssertionError("rev0669 manifest missing paths: " + ", ".join(missing))
    if OLD_ACTIVE_BINARY in files:
        raise AssertionError("manifest must not include old rev0668 active binary")
    if "schema/rev0669/slim-cube-manifest.json" not in set(manifest.get("excluded_mutable_evidence", [])):
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
