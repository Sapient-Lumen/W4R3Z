#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_VALIDATOR = "rev0694 retry-at backoff package validator passed"
EXPECTED_CTEST = "100% tests passed, 0 tests failed out of 27"
EXPECTED_SELFTEST = "anonsync_core sync domain model selftest passed=252 failed=0"
ACTIVE_BINARY = "bin/rev0694/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
OLD_ACTIVE_BINARY = "bin/rev0693/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
AUDIT = ROOT / "audit/rev0694-retry-at-backoff-audit.json"
MANIFEST = ROOT / "schema/rev0694/slim-cube-manifest.json"
VALIDATOR_LOG = "audit/logs/rev0694-retry-at-backoff-package-validator.log"
EXCLUDED_MUTABLE = {"schema/rev0694/slim-cube-manifest.json", VALIDATOR_LOG}

REQUIRED_FILES = [
    "README.md",
    "bin/HISTORY.md",
    "docs/0001-cpp-core-gameplan.md",
    "docs/0003-next-risk-register.md",
    "docs/0084-rev0694-retry-at-backoff.md",
    "docs/0083-rev0693-attempt-cap-abandon.md",
    "docs/0082-rev0692-reclaim-event-history.md",
    "docs/0081-rev0691-resume-lease-reclaim.md",
    "docs/0080-rev0690-resume-claim-split.md",
    "docs/0079-rev0689-mission-reclaim-compass.md",
    "docs/0078-rev0688-resume-workorder-lease.md",
    "cpp/anonsync_core/README.md",
    "cpp/anonsync_core/include/anonsync_core.hpp",
    "cpp/anonsync_core/src/sync_domain.cpp",
    ACTIVE_BINARY,
    "audit/rev0694-retry-at-backoff-audit.json",
    "audit/rev0694-retry-at-backoff-source.patch",
    "audit/logs/rev0694-release-configure.log",
    "audit/logs/rev0694-release-build-final.log",
    "audit/logs/rev0694-release-ctest.log",
    "audit/logs/rev0694-packaged-sync-domain-selftest.log",
    "audit/logs/rev0694-asan-ubsan-configure.log",
    "audit/logs/rev0694-asan-ubsan-build-final.log",
    "audit/logs/rev0694-asan-ubsan-sync-domain-selftest.log",
    "audit/logs/rev0694-binary-sha256.txt",
    "audit/logs/rev0694-binary-ldd.txt",
    VALIDATOR_LOG,
    "tools/validate_rev0694_retry_at_backoff.py",
    "schema/rev0694/slim-cube-manifest.json",
]

REQUIRED_PHRASES = {
    "README.md": [
        "AnonSync slim C++ working cube — rev0694",
        "Rev0694 is **code-bearing**",
        "retry_at_epoch",
        "workorder_retry_backoff_seconds",
        "retry-window-gated expired reclaim",
        "folder convergence under evidence-bound local truth",
        EXPECTED_SELFTEST,
    ],
    "bin/HISTORY.md": [
        "rev0694",
        ACTIVE_BINARY,
        "deterministic retry-at backoff scheduling",
        "rev0693 runnable binary is intentionally omitted",
    ],
    "cpp/anonsync_core/README.md": [
        "anonsync_core rev0694",
        "workorder_retry_backoff_seconds",
        "retry_at_epoch",
        "previous_retry_at_epoch",
        "new_retry_at_epoch",
        EXPECTED_SELFTEST,
    ],
    "docs/0084-rev0694-retry-at-backoff.md": [
        "Rev0694 — retry-at backoff scheduling",
        "retry_at_epoch = lease_expires_at_epoch + (workorder_retry_backoff_seconds * n)",
        "previous_retry_at_epoch",
        "new_retry_at_epoch",
        "Rev0695 should use this scheduling evidence to add the first durable quarantine state",
        "Project-Name-rev####-YYYY.MM.DD.HH.MM-foobarnamesummaryhighlightcodename.zip",
    ],
    "docs/0001-cpp-core-gameplan.md": [
        "current rev0694 code slice",
        "deterministic retry-at scheduling",
        "expired/retry-open → reclaimed",
        "Add quarantine transitions",
        EXPECTED_SELFTEST,
    ],
    "docs/0003-next-risk-register.md": [
        "Next risk register after rev0694",
        "No quarantine transition",
        "retry_at_epoch",
        "expired/retry-open/at-cap → abandoned",
        EXPECTED_SELFTEST,
    ],
    "cpp/anonsync_core/include/anonsync_core.hpp": [
        "std::uint64_t workorder_retry_backoff_seconds = 0;",
        "std::uint64_t retry_at_epoch = 0;",
        "std::uint64_t max_workorder_claim_attempts = 0;",
        "std::uint64_t workorder_abandon_events_written = 0;",
    ],
    "cpp/anonsync_core/src/sync_domain.cpp": [
        "retry_at_epoch INTEGER NOT NULL CHECK(retry_at_epoch >= lease_expires_at_epoch)",
        "previous_retry_at_epoch INTEGER NOT NULL CHECK(previous_retry_at_epoch >= previous_lease_expires_at_epoch)",
        "new_retry_at_epoch INTEGER NOT NULL CHECK(new_retry_at_epoch >= new_lease_expires_at_epoch)",
        "compute_resume_transfer_workorder_retry_at_or_throw",
        "transfer workorder row lease is expired but retry_at_epoch has not opened",
        "resume transfer retry-backoff reclaim audit event count",
    ],
    "audit/rev0694-retry-at-backoff-audit.json": [
        "retry-at-backoff",
        "workorder_retry_backoff_seconds",
        "previous_retry_at_epoch",
        "no durable quarantined workorder state",
    ],
    "audit/rev0694-retry-at-backoff-source.patch": [
        "0084-rev0694-retry-at-backoff.md",
        "retry_at_epoch",
        "validate_rev0694_retry_at_backoff.py",
    ],
}


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def rel_files():
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT).as_posix()
        if "__pycache__" in rel or rel.endswith(".pyc"):
            continue
        yield rel


