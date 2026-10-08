#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_VALIDATOR = "rev0668 peer chunk schedule package validator passed"
EXPECTED_CTEST = "100% tests passed, 0 tests failed out of 27"
EXPECTED_SELFTEST = "anonsync_core sync domain model selftest passed=171 failed=0"
ACTIVE_BINARY = "bin/rev0668/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
OLD_ACTIVE_BINARY = "bin/rev0667/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
CAPABILITY_MANIFEST = "gateway/rev0648-cpp-ledger-backend-capabilities.json"
AUDIT = ROOT / "audit/rev0668-peer-chunk-schedule-audit.json"
MANIFEST = ROOT / "schema/rev0668/slim-cube-manifest.json"

REQUIRED_CURRENT_FILES = [
    "README.md",
    "cpp/anonsync_core/README.md",
    "cpp/anonsync_core/include/anonsync_core.hpp",
    "cpp/anonsync_core/src/sync_domain.cpp",
    ACTIVE_BINARY,
    "bin/HISTORY.md",
    "docs/0001-cpp-core-gameplan.md",
    "docs/0003-next-risk-register.md",
    "docs/0058-rev0668-peer-chunk-schedule.md",
    "audit/rev0668-peer-chunk-schedule-audit.json",
    "audit/rev0668-peer-chunk-schedule-source.patch",
    "audit/logs/rev0668-release-o0-configure.log",
    "audit/logs/rev0668-release-o0-build.log",
    "audit/logs/rev0668-release-o0-ctest.log",
    "audit/logs/rev0668-peer-chunk-schedule-selftest.log",
    "audit/logs/rev0668-narrow-asan-ubsan-sync-domain-build.log",
    "audit/logs/rev0668-narrow-asan-ubsan-sync-domain-selftest.log",
    "audit/logs/rev0668-binary-sha256.txt",
    "audit/logs/rev0668-binary-ldd.txt",
    "audit/logs/rev0668-peer-chunk-schedule-package-validator.log",
    "tools/validate_rev0668_peer_chunk_schedule.py",
]

