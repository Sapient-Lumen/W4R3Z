#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_VALIDATOR = "rev0690 resume claim split package validator passed"
EXPECTED_CTEST = "100% tests passed, 0 tests failed out of 27"
EXPECTED_SELFTEST = "anonsync_core sync domain model selftest passed=242 failed=0"
ACTIVE_BINARY = "bin/rev0690/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
OLD_ACTIVE_BINARY = "bin/rev0688/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
AUDIT = ROOT / "audit/rev0690-resume-claim-split-audit.json"
MANIFEST = ROOT / "schema/rev0690/slim-cube-manifest.json"
VALIDATOR_LOG = "audit/logs/rev0690-resume-claim-split-package-validator.log"
EXCLUDED_MUTABLE = {"schema/rev0690/slim-cube-manifest.json", VALIDATOR_LOG}

REQUIRED_FILES = [
    "README.md",
    "bin/HISTORY.md",
    "docs/0001-cpp-core-gameplan.md",
    "docs/0003-next-risk-register.md",
    "docs/0080-rev0690-resume-claim-split.md",
    "docs/0079-rev0689-mission-reclaim-compass.md",
    "docs/0078-rev0688-resume-workorder-lease.md",
    "cpp/anonsync_core/README.md",
    "cpp/anonsync_core/include/anonsync_core.hpp",
    "cpp/anonsync_core/src/sync_domain.cpp",
    ACTIVE_BINARY,
    "audit/rev0690-resume-claim-split-audit.json",
    "audit/rev0690-resume-claim-split-source.patch",
    "audit/logs/rev0690-release-configure.log",
    "audit/logs/rev0690-release-build-final.log",
    "audit/logs/rev0690-release-ctest.log",
    "audit/logs/rev0690-packaged-sync-domain-selftest.log",
    "audit/logs/rev0690-asan-ubsan-configure.log",
    "audit/logs/rev0690-asan-ubsan-build-final.log",
    "audit/logs/rev0690-asan-ubsan-sync-domain-selftest.log",
    "audit/logs/rev0690-binary-sha256.txt",
    "audit/logs/rev0690-binary-ldd.txt",
    VALIDATOR_LOG,
    "tools/validate_rev0690_resume_claim_split.py",
    "schema/rev0690/slim-cube-manifest.json",
]