def assert_exists() -> None:
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).exists()]
    if missing:
        raise AssertionError("missing required rev0694 files: " + ", ".join(missing))
    if (ROOT / OLD_ACTIVE_BINARY).exists():
        raise AssertionError("old rev0693 active binary must be omitted from the slim rev0694 package")
    if (ROOT / ACTIVE_BINARY).stat().st_mode & 0o111 == 0:
        raise AssertionError("active rev0694 binary must be executable")
    materialize_slice = (ROOT / "cpp/anonsync_core/include/anonsync_core.hpp").read_text(errors="replace").split("struct SyncSessionCheckpointMaterializeResumeResult", 1)[1].split("struct SyncSessionCheckpointCleanupResumeOptions", 1)[0]
    for forbidden in ["workorder_claim_now_epoch", "worker_lease_seconds", "lease_expires_at_epoch", "workorder_reclaim_events_written", "workorder_abandon_events_written", "retry_at_epoch"]:
        if forbidden in materialize_slice:
            raise AssertionError("transfer workorder field leaked into materialization result surface: " + forbidden)


def assert_phrases() -> None:
    for rel, phrases in REQUIRED_PHRASES.items():
        text = (ROOT / rel).read_text(errors="replace")
        for phrase in phrases:
            if phrase not in text:
                raise AssertionError(f"required phrase missing from {rel}: {phrase}")


def assert_logs() -> None:
    if EXPECTED_CTEST not in (ROOT / "audit/logs/rev0694-release-ctest.log").read_text(errors="replace"):
        raise AssertionError("release ctest log missing expected pass line")
    if EXPECTED_SELFTEST not in (ROOT / "audit/logs/rev0694-packaged-sync-domain-selftest.log").read_text(errors="replace"):
        raise AssertionError("packaged sync-domain selftest log missing expected pass line")
    if EXPECTED_SELFTEST not in (ROOT / "audit/logs/rev0694-asan-ubsan-sync-domain-selftest.log").read_text(errors="replace"):
        raise AssertionError("asan/ubsan sync-domain selftest log missing expected pass line")
    if "Built target anonsync_core" not in (ROOT / "audit/logs/rev0694-release-build-final.log").read_text(errors="replace"):
        raise AssertionError("release build final log missing built target line")
    if "Built target anonsync_core" not in (ROOT / "audit/logs/rev0694-asan-ubsan-build-final.log").read_text(errors="replace"):
        raise AssertionError("asan/ubsan build final log missing built target line")
    validator_log = ROOT / VALIDATOR_LOG
    if validator_log.exists():
        text = validator_log.read_text(errors="replace")
        if text.strip() and EXPECTED_VALIDATOR not in text:
            raise AssertionError("rev0694 validator log exists but is missing expected pass line")


