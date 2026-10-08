#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_VALIDATOR = "rev0675 sync session resume view package validator passed"
EXPECTED_CTEST = "100% tests passed, 0 tests failed out of 27"
EXPECTED_SELFTEST = "anonsync_core sync domain model selftest passed=202 failed=0"
ACTIVE_BINARY = "bin/rev0675/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
OLD_ACTIVE_BINARY = "bin/rev0674/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
CAPABILITY_MANIFEST = "gateway/rev0648-cpp-ledger-backend-capabilities.json"
AUDIT = ROOT / "audit/rev0675-sync-session-resume-view-audit.json"
MANIFEST = ROOT / "schema/rev0675/slim-cube-manifest.json"
VALIDATOR_LOG = "audit/logs/rev0675-sync-session-resume-view-package-validator.log"
EXCLUDED_MUTABLE = {"schema/rev0675/slim-cube-manifest.json", VALIDATOR_LOG}

REQUIRED_CURRENT_FILES = [
    "README.md",
    "cpp/anonsync_core/README.md",
    "cpp/anonsync_core/include/anonsync_core.hpp",
    "cpp/anonsync_core/src/sync_domain.cpp",
    ACTIVE_BINARY,
    "bin/HISTORY.md",
    "docs/0001-cpp-core-gameplan.md",
    "docs/0003-next-risk-register.md",
    "docs/0065-rev0675-sync-session-resume-view.md",
    "audit/rev0675-sync-session-resume-view-audit.json",
    "audit/rev0675-sync-session-resume-view-source.patch",
    "audit/logs/rev0675-release-o0-configure.log",
    "audit/logs/rev0675-release-o0-build.log",
    "audit/logs/rev0675-release-o0-ctest.log",
    "audit/logs/rev0675-sync-session-resume-view-selftest.log",
    "audit/logs/rev0675-narrow-asan-ubsan-sync-domain-configure.log",
    "audit/logs/rev0675-narrow-asan-ubsan-sync-domain-build.log",
    "audit/logs/rev0675-narrow-asan-ubsan-sync-domain-selftest.log",
    "audit/logs/rev0675-binary-sha256.txt",
    "audit/logs/rev0675-binary-ldd.txt",
    "tools/validate_rev0675_sync_session_resume_view.py",
    "schema/rev0675/slim-cube-manifest.json",
]