REQUIRED_PHRASES = {
    "README.md": [
        "AnonSync slim C++ working cube — rev0690",
        "Rev0690 is **code-bearing**",
        "claim-only API",
        "INSERT OR REPLACE",
        "INSERT OR IGNORE",
        "folder convergence under evidence-bound local truth",
        "abandoned-lease semantics",
        EXPECTED_SELFTEST,
    ],
    "cpp/anonsync_core/README.md": [
        "anonsync_core rev0690",
        "claim-only resume-transfer workorder boundary",
        "INSERT OR IGNORE",
        "mismatched-worker claim steal rejection",
        EXPECTED_SELFTEST,
    ],
    "docs/0080-rev0690-resume-claim-split.md": [
        "Rev0690 — resume transfer claim split",
        "claim_sync_session_checkpoint_resume_transfer_workorders",
        "INSERT OR IGNORE",
        "fails closed if another worker or lease already owns the row",
        "worker `worker-echo` attempting to execute the live claimed rows",
        "Rev0691 — resume transfer lease expiry and reclaim policy",
        "Project-Name-rev####-YYYY.MM.DD.HH.MM-foobarnamesummaryhighlightcodename.zip",
    ],
    "docs/0001-cpp-core-gameplan.md": [
        "Current rev0690 code slice",
        "claimed-at timestamp",
        "Make durable worker rows reclaimable before adding production transport",
        "Do not confuse claimed work with completed work",
    ],
    "docs/0003-next-risk-register.md": [
        "Next risk register after rev0690",
        "No abandoned-lease semantics",
        "No reclaim transition",
        "Real peer response binding is missing",
        EXPECTED_SELFTEST,
    ],
    "cpp/anonsync_core/include/anonsync_core.hpp": [
        "SyncSessionCheckpointResumeTransferClaimOptions",
        "SyncSessionCheckpointResumeTransferFileClaimResult",
        "SyncSessionCheckpointResumeTransferClaimResult",
        "claim_sync_session_checkpoint_resume_transfer_workorders",
    ],
    "cpp/anonsync_core/src/sync_domain.cpp": [
        "claim_sync_session_checkpoint_resume_transfer_workorders",
        "INSERT OR IGNORE INTO sync_session_resume_transfer_workorders",
        "transfer workorder row is already claimed by another worker or lease",
        "sync session checkpoint resume transfer claim leaves claimed rows crash-visible without staged bytes or receipt sidecars",
        "sync session checkpoint resume transfer executor rejects another worker trying to steal a live claimed row",
    ],
    "audit/rev0690-resume-claim-split-audit.json": [
        "resume-claim-split",
        "claim-only resume transfer workorders",
        "INSERT OR REPLACE",
        "INSERT OR IGNORE",
        "abandoned-lease semantics",
    ],
    "audit/rev0690-resume-claim-split-source.patch": [
        "0080-rev0690-resume-claim-split.md",
        "SyncSessionCheckpointResumeTransferClaimOptions",
        "INSERT OR IGNORE INTO sync_session_resume_transfer_workorders",
        "validate_rev0690_resume_claim_split.py",
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
        raise AssertionError("missing required rev0690 files: " + ", ".join(missing))
    if (ROOT / OLD_ACTIVE_BINARY).exists():
        raise AssertionError("old rev0688 active binary must be omitted from the slim rev0690 package")
    if (ROOT / ACTIVE_BINARY).stat().st_mode & 0o111 == 0:
        raise AssertionError("active rev0690 binary must be executable")


def assert_phrases() -> None:
    for rel, phrases in REQUIRED_PHRASES.items():
        text = (ROOT / rel).read_text(errors="replace")
        for phrase in phrases:
            if phrase not in text:
                raise AssertionError(f"required phrase missing from {rel}: {phrase}")


def assert_logs() -> None:
    ctest = (ROOT / "audit/logs/rev0690-release-ctest.log").read_text(errors="replace")
    if EXPECTED_CTEST not in ctest:
        raise AssertionError("release ctest log missing expected pass line")
    packaged = (ROOT / "audit/logs/rev0690-packaged-sync-domain-selftest.log").read_text(errors="replace")
    if EXPECTED_SELFTEST not in packaged:
        raise AssertionError("packaged sync-domain selftest log missing expected pass line")
    asan = (ROOT / "audit/logs/rev0690-asan-ubsan-sync-domain-selftest.log").read_text(errors="replace")
    if EXPECTED_SELFTEST not in asan:
        raise AssertionError("asan/ubsan sync-domain selftest log missing expected pass line")
    build = (ROOT / "audit/logs/rev0690-release-build-final.log").read_text(errors="replace")
    if "Built target anonsync_core" not in build:
        raise AssertionError("release build final log missing built target line")
    validator_log = ROOT / VALIDATOR_LOG
    if validator_log.exists():
        text = validator_log.read_text(errors="replace")
        if text.strip() and EXPECTED_VALIDATOR not in text:
            raise AssertionError("rev0690 validator log exists but is missing expected pass line")


def assert_audit() -> None:
    audit = json.loads(AUDIT.read_text())
    if audit.get("revision_id") != "rev0690" or audit.get("parent_revision") != "rev0689":
        raise AssertionError("audit revision lineage mismatch")
    if audit.get("codename") != "resume-claim-split":
        raise AssertionError("audit codename mismatch")
    if audit.get("manifest_kind") != "code-bearing-resume-claim-split":
        raise AssertionError("audit manifest kind mismatch")
    if audit.get("product_mission") != "cxx-p2p-file-sync":
        raise AssertionError("audit product mission mismatch")
    if audit.get("cxx_behavior_changed") is not True:
        raise AssertionError("rev0690 must be marked code-bearing")
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
    sha_log = (ROOT / "audit/logs/rev0690-binary-sha256.txt").read_text().split()[0]
    if sha_file(ROOT / ACTIVE_BINARY) != sha_log:
        raise AssertionError("active binary sha256 mismatch")


def assert_manifest() -> None:
    manifest = json.loads(MANIFEST.read_text())
    if manifest.get("revision_id") != "rev0690" or manifest.get("parent_revision") != "rev0689":
        raise AssertionError("manifest lineage mismatch")
    if manifest.get("codename") != "resume-claim-split":
        raise AssertionError("manifest codename mismatch")
    if manifest.get("manifest_kind") != "code-bearing-resume-claim-split":
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
    expected_files = [rel for rel in rel_files() if rel not in EXCLUDED_MUTABLE]
    if manifest.get("file_count") != len(expected_files):
        raise AssertionError("manifest file_count mismatch")
    files = {item["path"]: item for item in manifest.get("files", [])}
    if set(files) != set(expected_files):
        missing = sorted(set(expected_files) - set(files))[:10]
        extra = sorted(set(files) - set(expected_files))[:10]
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
