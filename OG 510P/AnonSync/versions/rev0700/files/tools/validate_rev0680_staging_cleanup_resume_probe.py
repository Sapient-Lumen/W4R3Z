#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_VALIDATOR = "rev0680 staging cleanup resume probe package validator passed"
EXPECTED_CTEST = "100% tests passed, 0 tests failed out of 27"
EXPECTED_SELFTEST = "anonsync_core sync domain model selftest passed=212 failed=0"
ACTIVE_BINARY = "bin/rev0680/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
OLD_ACTIVE_BINARY = "bin/rev0679/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
CAPABILITY_MANIFEST = "gateway/rev0648-cpp-ledger-backend-capabilities.json"
AUDIT = ROOT / "audit/rev0680-staging-cleanup-resume-probe-audit.json"
MANIFEST = ROOT / "schema/rev0680/slim-cube-manifest.json"
VALIDATOR_LOG = "audit/logs/rev0680-staging-cleanup-resume-probe-package-validator.log"
EXCLUDED_MUTABLE = {"schema/rev0680/slim-cube-manifest.json", VALIDATOR_LOG}

REQUIRED_CURRENT_FILES = [
    "README.md",
    "cpp/anonsync_core/README.md",
    "cpp/anonsync_core/include/anonsync_core.hpp",
    "cpp/anonsync_core/src/sync_domain.cpp",
    ACTIVE_BINARY,
    "bin/HISTORY.md",
    "docs/0001-cpp-core-gameplan.md",
    "docs/0003-next-risk-register.md",
    "docs/0070-rev0680-staging-cleanup-resume-probe.md",
    "audit/rev0680-staging-cleanup-resume-probe-audit.json",
    "audit/rev0680-staging-cleanup-resume-probe-source.patch",
    "audit/logs/rev0680-release-configure.log",
    "audit/logs/rev0680-release-build.log",
    "audit/logs/rev0680-release-ctest.log",
    "audit/logs/rev0680-staging-cleanup-resume-probe-selftest.log",
    "audit/logs/rev0680-narrow-asan-ubsan-sync-domain-configure.log",
    "audit/logs/rev0680-narrow-asan-ubsan-sync-domain-build.log",
    "audit/logs/rev0680-narrow-asan-ubsan-sync-domain-selftest.log",
    "audit/logs/rev0680-binary-sha256.txt",
    "audit/logs/rev0680-binary-ldd.txt",
    "tools/validate_rev0680_staging_cleanup_resume_probe.py",
    "schema/rev0680/slim-cube-manifest.json",
]

