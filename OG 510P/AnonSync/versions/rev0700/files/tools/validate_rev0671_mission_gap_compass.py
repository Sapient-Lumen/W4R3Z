#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_VALIDATOR = "rev0671 mission gap compass package validator passed"
EXPECTED_PREV_VALIDATOR = "rev0670 peer transfer round package validator passed"
EXPECTED_SELFTEST = "anonsync_core sync domain model selftest passed=191 failed=0"
ACTIVE_BINARY = "bin/rev0670/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
AUDIT = ROOT / "audit/rev0671-mission-gap-compass-audit.json"
MANIFEST = ROOT / "schema/rev0671/slim-cube-manifest.json"

REQUIRED_FILES = [
    "README.md",
    "docs/0001-cpp-core-gameplan.md",
    "docs/0003-next-risk-register.md",
    "docs/0061-rev0671-mission-gap-compass.md",
    "docs/0060-rev0670-peer-transfer-round.md",
    "cpp/anonsync_core/include/anonsync_core.hpp",
    "cpp/anonsync_core/src/sync_domain.cpp",
    ACTIVE_BINARY,
    "audit/rev0671-mission-gap-compass-audit.json",
    "audit/rev0671-mission-gap-compass-source.patch",
    "audit/logs/rev0671-rev0670-package-validator-rerun.log",
    "audit/logs/rev0671-active-sync-domain-selftest-rerun.log",
    "audit/logs/rev0671-mission-gap-compass-package-validator.log",
    "tools/validate_rev0671_mission_gap_compass.py",
    "schema/rev0671/slim-cube-manifest.json",
]

REQUIRED_PHRASES = {
    "README.md": [
        "AnonSync slim C++ working cube — rev0671",
        "C++ peer-to-peer file synchronization system",
        "Rev0671 is a deep mission/gap compass",
        "active executable remains `bin/rev0670/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3`",
        "Rev0670",
        "peer transfer-round continuation",
        "SyncPeerChunkTransferRoundResult",
        "accept_sync_peer_chunk_response_batch_and_plan_next",
        "sync-peer-chunk-schedule:v1",
        "deterministic fake peer-session harness",
        "not yet",
    ],
    "docs/0061-rev0671-mission-gap-compass.md": [
        "Rev0671 — mission gap compass",
        "makes no C++ source, binary, capability, fixture, or runtime behavior change",
        "folder convergence under evidence-bound local truth",
        "The missing piece is a **session loop**",
        "deterministic fake peer-session harness",
        "Rev0672 — deterministic fake peer-session harness",
        "Project-Name-rev####-YYYY.MM.DD.HH.MM-foobarnamesummaryhighlightcodename.zip",
        "Honest ceiling after rev0671",
    ],
    "docs/0001-cpp-core-gameplan.md": [
        "Current rev0670 product slice, held by rev0671 mission compass",
        "Rev0671 makes no C++ behavior change",
        "accept_sync_peer_chunk_response_batch_and_plan_next",
        "fake peer-session harness",
    ],
    "docs/0003-next-risk-register.md": [
        "Next risk register after rev0670",
        "sharpened by rev0671",
        "Rev0671 priority note",
        "fake peer-session convergence harness",
    ],
    "audit/rev0671-mission-gap-compass-audit.json": [
        "mission-gap-compass",
        "authorized peer-to-peer folder convergence under evidence-bound local truth",
        "fake-peer-session-harness",
        "new C++ runtime behavior",
    ],
    "audit/rev0671-mission-gap-compass-source.patch": [
        "0061-rev0671-mission-gap-compass.md",
        "mission gap compass",
        "validate_rev0671_mission_gap_compass.py",
    ],
}


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def assert_exists() -> None:
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).exists()]
    if missing:
        raise AssertionError("missing required rev0671 files: " + ", ".join(missing))
    if (ROOT / "bin/rev0671").exists():
        raise AssertionError("rev0671 is non-code-bearing and must not introduce a rev0671 active binary directory")


def assert_phrases() -> None:
    for rel, phrases in REQUIRED_PHRASES.items():
        text = (ROOT / rel).read_text(errors="replace")
        for phrase in phrases:
            if phrase not in text:
                raise AssertionError(f"required phrase missing from {rel}: {phrase}")