REQUIRED_PHRASES = {
    "README.md": [
        "AnonSync slim C++ working cube — rev0675",
        "sync session checkpoint resume view",
        "load_sync_session_checkpoint_resume_view",
        "SyncSessionCheckpointResumeViewOptions",
        "SyncSessionCheckpointResumeViewResult",
        EXPECTED_SELFTEST,
        "does not replay them into resumed work",
    ],
    "cpp/anonsync_core/README.md": [
        "anonsync_core rev0675",
        "SyncSessionCheckpointResumeViewOptions",
        "SyncSessionCheckpointResumeViewResult",
        "load_sync_session_checkpoint_resume_view",
        "committed-cleaned",
        "restart input, not restart execution",
    ],
    "cpp/anonsync_core/include/anonsync_core.hpp": [
        "struct SyncSessionCheckpointResumeViewOptions",
        "struct SyncSessionCheckpointResumeViewResult",
        "bool terminal_session_complete = false;",
        "std::uint64_t chunk_receipts_pending_cleanup = 0;",
        "load_sync_session_checkpoint_resume_view",
    ],
    "cpp/anonsync_core/src/sync_domain.cpp": [
        "ensure_sync_session_checkpoint_schema_or_throw",
        "sqlite_count_for_session_or_throw",
        "load_sync_session_checkpoint_resume_view",
        "sync session checkpoint resume view reloads terminal completion evidence as restart input",
        "sync session checkpoint resume view rejects mismatched destination device identity",
        "sync session checkpoint resume view rejects database paths inside synchronized roots before opening sqlite",
    ],
    "docs/0065-rev0675-sync-session-resume-view.md": [
        "Rev0675 — sync session checkpoint resume view",
        "load_sync_session_checkpoint_resume_view",
        "Audit/refactor performed",
        EXPECTED_SELFTEST,
        "Remaining ceiling",
    ],
    "docs/0001-cpp-core-gameplan.md": [
        "Current rev0675 product slice — sync session checkpoint resume view",
        "load_sync_session_checkpoint_resume_view",
        "checkpoint resume-view loading",
        EXPECTED_SELFTEST,
        EXPECTED_CTEST,
    ],
    "docs/0003-next-risk-register.md": [
        "Next risk register after rev0675",
        "Rev0675 priority note",
        "completed checkpoint rows can be read as typed restart input",
        "actionable recovery",
    ],
    "bin/HISTORY.md": [
        "rev0675",
        "sync session checkpoint resume-view loading",
        "rev0674: historical source/audit only",
    ],
    "audit/rev0675-sync-session-resume-view-audit.json": [
        "sync-session-resume-view",
        "load_sync_session_checkpoint_resume_view",
        "Resume-view rows are not yet replayed into resumed filesystem or transfer work",
        "package_validator_summary",
    ],
    "audit/rev0675-sync-session-resume-view-source.patch": [
        "0065-rev0675-sync-session-resume-view.md",
        "SyncSessionCheckpointResumeViewOptions",
        "load_sync_session_checkpoint_resume_view",
        "validate_rev0675_sync_session_resume_view.py",
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
        raise AssertionError("missing required rev0675 files: " + ", ".join(missing))
    if (ROOT / OLD_ACTIVE_BINARY).exists():
        raise AssertionError("rev0675 package must not carry the rev0674 active binary")


def assert_phrases() -> None:
    for rel, phrases in REQUIRED_PHRASES.items():
        text = (ROOT / rel).read_text(errors="replace")
        for phrase in phrases:
            if phrase not in text:
                raise AssertionError(f"required phrase missing from {rel}: {phrase}")


def assert_logs() -> None:
    ctest = (ROOT / "audit/logs/rev0675-release-o0-ctest.log").read_text(errors="replace")
    if EXPECTED_CTEST not in ctest:
        raise AssertionError("release ctest summary missing")
    selftest = (ROOT / "audit/logs/rev0675-sync-session-resume-view-selftest.log").read_text(errors="replace")
    if EXPECTED_SELFTEST not in selftest:
        raise AssertionError("sync-domain selftest summary missing")
    asan = (ROOT / "audit/logs/rev0675-narrow-asan-ubsan-sync-domain-selftest.log").read_text(errors="replace")
    if EXPECTED_SELFTEST not in asan:
        raise AssertionError("narrow asan/ubsan selftest summary missing")
    build = (ROOT / "audit/logs/rev0675-release-o0-build.log").read_text(errors="replace")
    if "Built target anonsync_core" not in build:
        raise AssertionError("release build log missing built target line")
    validator_log = ROOT / VALIDATOR_LOG
    if validator_log.exists() and EXPECTED_VALIDATOR not in validator_log.read_text(errors="replace"):
        raise AssertionError("package validator log exists but is missing expected pass line")


def assert_audit() -> None:
    audit = json.loads(AUDIT.read_text())
    if audit.get("revision_id") != "rev0675" or audit.get("parent_revision") != "rev0674":
        raise AssertionError("audit revision lineage mismatch")
    if audit.get("product_mission") != "cxx-p2p-file-sync":
        raise AssertionError("audit product mission mismatch")
    if audit.get("codename") != "sync-session-resume-view":
        raise AssertionError("audit codename mismatch")
    if audit.get("active_binary") != ACTIVE_BINARY:
        raise AssertionError("audit active binary mismatch")
    if audit.get("active_binary_sha256") != sha_file(ROOT / ACTIVE_BINARY):
        raise AssertionError("audit active binary sha mismatch")
    if audit.get("cxx_behavior_changed") is not True:
        raise AssertionError("rev0675 must claim C++ behavior changed")
    if audit.get("validation", {}).get("sync_domain_selftest") != EXPECTED_SELFTEST:
        raise AssertionError("audit selftest summary mismatch")
    if audit.get("validation", {}).get("release_o0_ctest") != EXPECTED_CTEST:
        raise AssertionError("audit ctest summary mismatch")


def assert_binary_hash() -> None:
    sha_log = (ROOT / "audit/logs/rev0675-binary-sha256.txt").read_text().split()[0]
    if sha_file(ROOT / ACTIVE_BINARY) != sha_log:
        raise AssertionError("active binary sha256 mismatch")


def assert_manifest() -> None:
    manifest = json.loads(MANIFEST.read_text())
    if manifest.get("revision_id") != "rev0675" or manifest.get("parent_revision") != "rev0674":
        raise AssertionError("rev0675 manifest lineage mismatch")
    if manifest.get("manifest_kind") != "code-bearing-sync-session-resume-view":
        raise AssertionError("rev0675 manifest kind mismatch")
    if manifest.get("product_mission") != "cxx-p2p-file-sync":
        raise AssertionError("rev0675 product mission tag mismatch")
    if manifest.get("codename") != "sync-session-resume-view":
        raise AssertionError("rev0675 codename mismatch")
    if manifest.get("active_binary") != ACTIVE_BINARY:
        raise AssertionError("active binary should be rev0675")
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
        missing = sorted(set(expected_files) - set(files))[:12]
        extra = sorted(set(files) - set(expected_files))[:12]
        raise AssertionError(f"manifest path set mismatch missing={missing} extra={extra}")
    if OLD_ACTIVE_BINARY in files:
        raise AssertionError("manifest must not include old rev0674 active binary")
    for rel in expected_files:
        row = files[rel]
        path = ROOT / rel
        if row.get("size_bytes") != path.stat().st_size:
            raise AssertionError(f"manifest size mismatch for {rel}")
        if row.get("sha256") != sha_file(path):
            raise AssertionError(f"manifest sha mismatch for {rel}")


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