REQUIRED_PHRASES = {
    "README.md": [
        "AnonSync slim C++ working cube — rev0680",
        "staging cleanup resume probe",
        "require_staging_artifacts_cleaned",
        "staging_artifacts_verified",
        EXPECTED_SELFTEST,
        "does not replay checkpoint rows into resumed work",
    ],
    "cpp/anonsync_core/README.md": [
        "anonsync_core rev0680",
        "staging cleanup resume probe",
        "require_staging_artifacts_cleaned",
        "staging_receipt_directories_present",
        "docs/session-report.txt",
    ],
    "cpp/anonsync_core/include/anonsync_core.hpp": [
        "bool require_staging_artifacts_cleaned = true;",
        "bool staging_artifacts_verified = false;",
        "std::uint64_t staging_artifact_paths_checked = 0;",
        "std::uint64_t staging_receipt_directories_present = 0;",
        "std::vector<NormalizedSyncPath> staging_artifact_paths;",
    ],
    "cpp/anonsync_core/src/sync_domain.cpp": [
        "SyncStagingArtifactsProbe",
        "verify_committed_staging_artifacts_absent_or_throw",
        "staging_artifacts_verified",
        "require_staging_artifacts_cleaned",
        "sync session checkpoint resume staging cleanup probe rejects stale committed receipt directories",
        "sync session checkpoint resume staging cleanup probe exposes advisory stale receipt directory evidence",
    ],
    "docs/0070-rev0680-staging-cleanup-resume-probe.md": [
        "Rev0680 — staging cleanup resume probe",
        "require_staging_artifacts_cleaned",
        "staging_artifacts_verified",
        EXPECTED_SELFTEST,
        "Remaining ceiling",
    ],
    "docs/0001-cpp-core-gameplan.md": [
        "Current rev0680 product slice — staging cleanup resume probe",
        "staging_artifacts_verified",
        "staging_receipt_directories_present",
        EXPECTED_SELFTEST,
        EXPECTED_CTEST,
    ],
    "docs/0003-next-risk-register.md": [
        "Next risk register after rev0680",
        "Rev0680 priority note",
        "source/destination/staging-verified resume view",
        "pending-transfer reconstruction view",
    ],
    "bin/HISTORY.md": [
        "rev0680",
        "source, destination, and staging cleanup resume verification",
        "rev0679: historical source/audit only",
    ],
    "audit/rev0680-staging-cleanup-resume-probe-audit.json": [
        "staging-cleanup-resume-probe",
        "require_staging_artifacts_cleaned",
        "staging_artifacts_verified",
        "package_validator_summary",
    ],
    "audit/rev0680-staging-cleanup-resume-probe-source.patch": [
        "0070-rev0680-staging-cleanup-resume-probe.md",
        "require_staging_artifacts_cleaned",
        "staging_artifacts_verified",
        "validate_rev0680_staging_cleanup_resume_probe.py",
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
        raise AssertionError("missing required rev0680 files: " + ", ".join(missing))
    if (ROOT / OLD_ACTIVE_BINARY).exists():
        raise AssertionError("rev0680 package must not carry the rev0679 active binary")


def assert_phrases() -> None:
    for rel, phrases in REQUIRED_PHRASES.items():
        text = (ROOT / rel).read_text(errors="replace")
        for phrase in phrases:
            if phrase not in text:
                raise AssertionError(f"required phrase missing from {rel}: {phrase}")


def assert_logs() -> None:
    ctest = (ROOT / "audit/logs/rev0680-release-ctest.log").read_text(errors="replace")
    if EXPECTED_CTEST not in ctest:
        raise AssertionError("release ctest summary missing")
    selftest = (ROOT / "audit/logs/rev0680-staging-cleanup-resume-probe-selftest.log").read_text(errors="replace")
    if EXPECTED_SELFTEST not in selftest:
        raise AssertionError("sync-domain selftest summary missing")
    asan = (ROOT / "audit/logs/rev0680-narrow-asan-ubsan-sync-domain-selftest.log").read_text(errors="replace")
    if EXPECTED_SELFTEST not in asan:
        raise AssertionError("narrow asan/ubsan selftest summary missing")
    build = (ROOT / "audit/logs/rev0680-release-build.log").read_text(errors="replace")
    if "Built target anonsync_core" not in build:
        raise AssertionError("release build log missing built target line")
    asan_build = (ROOT / "audit/logs/rev0680-narrow-asan-ubsan-sync-domain-build.log").read_text(errors="replace")
    if "Built target anonsync_core" not in asan_build:
        raise AssertionError("narrow sanitizer build log missing built target line")
    validator_log = ROOT / VALIDATOR_LOG
    if validator_log.exists():
        validator_text = validator_log.read_text(errors="replace")
        if validator_text.strip() and EXPECTED_VALIDATOR not in validator_text:
            raise AssertionError("package validator log exists but is missing expected pass line")


def assert_audit() -> None:
    audit = json.loads(AUDIT.read_text())
    if audit.get("revision_id") != "rev0680" or audit.get("parent_revision") != "rev0679":
        raise AssertionError("audit revision lineage mismatch")
    if audit.get("product_mission") != "cxx-p2p-file-sync":
        raise AssertionError("audit product mission mismatch")
    if audit.get("codename") != "staging-cleanup-resume-probe":
        raise AssertionError("audit codename mismatch")
    if audit.get("active_binary") != ACTIVE_BINARY:
        raise AssertionError("audit active binary mismatch")
    if audit.get("active_binary_sha256") != sha_file(ROOT / ACTIVE_BINARY):
        raise AssertionError("audit active binary sha mismatch")
    if audit.get("cxx_behavior_changed") is not True:
        raise AssertionError("rev0680 must claim C++ behavior changed")
    checks = audit.get("resume_staging_checks", [])
    if not any("staging_root_path" in item for item in checks):
        raise AssertionError("audit staging checks must mention staging_root_path")
    if not any(".part.chunks" in item for item in checks):
        raise AssertionError("audit staging checks must mention .part.chunks artifacts")
    if audit.get("validation", {}).get("sync_domain_selftest") != EXPECTED_SELFTEST:
        raise AssertionError("audit selftest summary mismatch")
    if audit.get("validation", {}).get("release_ctest") != EXPECTED_CTEST:
        raise AssertionError("audit ctest summary mismatch")


def assert_binary_hash() -> None:
    sha_log = (ROOT / "audit/logs/rev0680-binary-sha256.txt").read_text().split()[0]
    if sha_file(ROOT / ACTIVE_BINARY) != sha_log:
        raise AssertionError("active binary sha256 mismatch")


def assert_manifest() -> None:
    manifest = json.loads(MANIFEST.read_text())
    if manifest.get("revision_id") != "rev0680" or manifest.get("parent_revision") != "rev0679":
        raise AssertionError("rev0680 manifest lineage mismatch")
    if manifest.get("manifest_kind") != "code-bearing-staging-cleanup-resume-probe":
        raise AssertionError("rev0680 manifest kind mismatch")
    if manifest.get("product_mission") != "cxx-p2p-file-sync":
        raise AssertionError("rev0680 product mission tag mismatch")
    if manifest.get("codename") != "staging-cleanup-resume-probe":
        raise AssertionError("rev0680 codename mismatch")
    if manifest.get("active_binary") != ACTIVE_BINARY:
        raise AssertionError("active binary should be rev0680")
    if manifest.get("capability_manifest") != CAPABILITY_MANIFEST:
        raise AssertionError("capability manifest should remain rev0648-bound until sync-ledger capabilities change")
    if set(manifest.get("excluded_mutable_evidence", [])) != EXCLUDED_MUTABLE:
        raise AssertionError("manifest excluded mutable evidence mismatch")

    expected_files = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT).as_posix()
        if rel in EXCLUDED_MUTABLE:
            continue
        expected_files.append({"path": rel, "sha256": sha_file(path), "size_bytes": path.stat().st_size})
    expected_files.sort(key=lambda item: item["path"])
    actual_files = sorted(manifest.get("files", []), key=lambda item: item.get("path", ""))
    if actual_files != expected_files:
        raise AssertionError("manifest file listing/hash set mismatch")


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