def assert_logs() -> None:
    prev = (ROOT / "audit/logs/rev0671-rev0670-package-validator-rerun.log").read_text(errors="replace")
    if EXPECTED_PREV_VALIDATOR not in prev:
        raise AssertionError("rev0670 validator rerun log missing expected pass line")
    selftest = (ROOT / "audit/logs/rev0671-active-sync-domain-selftest-rerun.log").read_text(errors="replace")
    if EXPECTED_SELFTEST not in selftest:
        raise AssertionError("active sync-domain selftest rerun log missing expected pass line")
    validator_log = ROOT / "audit/logs/rev0671-mission-gap-compass-package-validator.log"
    if validator_log.exists() and EXPECTED_VALIDATOR not in validator_log.read_text(errors="replace"):
        raise AssertionError("rev0671 validator log exists but is missing expected pass line")


def assert_audit() -> None:
    audit = json.loads(AUDIT.read_text())
    if audit.get("revision_id") != "rev0671" or audit.get("parent_revision") != "rev0670":
        raise AssertionError("audit revision lineage mismatch")
    if audit.get("codename") != "mission-gap-compass":
        raise AssertionError("audit codename mismatch")
    if audit.get("product_mission") != "cxx-p2p-file-sync":
        raise AssertionError("audit product mission mismatch")
    if audit.get("active_binary") != ACTIVE_BINARY:
        raise AssertionError("audit active binary mismatch")
    if audit.get("active_binary_sha256") != sha_file(ROOT / ACTIVE_BINARY):
        raise AssertionError("audit active binary sha mismatch")
    if audit.get("cxx_behavior_changed") is not False:
        raise AssertionError("rev0671 must be marked non-code-bearing")
    findings = audit.get("deep_read_findings", {})
    if findings.get("main_gap") != "no deterministic fake peer-session loop proves end-to-end convergence through existing C++ sync-domain boundaries":
        raise AssertionError("audit main gap mismatch")
    validation = audit.get("validation", {})
    if validation.get("rev0670_package_validator_rerun") != EXPECTED_PREV_VALIDATOR:
        raise AssertionError("audit prev validator summary mismatch")
    if validation.get("active_sync_domain_selftest_rerun") != EXPECTED_SELFTEST:
        raise AssertionError("audit selftest summary mismatch")
    if validation.get("package_validator_summary") != EXPECTED_VALIDATOR:
        raise AssertionError("audit package validator summary mismatch")


def assert_manifest() -> None:
    manifest = json.loads(MANIFEST.read_text())
    if manifest.get("revision_id") != "rev0671" or manifest.get("parent_revision") != "rev0670":
        raise AssertionError("manifest lineage mismatch")
    if manifest.get("codename") != "mission-gap-compass":
        raise AssertionError("manifest codename mismatch")
    if manifest.get("manifest_kind") != "mission-review-compass":
        raise AssertionError("manifest kind mismatch")
    if manifest.get("active_binary") != ACTIVE_BINARY:
        raise AssertionError("manifest active binary mismatch")
    excluded = set(manifest.get("excluded_mutable_evidence", []))
    if "schema/rev0671/slim-cube-manifest.json" not in excluded:
        raise AssertionError("manifest must exclude itself as mutable evidence")
    expected_files = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT).as_posix()
        if rel == "schema/rev0671/slim-cube-manifest.json":
            continue
        expected_files.append(rel)
    if manifest.get("file_count") != len(expected_files):
        raise AssertionError("manifest file_count mismatch")
    manifest_files = {item["path"]: item for item in manifest.get("files", [])}
    if set(manifest_files) != set(expected_files):
        missing = sorted(set(expected_files) - set(manifest_files))[:10]
        extra = sorted(set(manifest_files) - set(expected_files))[:10]
        raise AssertionError(f"manifest path set mismatch missing={missing} extra={extra}")
    for rel in expected_files:
        item = manifest_files[rel]
        path = ROOT / rel
        if item.get("sha256") != sha_file(path) or item.get("size_bytes") != path.stat().st_size:
            raise AssertionError(f"manifest digest/size mismatch for {rel}")


def main() -> None:
    assert_exists()
    assert_phrases()
    assert_logs()
    assert_audit()
    assert_manifest()
    print(EXPECTED_VALIDATOR)


if __name__ == "__main__":
    main()
