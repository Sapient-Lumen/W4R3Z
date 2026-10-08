#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_VALIDATOR = "rev0691 resume lease reclaim package validator passed"
EXPECTED_CTEST = "100% tests passed, 0 tests failed out of 27"
EXPECTED_SELFTEST = "anonsync_core sync domain model selftest passed=245 failed=0"
ACTIVE_BINARY = "bin/rev0691/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
OLD_ACTIVE_BINARY = "bin/rev0690/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
AUDIT = ROOT / "audit/rev0691-resume-lease-reclaim-audit.json"
MANIFEST = ROOT / "schema/rev0691/slim-cube-manifest.json"
VALIDATOR_LOG = "audit/logs/rev0691-resume-lease-reclaim-package-validator.log"
EXCLUDED_MUTABLE = {"schema/rev0691/slim-cube-manifest.json", VALIDATOR_LOG}

REQUIRED_FILES = [
    "README.md",
    "bin/HISTORY.md",
    "docs/0001-cpp-core-gameplan.md",
    "docs/0003-next-risk-register.md",
    "docs/0081-rev0691-resume-lease-reclaim.md",
    "docs/0080-rev0690-resume-claim-split.md",
    "docs/0079-rev0689-mission-reclaim-compass.md",
    "docs/0078-rev0688-resume-workorder-lease.md",
    "cpp/anonsync_core/README.md",
    "cpp/anonsync_core/include/anonsync_core.hpp",
    "cpp/anonsync_core/src/sync_domain.cpp",
    ACTIVE_BINARY,
    "audit/rev0691-resume-lease-reclaim-audit.json",
    "audit/rev0691-resume-lease-reclaim-source.patch",
    "audit/logs/rev0691-release-configure.log",
    "audit/logs/rev0691-release-build-final.log",
    "audit/logs/rev0691-release-ctest.log",
    "audit/logs/rev0691-packaged-sync-domain-selftest.log",
    "audit/logs/rev0691-asan-ubsan-configure.log",
    "audit/logs/rev0691-asan-ubsan-build-final.log",
    "audit/logs/rev0691-asan-ubsan-sync-domain-selftest.log",
    "audit/logs/rev0691-binary-sha256.txt",
    "audit/logs/rev0691-binary-ldd.txt",
    VALIDATOR_LOG,
    "tools/validate_rev0691_resume_lease_reclaim.py",
    "schema/rev0691/slim-cube-manifest.json",
]

REQUIRED_PHRASES = {
    "README.md": [
        "AnonSync slim C++ working cube — rev0691",
        "Rev0691 is **code-bearing**",
        "lease_expires_at_epoch",
        "claim_attempts",
        "expired transfer claims reclaimable",
        "folder convergence under evidence-bound local truth",
        "lease-field bleed into the materialization result surface was removed",
        EXPECTED_SELFTEST,
    ],
    "bin/HISTORY.md": [
        "rev0691",
        ACTIVE_BINARY,
        "lease-timed resume transfer claims",
        "expired workorder reclaim",
    ],
    "cpp/anonsync_core/README.md": [
        "anonsync_core rev0691",
        "lease-timed resume-transfer workorders",
        "expired-claim reclaim",
        "materialization result surface",
        EXPECTED_SELFTEST,
    ],
    "docs/0081-rev0691-resume-lease-reclaim.md": [
        "Rev0691 — resume transfer lease reclaim",
        "claimed_at_epoch",
        "lease_expires_at_epoch",
        "claim_attempts",
        "worker `worker-echo`",
        "worker `worker-delta`",
        "SyncSessionCheckpointMaterializeResumeResult",
        "Rev0692 should add previous-owner transition evidence",
        "Project-Name-rev####-YYYY.MM.DD.HH.MM-foobarnamesummaryhighlightcodename.zip",
    ],
    "docs/0001-cpp-core-gameplan.md": [
        "Current rev0691 code slice",
        "expired-claim reclaim",
        "previous-owner history",
        "Turn reclaim into a policy before adding production transport",
        EXPECTED_SELFTEST,
    ],
    "docs/0003-next-risk-register.md": [
        "Next risk register after rev0691",
        "No previous-owner history",
        "No abandon/quarantine transition",
        "Real peer response binding is missing",
        EXPECTED_SELFTEST,
    ],
    "cpp/anonsync_core/include/anonsync_core.hpp": [
        "SyncSessionCheckpointResumeTransferClaimOptions",
        "std::uint64_t workorder_claim_now_epoch = 1;",
        "std::uint64_t worker_lease_seconds = 60;",
        "bool allow_expired_workorder_reclaim = true;",
        "std::uint64_t workorder_rows_reclaimed = 0;",
    ],
    "cpp/anonsync_core/src/sync_domain.cpp": [
        "claimed_at_epoch INTEGER NOT NULL CHECK(claimed_at_epoch > 0)",
        "lease_expires_at_epoch INTEGER NOT NULL CHECK(lease_expires_at_epoch > claimed_at_epoch)",
        "claim_attempts INTEGER NOT NULL CHECK(claim_attempts > 0)",
        "INSERT OR IGNORE INTO sync_session_resume_transfer_workorders",
        "claim_attempts=claim_attempts+1",
        "transfer workorder row is already claimed by another worker or lease",
        "sync session checkpoint resume transfer executor rejects another worker trying to steal a live claimed row before lease expiry",
        "sync session checkpoint resume transfer claim reclaims expired rows for a new worker lease without executing bytes",
        "sync session checkpoint resume transfer executor rejects the stale worker after an expired claim is reclaimed",
    ],
    "audit/rev0691-resume-lease-reclaim-audit.json": [
        "resume-lease-reclaim",
        "deterministic claimed_at_epoch",
        "lease-field bleed",
        "previous-owner history",
    ],
    "audit/rev0691-resume-lease-reclaim-source.patch": [
        "0081-rev0691-resume-lease-reclaim.md",
        "claimed_at_epoch INTEGER NOT NULL CHECK",
        "claim_attempts=claim_attempts+1",
        "validate_rev0691_resume_lease_reclaim.py",
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
        if rel.startswith("build_rev"):
            continue
        yield rel


def assert_exists() -> None:
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).exists()]
    if missing:
        raise AssertionError("missing required rev0691 files: " + ", ".join(missing))
    if (ROOT / OLD_ACTIVE_BINARY).exists():
        raise AssertionError("old rev0690 active binary must be omitted from the slim rev0691 package")
    if (ROOT / ACTIVE_BINARY).stat().st_mode & 0o111 == 0:
        raise AssertionError("active rev0691 binary must be executable")
    materialize_slice = (ROOT / "cpp/anonsync_core/include/anonsync_core.hpp").read_text(errors="replace").split("struct SyncSessionCheckpointMaterializeResumeResult", 1)[1].split("struct SyncSessionCheckpointCleanupResumeOptions", 1)[0]
    for forbidden in ["workorder_claim_now_epoch", "worker_lease_seconds", "lease_expires_at_epoch"]:
        if forbidden in materialize_slice:
            raise AssertionError("lease field leaked into materialization result surface: " + forbidden)