def assert_audit() -> None:
    audit = json.loads(AUDIT.read_text())
    if audit.get("revision_id") != "rev0694" or audit.get("parent_revision") != "rev0693":
        raise AssertionError("audit revision lineage mismatch")
    if audit.get("codename") != "retry-at-backoff":
        raise AssertionError("audit codename mismatch")
    if audit.get("manifest_kind") != "code-bearing-retry-at-backoff":
        raise AssertionError("audit manifest kind mismatch")
    if audit.get("product_mission") != "cxx-p2p-file-sync":
        raise AssertionError("audit product mission mismatch")
    if audit.get("cxx_behavior_changed") is not True:
        raise AssertionError("rev0694 must be marked code-bearing")
    if audit.get("active_binary") != ACTIVE_BINARY:
        raise AssertionError("audit active binary mismatch")
    if audit.get("active_binary_sha256") != sha_file(ROOT / ACTIVE_BINARY):
        raise AssertionError("audit active binary sha mismatch")
    validation = audit.get("validation", {})
    if validation.get("release_ctest") != EXPECTED_CTEST:
        raise AssertionError("audit release ctest summary mismatch")
    if validation.get("sync_domain_selftest") != EXPECTED_SELFTEST:
        raise AssertionError("audit selftest summary mismatch")
    if validation.get("asan_ubsan_sync_domain_selftest") != EXPECTED_SELFTEST:
        raise AssertionError("audit asan/ubsan summary mismatch")
    if validation.get("package_validator_summary") != EXPECTED_VALIDATOR:
        raise AssertionError("audit package validator summary mismatch")
    changed = audit.get("sqlite_schema_added_or_changed", [])
    for required in ["sync_session_resume_transfer_workorders.retry_at_epoch", "sync_session_resume_transfer_workorder_reclaim_events.new_retry_at_epoch"]:
        if required not in changed:
            raise AssertionError("audit missing schema change: " + required)


def assert_binary_hash() -> None:
    sha_log = (ROOT / "audit/logs/rev0694-binary-sha256.txt").read_text().split()[0]
    if sha_file(ROOT / ACTIVE_BINARY) != sha_log:
        raise AssertionError("active binary sha256 mismatch")


def assert_manifest() -> None:
    manifest = json.loads(MANIFEST.read_text())
    if manifest.get("revision_id") != "rev0694" or manifest.get("parent_revision") != "rev0693":
        raise AssertionError("manifest lineage mismatch")
    if manifest.get("codename") != "retry-at-backoff":
        raise AssertionError("manifest codename mismatch")
    if manifest.get("manifest_kind") != "code-bearing-retry-at-backoff":
        raise AssertionError("manifest kind mismatch")
    if manifest.get("product_mission") != "cxx-p2p-file-sync":
        raise AssertionError("manifest product mission mismatch")
    if manifest.get("active_binary") != ACTIVE_BINARY:
        raise AssertionError("manifest active binary mismatch")
    if manifest.get("active_binary_sha256") != sha_file(ROOT / ACTIVE_BINARY):
        raise AssertionError("manifest active binary sha mismatch")
    if set(manifest.get("excluded_mutable_evidence", [])) != EXCLUDED_MUTABLE:
        raise AssertionError("manifest mutable exclusions mismatch")
    validation = manifest.get("validation", {})
    if validation.get("sync_domain_selftest") != EXPECTED_SELFTEST:
        raise AssertionError("manifest selftest mismatch")
    files = {entry["path"]: entry for entry in manifest.get("files", [])}
    actual_files = set(rel_files()) - EXCLUDED_MUTABLE
    if set(files) != actual_files:
        missing = sorted(actual_files - set(files))[:10]
        extra = sorted(set(files) - actual_files)[:10]
        raise AssertionError(f"manifest file set mismatch missing={missing} extra={extra}")
    for rel, entry in files.items():
        path = ROOT / rel
        if entry.get("sha256") != sha_file(path):
            raise AssertionError("manifest sha mismatch for " + rel)
        if entry.get("size_bytes") != path.stat().st_size:
            raise AssertionError("manifest size mismatch for " + rel)


def main() -> None:
    assert_exists()
    assert_phrases()
    assert_logs()
    assert_audit()
    assert_binary_hash()
    assert_manifest()
    print(EXPECTED_VALIDATOR)


if __name__ == "__main__":
    main()
