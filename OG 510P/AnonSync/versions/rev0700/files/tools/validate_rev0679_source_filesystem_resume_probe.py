#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_VALIDATOR = "rev0679 source filesystem resume probe package validator passed"
EXPECTED_CTEST = "100% tests passed, 0 tests failed out of 27"
EXPECTED_SELFTEST = "anonsync_core sync domain model selftest passed=209 failed=0"
ACTIVE_BINARY = "bin/rev0679/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
OLD_ACTIVE_BINARY = "bin/rev0678/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
CAPABILITY_MANIFEST = "gateway/rev0648-cpp-ledger-backend-capabilities.json"
AUDIT = ROOT / "audit/rev0679-source-filesystem-resume-probe-audit.json"
MANIFEST = ROOT / "schema/rev0679/slim-cube-manifest.json"
VALIDATOR_LOG = "audit/logs/rev0679-source-filesystem-resume-probe-package-validator.log"
EXCLUDED_MUTABLE = {"schema/rev0679/slim-cube-manifest.json", VALIDATOR_LOG}

REQUIRED_CURRENT_FILES = [
    "README.md",
    "cpp/anonsync_core/README.md",
    "cpp/anonsync_core/include/anonsync_core.hpp",
    "cpp/anonsync_core/src/sync_domain.cpp",
    ACTIVE_BINARY,
    "bin/HISTORY.md",
    "docs/0001-cpp-core-gameplan.md",
    "docs/0003-next-risk-register.md",
    "docs/0069-rev0679-source-filesystem-resume-probe.md",
    "audit/rev0679-source-filesystem-resume-probe-audit.json",
    "audit/rev0679-source-filesystem-resume-probe-source.patch",
    "audit/logs/rev0679-release-configure.log",
    "audit/logs/rev0679-release-build.log",
    "audit/logs/rev0679-release-ctest.log",
    "audit/logs/rev0679-source-filesystem-resume-probe-selftest.log",
    "audit/logs/rev0679-narrow-asan-ubsan-sync-domain-configure.log",
    "audit/logs/rev0679-narrow-asan-ubsan-sync-domain-build.log",
    "audit/logs/rev0679-narrow-asan-ubsan-sync-domain-selftest.log",
    "audit/logs/rev0679-binary-sha256.txt",
    "audit/logs/rev0679-binary-ldd.txt",
    "tools/validate_rev0679_source_filesystem_resume_probe.py",
    "schema/rev0679/slim-cube-manifest.json",
]