def assert_phrases() -> None:
    for rel, phrases in REQUIRED_PHRASES.items():
        text = (ROOT / rel).read_text(errors="replace")
        for phrase in phrases:
            if phrase not in text:
                raise AssertionError(f"required phrase missing from {rel}: {phrase}")


def assert_logs() -> None:
    ctest = (ROOT / "audit/logs/rev0691-release-ctest.log").read_text(errors="replace")
    if EXPECTED_CTEST not in ctest:
        raise AssertionError("release ctest log missing expected pass line")
    packaged = (ROOT / "audit/logs/rev0691-packaged-sync-domain-selftest.log").read_text(errors="replace")
    if EXPECTED_SELFTEST not in packaged:
        raise AssertionError("packaged sync-domain selftest log missing expected pass line")
    asan = (ROOT / "audit/logs/rev0691-asan-ubsan-sync-domain-selftest.log").read_text(errors="replace")
    if EXPECTED_SELFTEST not in asan:
        raise AssertionError("asan/ubsan sync-domain selftest log missing expected pass line")
    build = (ROOT / "audit/logs/rev0691-release-build-final.log").read_text(errors="replace")
    if "Built target anonsync_core" not in build:
        raise AssertionError("release build final log missing built target line")
    validator_log = ROOT / VALIDATOR_LOG
    if validator_log.exists():
        text = validator_log.read_text(errors="replace")
        if text.strip() and EXPECTED_VALIDATOR not in text:
            raise AssertionError("rev0691 validator log exists but is missing expected pass line")


def assert_audit() -> None:
    audit = json.loads(AUDIT.read_text())
    if audit.get("revision_id") != "rev0691" or audit.get("parent_revision") != "rev0690":
        raise AssertionError("audit revision lineage mismatch")
    if audit.get("codename") != "resume-lease-reclaim":
        raise AssertionError("audit codename mismatch")
    if audit.get("manifest_kind") != "code-bearing-resume-lease-reclaim":
        raise AssertionError("audit manifest kind mismatch")
    if audit.get("product_mission") != "cxx-p2p-file-sync":
        raise AssertionError("audit product mission mismatch")
    if audit.get("cxx_behavior_changed") is not True:
        raise AssertionError("rev0691 must be marked code-bearing")
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


def assert_binary_hash() -> None:
    sha_log = (ROOT / "audit/logs/rev0691-binary-sha256.txt").read_text().split()[0]
    if sha_file(ROOT / ACTIVE_BINARY) != sha_log:
        raise AssertionError("active binary sha256 mismatch")


def assert_manifest() -> None:
    manifest = json.loads(MANIFEST.read_text())
    if manifest.get("revision_id") != "rev0691" or manifest.get("parent_revision") != "rev0690":
        raise AssertionError("manifest lineage mismatch")
    if manifest.get("codename") != "resume-lease-reclaim":
        raise AssertionError("manifest codename mismatch")
    if manifest.get("manifest_kind") != "code-bearing-resume-lease-reclaim":
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
    if validation.get("release_ctest") != EXPECTED_CTEST:
        raise AssertionError("manifest ctest mismatch")
    if validation.get("asan_ubsan_sync_domain_selftest") != EXPECTED_SELFTEST:
        raise AssertionError("manifest asan/ubsan selftest mismatch")
    if validation.get("package_validator_summary") != EXPECTED_VALIDATOR:
        raise AssertionError("manifest validator summary mismatch")
    expected_files = [rel for rel in rel_files() if rel not in EXCLUDED_MUTABLE]
    if manifest.get("file_count") != len(expected_files):
        raise AssertionError("manifest file_count mismatch")
    files = {item["path"]: item for item in manifest.get("files", [])}
    if set(files) != set(expected_files):
        missing = sorted(set(expected_files) - set(files))[:20]
        extra = sorted(set(files) - set(expected_files))[:20]
        raise AssertionError(f"manifest path set mismatch missing={missing} extra={extra}")
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
