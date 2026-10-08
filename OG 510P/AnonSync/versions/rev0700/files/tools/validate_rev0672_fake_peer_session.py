#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_VALIDATOR = "rev0672 fake peer session package validator passed"
EXPECTED_CTEST = "100% tests passed, 0 tests failed out of 27"
EXPECTED_SELFTEST = "anonsync_core sync domain model selftest passed=196 failed=0"
ACTIVE_BINARY = "bin/rev0672/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
OLD_ACTIVE_BINARY = "bin/rev0670/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
CAPABILITY_MANIFEST = "gateway/rev0648-cpp-ledger-backend-capabilities.json"
AUDIT = ROOT / "audit/rev0672-fake-peer-session-audit.json"
MANIFEST = ROOT / "schema/rev0672/slim-cube-manifest.json"

REQUIRED_CURRENT_FILES = [
    "README.md",
    "cpp/anonsync_core/README.md",
    "cpp/anonsync_core/include/anonsync_core.hpp",
    "cpp/anonsync_core/src/sync_domain.cpp",
    ACTIVE_BINARY,
    "bin/HISTORY.md",
    "docs/0001-cpp-core-gameplan.md",
    "docs/0003-next-risk-register.md",
    "docs/0062-rev0672-fake-peer-session.md",
    "audit/rev0672-fake-peer-session-audit.json",
    "audit/rev0672-fake-peer-session-source.patch",
    "audit/logs/rev0672-release-o0-configure.log",
    "audit/logs/rev0672-release-o0-build.log",
    "audit/logs/rev0672-release-o0-ctest.log",
    "audit/logs/rev0672-fake-peer-session-selftest.log",
    "audit/logs/rev0672-narrow-asan-ubsan-sync-domain-configure.log",
    "audit/logs/rev0672-narrow-asan-ubsan-sync-domain-build.log",
    "audit/logs/rev0672-narrow-asan-ubsan-sync-domain-selftest.log",
    "audit/logs/rev0672-binary-sha256.txt",
    "audit/logs/rev0672-binary-ldd.txt",
    "audit/logs/rev0672-fake-peer-session-package-validator.log",
    "tools/validate_rev0672_fake_peer_session.py",
    "schema/rev0672/slim-cube-manifest.json",
]

