#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_VALIDATOR = "rev0670 peer transfer round package validator passed"
EXPECTED_CTEST = "100% tests passed, 0 tests failed out of 27"
EXPECTED_SELFTEST = "anonsync_core sync domain model selftest passed=191 failed=0"
ACTIVE_BINARY = "bin/rev0670/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
OLD_ACTIVE_BINARY = "bin/rev0669/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
CAPABILITY_MANIFEST = "gateway/rev0648-cpp-ledger-backend-capabilities.json"
AUDIT = ROOT / "audit/rev0670-peer-transfer-round-audit.json"
MANIFEST = ROOT / "schema/rev0670/slim-cube-manifest.json"

REQUIRED_CURRENT_FILES = [
    "README.md",
    "cpp/anonsync_core/README.md",
    "cpp/anonsync_core/include/anonsync_core.hpp",
    "cpp/anonsync_core/src/sync_domain.cpp",
    ACTIVE_BINARY,
    "bin/HISTORY.md",
    "docs/0001-cpp-core-gameplan.md",
    "docs/0003-next-risk-register.md",
    "docs/0060-rev0670-peer-transfer-round.md",
    "audit/rev0670-peer-transfer-round-audit.json",
    "audit/rev0670-peer-transfer-round-source.patch",
    "audit/logs/rev0670-release-o0-configure.log",
    "audit/logs/rev0670-release-o0-build.log",
    "audit/logs/rev0670-release-o0-ctest.log",
    "audit/logs/rev0670-peer-transfer-round-selftest.log",
    "audit/logs/rev0670-narrow-asan-ubsan-sync-domain-build.log",
    "audit/logs/rev0670-narrow-asan-ubsan-sync-domain-selftest.log",
    "audit/logs/rev0670-binary-sha256.txt",
    "audit/logs/rev0670-binary-ldd.txt",
    "audit/logs/rev0670-peer-transfer-round-package-validator.log",
    "tools/validate_rev0670_peer_transfer_round.py",
]