REQUIRED_PHRASES = {
    "README.md": [
        "C++ peer-to-peer file synchronization system",
        "Rev0668",
        "deterministic peer chunk scheduling",
        "SyncPeerChunkScheduleResult",
        "build_sync_peer_chunk_schedule",
        "sync-peer-chunk-request:v1",
        "not yet",
    ],
    "cpp/anonsync_core/README.md": [
        "anonsync_core rev0668",
        "SyncPeerChunkAvailability",
        "SyncPeerChunkAssignment",
        "SyncPeerChunkScheduleResult",
        "build_sync_peer_chunk_schedule",
        "deterministic peer chunk scheduling",
    ],
    "cpp/anonsync_core/include/anonsync_core.hpp": [
        "struct SyncPeerChunkAvailability",
        "struct SyncPeerChunkAssignment",
        "struct SyncPeerChunkScheduleResult",
        "std::vector<SyncChunkRange> unassigned_chunks;",
        "build_sync_peer_chunk_schedule",
    ],
    "cpp/anonsync_core/src/sync_domain.cpp": [
        "SyncValidationResult build_sync_peer_chunk_schedule",
        "peer chunk schedule duplicate peer_id",
        "peer chunk schedule peer availability must be an ordered unique subset of the request batch",
        "peer chunk schedule deterministically assigns a request batch across sorted peer availability",
        "peer chunk schedule reports exact unassigned chunks when peer availability cannot cover the request batch",
        "sync-peer-chunk-request:v1:",
        "sync-peer-chunk-schedule:v1:",
    ],
    "docs/0058-rev0668-peer-chunk-schedule.md": [
        "peer chunk schedule",
        "`SyncPeerChunkAvailability`",
        "`SyncPeerChunkAssignment`",
        "`SyncPeerChunkScheduleResult`",
        "`build_sync_peer_chunk_schedule`",
        "scheduler drift outside the evidence boundary",
        "still does not run a real peer protocol",
    ],
    "docs/0001-cpp-core-gameplan.md": [
        "Current rev0668 product slice",
        "build_sync_peer_chunk_schedule",
        "peer chunk scheduling",
    ],
    "docs/0003-next-risk-register.md": [
        "Next risk register after rev0668",
        "SyncPeerChunkScheduleResult",
        "build_sync_peer_chunk_schedule",
    ],
    "bin/HISTORY.md": [
        "rev0668",
        "peer chunk scheduling seam",
        "rev0667: historical source/audit only",
    ],
    "audit/rev0668-peer-chunk-schedule-audit.json": [
        "peer-chunk-schedule",
        "fixed_by_build_sync_peer_chunk_schedule",
        "fixed_by_duplicate_peer_id_rejection",
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
        raise AssertionError("missing required rev0668 files: " + ", ".join(missing))
    if (ROOT / OLD_ACTIVE_BINARY).exists():
        raise AssertionError("rev0668 package must not carry the rev0667 active binary")


def assert_phrases() -> None:
    for rel, phrases in REQUIRED_PHRASES.items():
        text = (ROOT / rel).read_text(errors="replace")
        for phrase in phrases:
            if phrase not in text:
                raise AssertionError(f"required phrase missing from {rel}: {phrase}")


def assert_logs() -> None:
    ctest = (ROOT / "audit/logs/rev0668-release-o0-ctest.log").read_text(errors="replace")
    if EXPECTED_CTEST not in ctest:
        raise AssertionError("release ctest summary missing")
    selftest = (ROOT / "audit/logs/rev0668-peer-chunk-schedule-selftest.log").read_text(errors="replace")
    if EXPECTED_SELFTEST not in selftest:
        raise AssertionError("sync-domain selftest summary missing")
    asan = (ROOT / "audit/logs/rev0668-narrow-asan-ubsan-sync-domain-selftest.log").read_text(errors="replace")
    if EXPECTED_SELFTEST not in asan:
        raise AssertionError("narrow asan/ubsan selftest summary missing")
    validator_log = ROOT / "audit/logs/rev0668-peer-chunk-schedule-package-validator.log"
    if validator_log.exists() and EXPECTED_VALIDATOR not in validator_log.read_text(errors="replace"):
        raise AssertionError("package validator log exists but is missing expected pass line")


def assert_audit() -> None:
    audit = json.loads(AUDIT.read_text())
    if audit.get("revision_id") != "rev0668" or audit.get("parent_revision") != "rev0667":
        raise AssertionError("audit revision lineage mismatch")
    if audit.get("product_mission") != "cxx-p2p-file-sync":
        raise AssertionError("audit product mission mismatch")
    if audit.get("active_binary") != ACTIVE_BINARY:
        raise AssertionError("audit active binary mismatch")
    if audit.get("active_binary_sha256") != sha_file(ROOT / ACTIVE_BINARY):
        raise AssertionError("audit active binary sha mismatch")
    if not audit.get("cxx_behavior_changed"):
        raise AssertionError("rev0668 must claim C++ behavior changed")
    required_api = {
        "SyncPeerChunkAvailability added to represent one peer/session availability subset for a selected chunk request batch",
        "SyncPeerChunkAssignment added to carry per-peer assigned chunks and sync-peer-chunk-request:v1 evidence",
        "SyncPeerChunkScheduleResult added to carry schedule id, assigned totals, full-coverage status, assignments, and exact unassigned chunks",
        "build_sync_peer_chunk_schedule added to validate request evidence, peer availability, duplicate peers, per-peer budgets, and deterministic assignment",
        "sync-domain selftest extended with deterministic multi-peer scheduling, partial coverage, duplicate peer rejection, and out-of-request availability rejection",
    }
    missing_api = required_api - set(audit.get("cxx_api_changed", []))
    if missing_api:
        raise AssertionError("audit missing API changes: " + ", ".join(sorted(missing_api)))
    findings = audit.get("audit_findings", {})
    if findings.get("peer_selection_was_left_to_session_glue") != "fixed_by_build_sync_peer_chunk_schedule":
        raise AssertionError("audit must record peer selection fix")
    if findings.get("duplicate_peer_availability_could_create_ambiguous_network_work") != "fixed_by_duplicate_peer_id_rejection":
        raise AssertionError("audit must record duplicate peer rejection")
    if findings.get("peer_advertisement_could_include_chunks_outside_current_request") != "fixed_by_ordered_unique_subset_check_against_request_batch":
        raise AssertionError("audit must record out-of-request availability rejection")
    if findings.get("partial_peer_coverage_needed_explicit_resume_state") != "fixed_by_unassigned_chunks_in_SyncPeerChunkScheduleResult":
        raise AssertionError("audit must record unassigned chunk state")
    validation = audit.get("validation", {})
    if validation.get("release_ctest_summary") != EXPECTED_CTEST:
        raise AssertionError("audit ctest summary mismatch")
    if validation.get("sync_domain_selftest_summary") != EXPECTED_SELFTEST:
        raise AssertionError("audit sync-domain selftest summary mismatch")
    if validation.get("narrow_asan_ubsan_selftest_summary") != EXPECTED_SELFTEST:
        raise AssertionError("audit narrow asan/ubsan selftest summary mismatch")


def assert_binary_sha() -> None:
    line = (ROOT / "audit/logs/rev0668-binary-sha256.txt").read_text().strip().split()
    if len(line) < 2:
        raise AssertionError("binary sha256 log malformed")
    expected_sha, rel = line[0], line[1]
    if rel != ACTIVE_BINARY:
        raise AssertionError("binary sha256 log points at wrong active binary")
    if sha_file(ROOT / ACTIVE_BINARY) != expected_sha:
        raise AssertionError("active binary sha256 mismatch")


def assert_manifest() -> None:
    manifest = json.loads(MANIFEST.read_text())
    if manifest.get("revision_id") != "rev0668" or manifest.get("parent_revision") != "rev0667":
        raise AssertionError("rev0668 manifest lineage mismatch")
    if manifest.get("manifest_kind") != "code-bearing-peer-chunk-schedule":
        raise AssertionError("rev0668 manifest kind mismatch")
    if manifest.get("product_mission") != "cxx-p2p-file-sync":
        raise AssertionError("rev0668 product mission tag mismatch")
    if manifest.get("codename") != "peer-chunk-schedule":
        raise AssertionError("rev0668 codename mismatch")
    if manifest.get("active_binary") != ACTIVE_BINARY:
        raise AssertionError("active binary should be rev0668")
    if manifest.get("capability_manifest") != CAPABILITY_MANIFEST:
        raise AssertionError("capability manifest should remain rev0648-bound until sync-ledger capabilities change")
    rows = manifest.get("files", [])
    if manifest.get("file_count") != len(rows):
        raise AssertionError("manifest file_count mismatch")
    files = {item.get("path"): item for item in rows}
    missing = sorted(path for path in REQUIRED_CURRENT_FILES if path not in files)
    if missing:
        raise AssertionError("rev0668 manifest missing paths: " + ", ".join(missing))
    if OLD_ACTIVE_BINARY in files:
        raise AssertionError("manifest must not include old rev0667 active binary")
    if "schema/rev0668/slim-cube-manifest.json" not in set(manifest.get("excluded_mutable_evidence", [])):
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