REQUIRED_PHRASES = {
    "README.md": [
        "AnonSync slim C++ working cube — rev0679",
        "source filesystem resume probe",
        "require_source_filesystem_match",
        "source_filesystem_verified",
        EXPECTED_SELFTEST,
        "does not replay checkpoint rows into resumed work",
    ],
    "cpp/anonsync_core/README.md": [
        "anonsync_core rev0679",
        "source filesystem resume probe",
        "require_source_filesystem_match",
        "source_filesystem_drift_paths",
        "docs/session-report.txt",
    ],
    "cpp/anonsync_core/include/anonsync_core.hpp": [
        "bool require_source_filesystem_match = true;",
        "bool source_filesystem_verified = false;",
        "std::uint64_t source_filesystem_entries_checked = 0;",
        "std::uint64_t source_filesystem_content_mismatches = 0;",
        "std::vector<NormalizedSyncPath> source_filesystem_drift_paths;",
    ],
    "cpp/anonsync_core/src/sync_domain.cpp": [
        "SyncManifestFilesystemProbe",
        "verify_manifest_filesystem_or_throw",
        "source_filesystem_verified",
        "require_source_filesystem_match",
        "sync session checkpoint resume source filesystem probe rejects source content drift after durable terminal checkpoint",
        "sync session checkpoint resume source filesystem probe exposes advisory drift evidence when strict source matching is disabled",
    ],
    "docs/0069-rev0679-source-filesystem-resume-probe.md": [
        "Rev0679 — source filesystem resume probe",
        "require_source_filesystem_match",
        "source_filesystem_verified",
        EXPECTED_SELFTEST,
        "Remaining ceiling",
    ],
    "docs/0001-cpp-core-gameplan.md": [
        "Current rev0679 product slice — source filesystem resume probe",
        "source_filesystem_verified",
        "source_filesystem_content_mismatches",
        EXPECTED_SELFTEST,
        EXPECTED_CTEST,
    ],
    "docs/0003-next-risk-register.md": [
        "Next risk register after rev0679",
        "Rev0679 priority note",
        "source/destination-filesystem-verified resume view",
        "actionable restart",
    ],
    "bin/HISTORY.md": [
        "rev0679",
        "source and destination filesystem resume verification",
        "rev0678: historical source/audit only",
    ],
    "audit/rev0679-source-filesystem-resume-probe-audit.json": [
        "source-filesystem-resume-probe",
        "require_source_filesystem_match",
        "source_filesystem_verified",
        "package_validator_summary",
    ],
    "audit/rev0679-source-filesystem-resume-probe-source.patch": [
        "0069-rev0679-source-filesystem-resume-probe.md",
        "require_source_filesystem_match",
        "source_filesystem_verified",
        "validate_rev0679_source_filesystem_resume_probe.py",
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
        raise AssertionError("missing required rev0679 files: " + ", ".join(missing))
    if (ROOT / OLD_ACTIVE_BINARY).exists():
        raise AssertionError("rev0679 package must not carry the rev0678 active binary")


def assert_phrases() -> None:
    for rel, phrases in REQUIRED_PHRASES.items():
        text = (ROOT / rel).read_text(errors="replace")
        for phrase in phrases:
            if phrase not in text:
                raise AssertionError(f"required phrase missing from {rel}: {phrase}")


def assert_logs() -> None:
    ctest = (ROOT / "audit/logs/rev0679-release-ctest.log").read_text(errors="replace")
    if EXPECTED_CTEST not in ctest:
        raise AssertionError("release ctest summary missing")
    selftest = (ROOT / "audit/logs/rev0679-source-filesystem-resume-probe-selftest.log").read_text(errors="replace")
    if EXPECTED_SELFTEST not in selftest:
        raise AssertionError("sync-domain selftest summary missing")
    asan = (ROOT / "audit/logs/rev0679-narrow-asan-ubsan-sync-domain-selftest.log").read_text(errors="replace")
    if EXPECTED_SELFTEST not in asan:
        raise AssertionError("narrow asan/ubsan selftest summary missing")
    build = (ROOT / "audit/logs/rev0679-release-build.log").read_text(errors="replace")
    if "Built target anonsync_core" not in build:
        raise AssertionError("release build log missing built target line")
    validator_log = ROOT / VALIDATOR_LOG
    if validator_log.exists():
        validator_text = validator_log.read_text(errors="replace")
        if validator_text.strip() and EXPECTED_VALIDATOR not in validator_text:
            raise AssertionError("package validator log exists but is missing expected pass line")


def assert_audit() -> None:
    audit = json.loads(AUDIT.read_text())
    if audit.get("revision_id") != "rev0679" or audit.get("parent_revision") != "rev0678":
        raise AssertionError("audit revision lineage mismatch")
    if audit.get("product_mission") != "cxx-p2p-file-sync":
        raise AssertionError("audit product mission mismatch")
    if audit.get("codename") != "source-filesystem-resume-probe":
        raise AssertionError("audit codename mismatch")
    if audit.get("active_binary") != ACTIVE_BINARY:
        raise AssertionError("audit active binary mismatch")
    if audit.get("active_binary_sha256") != sha_file(ROOT / ACTIVE_BINARY):
        raise AssertionError("audit active binary sha mismatch")
    if audit.get("cxx_behavior_changed") is not True:
        raise AssertionError("rev0679 must claim C++ behavior changed")
    checks = audit.get("resume_filesystem_checks", [])
    if not any("source" in item and "source_root_path" in item for item in checks):
        raise AssertionError("audit resume filesystem checks must mention source rows under source_root_path")
    if not any("destination_after" in item and "destination_root_path" in item for item in checks):
        raise AssertionError("audit resume filesystem checks must mention destination_after rows under destination_root_path")
    if audit.get("validation", {}).get("sync_domain_selftest") != EXPECTED_SELFTEST:
        raise AssertionError("audit selftest summary mismatch")
    if audit.get("validation", {}).get("release_ctest") != EXPECTED_CTEST:
        raise AssertionError("audit ctest summary mismatch")


def assert_binary_hash() -> None:
    sha_log = (ROOT / "audit/logs/rev0679-binary-sha256.txt").read_text().split()[0]
    if sha_file(ROOT / ACTIVE_BINARY) != sha_log:
        raise AssertionError("active binary sha256 mismatch")


def assert_manifest() -> None:
    manifest = json.loads(MANIFEST.read_text())
    if manifest.get("revision_id") != "rev0679" or manifest.get("parent_revision") != "rev0678":
        raise AssertionError("rev0679 manifest lineage mismatch")
    if manifest.get("manifest_kind") != "code-bearing-source-filesystem-resume-probe":
        raise AssertionError("rev0679 manifest kind mismatch")
    if manifest.get("product_mission") != "cxx-p2p-file-sync":
        raise AssertionError("rev0679 product mission tag mismatch")
    if manifest.get("codename") != "source-filesystem-resume-probe":
        raise AssertionError("rev0679 codename mismatch")
    if manifest.get("active_binary") != ACTIVE_BINARY:
        raise AssertionError("active binary should be rev0679")
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
        expected_files.append(rel)
    expected_files.sort()

    rows = manifest.get("files", [])
    files = {item.get("path"): item for item in rows}
    if manifest.get("file_count") != len(expected_files) or len(rows) != len(expected_files):
        raise AssertionError("manifest file_count mismatch")
    if set(files) != set(expected_files):
        missing = sorted(set(expected_files) - set(files))
        extra = sorted(set(files) - set(expected_files))
        raise AssertionError(f"manifest file set mismatch missing={missing[:5]} extra={extra[:5]}")
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
    assert_binary_hash()
    assert_manifest()
    print(EXPECTED_VALIDATOR)


if __name__ == "__main__":
    main()