REQUIRED_PHRASES = {
    "README.md": [
        "C++ peer-to-peer file synchronization system",
        "Rev0670",
        "peer transfer-round continuation",
        "SyncPeerChunkTransferRoundResult",
        "accept_sync_peer_chunk_response_batch_and_plan_next",
        "sync-peer-chunk-schedule:v1",
        "not yet",
    ],
    "cpp/anonsync_core/README.md": [
        "anonsync_core rev0670",
        "SyncPeerChunkTransferRoundResult",
        "accept_sync_peer_chunk_response_batch_and_plan_next",
        "peer transfer-round continuation",
        "filters next-peer availability",
    ],
    "cpp/anonsync_core/include/anonsync_core.hpp": [
        "struct SyncPeerChunkTransferRoundResult",
        "SyncPeerChunkResponseBatchAcceptanceResult peer_batch_acceptance;",
        "SyncPeerChunkScheduleResult next_peer_schedule;",
        "bool peer_work_scheduled = false;",
        "accept_sync_peer_chunk_response_batch_and_plan_next",
    ],
    "cpp/anonsync_core/src/sync_domain.cpp": [
        "SyncValidationResult accept_sync_peer_chunk_response_batch_and_plan_next",
        "validate_peer_round_next_availabilities_for_remote",
        "peer_availabilities_limited_to_request",
        "peer chunk transfer round requires matching write and inspection roots",
        "peer transfer round accepts one scheduled peer batch, reinspects, and filters broad next-peer availability into a continuation schedule",
        "peer transfer round marks a fully received staged file materialization-ready and emits an empty complete schedule",
        "peer transfer round rejects invalid next-peer availability before invoking receipt-backed acceptance",
    ],
    "docs/0060-rev0670-peer-transfer-round.md": [
        "peer transfer-round continuation",
        "`SyncPeerChunkTransferRoundResult`",
        "`accept_sync_peer_chunk_response_batch_and_plan_next`",
        "filters next-peer availability",
        "Remaining ceiling",
    ],
    "docs/0001-cpp-core-gameplan.md": [
        "Current rev0670 product slice",
        "accept_sync_peer_chunk_response_batch_and_plan_next",
        "peer transfer-round continuation",
    ],
    "docs/0003-next-risk-register.md": [
        "Next risk register after rev0670",
        "SyncPeerChunkTransferRoundResult",
        "accept_sync_peer_chunk_response_batch_and_plan_next",
    ],
    "bin/HISTORY.md": [
        "rev0670",
        "peer transfer-round continuation seam",
        "rev0669: historical source/audit only",
    ],
    "audit/rev0670-peer-transfer-round-audit.json": [
        "peer-transfer-round",
        "fixed_by_accept_sync_peer_chunk_response_batch_and_plan_next",
        "fixed_by_pre_acceptance_next_peer_availability_validation",
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
        raise AssertionError("missing required rev0670 files: " + ", ".join(missing))
    if (ROOT / OLD_ACTIVE_BINARY).exists():
        raise AssertionError("rev0670 package must not carry the rev0669 active binary")


def assert_phrases() -> None:
    for rel, phrases in REQUIRED_PHRASES.items():
        text = (ROOT / rel).read_text(errors="replace")
        for phrase in phrases:
            if phrase not in text:
                raise AssertionError(f"required phrase missing from {rel}: {phrase}")


def assert_logs() -> None:
    ctest = (ROOT / "audit/logs/rev0670-release-o0-ctest.log").read_text(errors="replace")
    if EXPECTED_CTEST not in ctest:
        raise AssertionError("release ctest summary missing")
    selftest = (ROOT / "audit/logs/rev0670-peer-transfer-round-selftest.log").read_text(errors="replace")
    if EXPECTED_SELFTEST not in selftest:
        raise AssertionError("sync-domain selftest summary missing")
    asan = (ROOT / "audit/logs/rev0670-narrow-asan-ubsan-sync-domain-selftest.log").read_text(errors="replace")
    if EXPECTED_SELFTEST not in asan:
        raise AssertionError("narrow asan/ubsan selftest summary missing")
    validator_log = ROOT / "audit/logs/rev0670-peer-transfer-round-package-validator.log"
    if validator_log.exists() and EXPECTED_VALIDATOR not in validator_log.read_text(errors="replace"):
        raise AssertionError("package validator log exists but is missing expected pass line")


def assert_audit() -> None:
    audit = json.loads(AUDIT.read_text())
    if audit.get("revision_id") != "rev0670" or audit.get("parent_revision") != "rev0669":
        raise AssertionError("audit revision lineage mismatch")
    if audit.get("product_mission") != "cxx-p2p-file-sync":
        raise AssertionError("audit product mission mismatch")
    if audit.get("active_binary") != ACTIVE_BINARY:
        raise AssertionError("audit active binary mismatch")
    if audit.get("active_binary_sha256") != sha_file(ROOT / ACTIVE_BINARY):
        raise AssertionError("audit active binary sha mismatch")
    if not audit.get("cxx_behavior_changed"):
        raise AssertionError("rev0670 must claim C++ behavior changed")
    required_api = {
        "SyncPeerChunkTransferRoundResult added to expose peer-bound acceptance, post-batch inspection, next request plan, next peer schedule, and continuation/materialization flags",
        "accept_sync_peer_chunk_response_batch_and_plan_next added to accept one scheduled peer batch, re-inspect staged receipt state, derive the next sync-chunk-request:v1 plan, and build the next sync-peer-chunk-schedule:v1 result",
        "internal next-peer availability validation added so malformed future peer ids/sessions/chunks are rejected before receipt-backed byte acceptance",
        "internal next-peer availability filtering added so broad peer availability is narrowed to the verified next request before scheduling",
        "sync-domain selftest extended with peer transfer-round root rejection, continuation scheduling, broad availability filtering, final materialization-ready evidence, and invalid next-peer availability rejection",
    }
    missing_api = required_api - set(audit.get("cxx_api_changed", []))
    if missing_api:
        raise AssertionError("audit missing API changes: " + ", ".join(sorted(missing_api)))
    findings = audit.get("audit_findings", {})
    if findings.get("peer_bound_acceptance_stopped_before_continuation") != "fixed_by_accept_sync_peer_chunk_response_batch_and_plan_next":
        raise AssertionError("audit must record peer transfer round fix")
    if findings.get("caller_glue_could_choose_different_write_and_inspection_roots") != "fixed_by_prewrite_root_match_check":
        raise AssertionError("audit must record root mismatch fix")
    if findings.get("future_peer_availability_could_fail_after_byte_acceptance") != "fixed_by_pre_acceptance_next_peer_availability_validation":
        raise AssertionError("audit must record pre-acceptance availability validation")
    validation = audit.get("validation", {})
    if validation.get("release_ctest_summary") != EXPECTED_CTEST:
        raise AssertionError("audit ctest summary mismatch")
    if validation.get("sync_domain_selftest_summary") != EXPECTED_SELFTEST:
        raise AssertionError("audit sync-domain selftest summary mismatch")
    if validation.get("narrow_asan_ubsan_selftest_summary") != EXPECTED_SELFTEST:
        raise AssertionError("audit narrow asan/ubsan selftest summary mismatch")


def assert_binary_sha() -> None:
    line = (ROOT / "audit/logs/rev0670-binary-sha256.txt").read_text().strip().split()
    if len(line) < 2:
        raise AssertionError("binary sha256 log malformed")
    expected_sha, rel = line[0], line[1]
    if rel != ACTIVE_BINARY:
        raise AssertionError("binary sha256 log points at wrong active binary")
    if sha_file(ROOT / ACTIVE_BINARY) != expected_sha:
        raise AssertionError("active binary sha256 mismatch")


def assert_manifest() -> None:
    manifest = json.loads(MANIFEST.read_text())
    if manifest.get("revision_id") != "rev0670" or manifest.get("parent_revision") != "rev0669":
        raise AssertionError("rev0670 manifest lineage mismatch")
    if manifest.get("manifest_kind") != "code-bearing-peer-transfer-round":
        raise AssertionError("rev0670 manifest kind mismatch")
    if manifest.get("product_mission") != "cxx-p2p-file-sync":
        raise AssertionError("rev0670 product mission tag mismatch")
    if manifest.get("codename") != "peer-transfer-round":
        raise AssertionError("rev0670 codename mismatch")
    if manifest.get("active_binary") != ACTIVE_BINARY:
        raise AssertionError("active binary should be rev0670")
    if manifest.get("capability_manifest") != CAPABILITY_MANIFEST:
        raise AssertionError("capability manifest should remain rev0648-bound until sync-ledger capabilities change")
    rows = manifest.get("files", [])
    if manifest.get("file_count") != len(rows):
        raise AssertionError("manifest file_count mismatch")
    files = {item.get("path"): item for item in rows}
    missing = sorted(path for path in REQUIRED_CURRENT_FILES if path not in files)
    if missing:
        raise AssertionError("rev0670 manifest missing paths: " + ", ".join(missing))
    if OLD_ACTIVE_BINARY in files:
        raise AssertionError("manifest must not include old rev0669 active binary")
    if "schema/rev0670/slim-cube-manifest.json" not in set(manifest.get("excluded_mutable_evidence", [])):
        raise AssertionError("manifest must exclude itself")
    for rel, row in files.items():
        if rel == "schema/rev0670/slim-cube-manifest.json":
            continue
        actual = ROOT / rel
        if actual.exists() and row.get("sha256") != sha_file(actual):
            raise AssertionError(f"manifest sha mismatch for {rel}")


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