REQUIRED_PHRASES = {
    "README.md": [
        "AnonSync slim C++ working cube — rev0672",
        "C++ peer-to-peer file synchronization system",
        "Rev0672 is code-bearing",
        "bin/rev0672/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3",
        "fake peer-session convergence harness",
        "run_sync_fake_peer_file_fetch_session",
        "SyncFakePeerFileFetchSessionOptions",
        "scan → manifest diff → local apply planning → staged-transfer inspection → chunk request planning → peer chunk scheduling",
        "publisher-neutral content convergence proof",
        "not yet",
    ],
    "cpp/anonsync_core/README.md": [
        "anonsync_core rev0672",
        "SyncFakePeerFileFetchSessionOptions",
        "SyncFakePeerFileFetchSessionResult",
        "SyncFakePeerFileFetchSessionFileResult",
        "run_sync_fake_peer_file_fetch_session",
        "source/destination fake peer file-fetch session",
        "publisher-neutral file-content convergence",
        "The harness covers file fetch convergence only",
    ],
    "cpp/anonsync_core/include/anonsync_core.hpp": [
        "struct SyncFakePeerFileFetchSessionOptions",
        "struct SyncFakePeerFileFetchSessionFileResult",
        "struct SyncFakePeerFileFetchSessionResult",
        "std::uint64_t max_transfer_rounds = 1024;",
        "bool require_chunk_receipts_for_materialization = true;",
        "SyncFolderManifest destination_manifest_after;",
        "bool content_converged = false;",
        "run_sync_fake_peer_file_fetch_session",
    ],
    "cpp/anonsync_core/src/sync_domain.cpp": [
        "SyncValidationResult run_sync_fake_peer_file_fetch_session",
        "fake peer file-fetch session source and destination roots must not overlap",
        "fake peer file-fetch session staging root must be outside source and destination roots",
        "build_sync_manifest_diff_plan(destination_before, source_manifest, diff_plan)",
        "build_sync_local_apply_plan(diff_plan, apply_options, apply_plan)",
        "SyncValidationResult schedule_result = build_sync_peer_chunk_schedule(*remote_entry,",
        "accept_sync_peer_chunk_response_batch_and_plan_next(*remote_entry",
        "materialize_staged_sync_file(*remote_entry",
        "convergence_content_digest_for_manifest(source_manifest)",
        "fake peer file-fetch session only supports remote file fetch apply entries",
        "fake peer file-fetch session drives scan, diff, local apply, peer rounds, materialization, and rescan convergence",
        "fake peer file-fetch session rejects overlapping staging roots before scan or transfer mutation",
    ],
    "docs/0062-rev0672-fake-peer-session.md": [
        "Rev0672 — fake peer-session convergence harness",
        "run_sync_fake_peer_file_fetch_session",
        "Audit/refactor performed",
        "source scan → destination scan → manifest diff → local apply plan",
        "publisher-neutral convergence-content digest",
        "anonsync_core sync domain model selftest passed=196 failed=0",
        "Remaining ceiling",
    ],
    "docs/0001-cpp-core-gameplan.md": [
        "Current rev0672 product slice — fake peer-session convergence harness",
        "run_sync_fake_peer_file_fetch_session",
        "publisher-neutral content convergence",
        "100% tests passed, 0 tests failed out of 27",
    ],
    "docs/0003-next-risk-register.md": [
        "Next risk register after rev0672",
        "Rev0672 priority note",
        "run_sync_fake_peer_file_fetch_session",
        "durable session state",
    ],
    "bin/HISTORY.md": [
        "rev0672",
        "fake peer-session convergence harness",
        "rev0670: historical source/audit only",
    ],
    "audit/rev0672-fake-peer-session-audit.json": [
        "fake-peer-session",
        "fixed_by_run_sync_fake_peer_file_fetch_session",
        "fixed_by_source_destination_and_staging_overlap_rejection_before_scan_or_write",
        "fixed_by_publisher_neutral_convergence_content_digest_helpers",
        "package_validator_summary",
    ],
    "audit/rev0672-fake-peer-session-source.patch": [
        "0062-rev0672-fake-peer-session.md",
        "SyncFakePeerFileFetchSessionOptions",
        "run_sync_fake_peer_file_fetch_session",
        "validate_rev0672_fake_peer_session.py",
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
        raise AssertionError("missing required rev0672 files: " + ", ".join(missing))
    if (ROOT / OLD_ACTIVE_BINARY).exists():
        raise AssertionError("rev0672 package must not carry the rev0670 active binary")


def assert_phrases() -> None:
    for rel, phrases in REQUIRED_PHRASES.items():
        text = (ROOT / rel).read_text(errors="replace")
        for phrase in phrases:
            if phrase not in text:
                raise AssertionError(f"required phrase missing from {rel}: {phrase}")


def assert_logs() -> None:
    ctest = (ROOT / "audit/logs/rev0672-release-o0-ctest.log").read_text(errors="replace")
    if EXPECTED_CTEST not in ctest:
        raise AssertionError("release ctest summary missing")
    selftest = (ROOT / "audit/logs/rev0672-fake-peer-session-selftest.log").read_text(errors="replace")
    if EXPECTED_SELFTEST not in selftest:
        raise AssertionError("sync-domain selftest summary missing")
    asan = (ROOT / "audit/logs/rev0672-narrow-asan-ubsan-sync-domain-selftest.log").read_text(errors="replace")
    if EXPECTED_SELFTEST not in asan:
        raise AssertionError("narrow asan/ubsan selftest summary missing")
    build = (ROOT / "audit/logs/rev0672-release-o0-build.log").read_text(errors="replace")
    if "Built target anonsync_core" not in build:
        raise AssertionError("release build log missing built target line")
    validator_log = ROOT / "audit/logs/rev0672-fake-peer-session-package-validator.log"
    if validator_log.exists() and EXPECTED_VALIDATOR not in validator_log.read_text(errors="replace"):
        raise AssertionError("package validator log exists but is missing expected pass line")


def assert_audit() -> None:
    audit = json.loads(AUDIT.read_text())
    if audit.get("revision_id") != "rev0672" or audit.get("parent_revision") != "rev0671":
        raise AssertionError("audit revision lineage mismatch")
    if audit.get("product_mission") != "cxx-p2p-file-sync":
        raise AssertionError("audit product mission mismatch")
    if audit.get("codename") != "fake-peer-session":
        raise AssertionError("audit codename mismatch")
    if audit.get("active_binary") != ACTIVE_BINARY:
        raise AssertionError("audit active binary mismatch")
    if audit.get("active_binary_sha256") != sha_file(ROOT / ACTIVE_BINARY):
        raise AssertionError("audit active binary sha mismatch")
    if audit.get("cxx_behavior_changed") is not True:
        raise AssertionError("rev0672 must claim C++ behavior changed")
    required_api = {
        "SyncFakePeerFileFetchSessionOptions added to configure source, destination, staging, folder, device, peer, session, counter, chunk-budget, peer-round-budget, max-round, and receipt-gating inputs",
        "SyncFakePeerFileFetchSessionFileResult added to expose per-path transfer rounds, chunk writes, receipt reuse, materialized bytes, source/destination content hashes, receipt gating, and materialization status",
        "SyncFakePeerFileFetchSessionResult added to expose source/destination manifests, diff plan, local apply plan, destination rescan, aggregate transfer evidence, convergence digests, and file-level results",
        "run_sync_fake_peer_file_fetch_session added to drive scan, manifest diff, local apply, staged inspection, chunk request, peer schedule, peer-bound transfer rounds, receipt-gated materialization, and destination rescan convergence for remote file fetches",
        "sync-domain selftest extended with a two-file fake peer session, bounded chunk request and peer-round caps, exact byte materialization checks, content-digest convergence checks, and root-overlap rejection",
    }
    missing_api = required_api - set(audit.get("cxx_api_changed", []))
    if missing_api:
        raise AssertionError("audit missing API changes: " + ", ".join(sorted(missing_api)))
    findings = audit.get("audit_findings", {})
    if findings.get("session_loop_only_existed_as_caller_glue") != "fixed_by_run_sync_fake_peer_file_fetch_session":
        raise AssertionError("audit must record fake session loop fix")
    if findings.get("fake_session_root_overlap_could_mutate_sync_tree") != "fixed_by_source_destination_and_staging_overlap_rejection_before_scan_or_write":
        raise AssertionError("audit must record root overlap fix")
    if findings.get("publisher_lineage_equality_was_wrong_convergence_evidence_after_rescan") != "fixed_by_publisher_neutral_convergence_content_digest_helpers":
        raise AssertionError("audit must record convergence digest fix")
    validation = audit.get("validation", {})
    if validation.get("release_ctest_summary") != EXPECTED_CTEST:
        raise AssertionError("audit ctest summary mismatch")
    if validation.get("sync_domain_selftest_summary") != EXPECTED_SELFTEST:
        raise AssertionError("audit sync-domain selftest summary mismatch")
    if validation.get("narrow_asan_ubsan_selftest_summary") != EXPECTED_SELFTEST:
        raise AssertionError("audit narrow asan/ubsan selftest summary mismatch")
    if validation.get("package_validator_summary") != EXPECTED_VALIDATOR:
        raise AssertionError("audit package validator summary mismatch")


def assert_binary_sha() -> None:
    line = (ROOT / "audit/logs/rev0672-binary-sha256.txt").read_text().strip().split()
    if len(line) < 2:
        raise AssertionError("binary sha256 log malformed")
    expected_sha, rel = line[0], line[1]
    if rel != ACTIVE_BINARY:
        raise AssertionError("binary sha256 log points at wrong active binary")
    if sha_file(ROOT / ACTIVE_BINARY) != expected_sha:
        raise AssertionError("active binary sha256 mismatch")


def assert_manifest() -> None:
    manifest = json.loads(MANIFEST.read_text())
    if manifest.get("revision_id") != "rev0672" or manifest.get("parent_revision") != "rev0671":
        raise AssertionError("rev0672 manifest lineage mismatch")
    if manifest.get("manifest_kind") != "code-bearing-fake-peer-session":
        raise AssertionError("rev0672 manifest kind mismatch")
    if manifest.get("product_mission") != "cxx-p2p-file-sync":
        raise AssertionError("rev0672 product mission tag mismatch")
    if manifest.get("codename") != "fake-peer-session":
        raise AssertionError("rev0672 codename mismatch")
    if manifest.get("active_binary") != ACTIVE_BINARY:
        raise AssertionError("active binary should be rev0672")
    if manifest.get("capability_manifest") != CAPABILITY_MANIFEST:
        raise AssertionError("capability manifest should remain rev0648-bound until sync-ledger capabilities change")
    if "schema/rev0672/slim-cube-manifest.json" not in set(manifest.get("excluded_mutable_evidence", [])):
        raise AssertionError("manifest must exclude itself")
    expected_files = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT).as_posix()
        if rel == "schema/rev0672/slim-cube-manifest.json":
            continue
        expected_files.append(rel)
    expected_files.sort()
    rows = manifest.get("files", [])
    files = {item.get("path"): item for item in rows}
    if manifest.get("file_count") != len(expected_files) or len(rows) != len(expected_files):
        raise AssertionError("manifest file_count mismatch")
    if set(files) != set(expected_files):
        missing = sorted(set(expected_files) - set(files))[:12]
        extra = sorted(set(files) - set(expected_files))[:12]
        raise AssertionError(f"manifest path set mismatch missing={missing} extra={extra}")
    if OLD_ACTIVE_BINARY in files:
        raise AssertionError("manifest must not include old rev0670 active binary")
    for rel in expected_files:
        item = files[rel]
        path = ROOT / rel
        if item.get("sha256") != sha_file(path) or item.get("size_bytes") != path.stat().st_size:
            raise AssertionError(f"manifest digest/size mismatch for {rel}")


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
