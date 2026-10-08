#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_VALIDATOR = "rev0689 mission reclaim compass package validator passed"
EXPECTED_PREV_VALIDATOR = "rev0688 resume workorder lease package validator passed"
EXPECTED_SELFTEST = "anonsync_core sync domain model selftest passed=238 failed=0"
ACTIVE_BINARY = "bin/rev0688/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
AUDIT = ROOT / "audit/rev0689-mission-reclaim-compass-audit.json"
MANIFEST = ROOT / "schema/rev0689/slim-cube-manifest.json"
VALIDATOR_LOG = "audit/logs/rev0689-mission-reclaim-compass-package-validator.log"
EXCLUDED_MUTABLE = {"schema/rev0689/slim-cube-manifest.json", VALIDATOR_LOG}

REQUIRED_FILES = [
    "README.md",
    "docs/0001-cpp-core-gameplan.md",
    "docs/0003-next-risk-register.md",
    "docs/0079-rev0689-mission-reclaim-compass.md",
    "docs/0078-rev0688-resume-workorder-lease.md",
    "cpp/anonsync_core/include/anonsync_core.hpp",
    "cpp/anonsync_core/src/sync_domain.cpp",
    ACTIVE_BINARY,
    "audit/rev0689-mission-reclaim-compass-audit.json",
    "audit/rev0689-mission-reclaim-compass-source.patch",
    "audit/logs/rev0689-rev0688-package-validator-rerun.log",
    "audit/logs/rev0689-active-sync-domain-selftest-rerun.log",
    VALIDATOR_LOG,
    "tools/validate_rev0689_mission_reclaim_compass.py",
    "schema/rev0689/slim-cube-manifest.json",
]

REQUIRED_PHRASES = {
    "README.md": [
        "AnonSync slim C++ working cube — rev0689",
        "Rev0689 is **non-code-bearing**",
        "folder convergence under evidence-bound local truth",
        "no invisible work, no caller-authored truth, no silent convergence",
        "crash-surviving worker boundary",
        EXPECTED_SELFTEST,
    ],
    "docs/0079-rev0689-mission-reclaim-compass.md": [
        "Rev0689 — mission reclaim compass",
        "makes no C++ source, binary, capability, fixture, or runtime behavior change",
        "folder convergence under evidence-bound local truth",
        "crash-surviving worker boundary",
        "make `claimed` a real product boundary",
        "Rev0690 — split resume transfer claim from execution",
        "Project-Name-rev####-YYYY.MM.DD.HH.MM-foobarnamesummaryhighlightcodename.zip",
        "Honest ceiling after rev0689",
    ],
    "docs/0001-cpp-core-gameplan.md": [
        "Current rev0688 code slice, held by rev0689 mission/reclaim compass",
        "Make durable worker rows real before adding production transport",
        "Do not confuse completed evidence with schedulable work",
        "Split transfer workorder claim from execution",
    ],
    "docs/0003-next-risk-register.md": [
        "Next risk register after rev0689",
        "Claim/execute fusion",
        "No abandoned-lease semantics",
        "Real peer response binding is missing",
        "Tombstone/conflict restart branches are not drained",
    ],
    "audit/rev0689-mission-reclaim-compass-audit.json": [
        "mission-reclaim-compass",
        "authorized peer-to-peer folder convergence under evidence-bound local truth",
        "split resume transfer workorder claim from execution before adding production peer transport",
        "new C++ runtime behavior",
    ],
    "audit/rev0689-mission-reclaim-compass-source.patch": [
        "0079-rev0689-mission-reclaim-compass.md",
        "mission reclaim compass",
        "validate_rev0689_mission_reclaim_compass.py",
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
        raise AssertionError("missing required rev0689 files: " + ", ".join(missing))
    if (ROOT / "bin/rev0689").exists():
        raise AssertionError("rev0689 is non-code-bearing and must not introduce a rev0689 active binary directory")
    if (ROOT / ACTIVE_BINARY).stat().st_mode & 0o111 == 0:
        raise AssertionError("active rev0688 binary must remain executable")


def assert_phrases() -> None:
    for rel, phrases in REQUIRED_PHRASES.items():
        text = (ROOT / rel).read_text(errors="replace")
        for phrase in phrases:
            if phrase not in text:
                raise AssertionError(f"required phrase missing from {rel}: {phrase}")


def assert_logs() -> None:
    prev = (ROOT / "audit/logs/rev0689-rev0688-package-validator-rerun.log").read_text(errors="replace")
    if EXPECTED_PREV_VALIDATOR not in prev:
        raise AssertionError("rev0688 validator rerun log missing expected pass line")
    selftest = (ROOT / "audit/logs/rev0689-active-sync-domain-selftest-rerun.log").read_text(errors="replace")
    if EXPECTED_SELFTEST not in selftest:
        raise AssertionError("active sync-domain selftest rerun log missing expected pass line")
    validator_log = ROOT / VALIDATOR_LOG
    if validator_log.exists():
        text = validator_log.read_text(errors="replace")
        if text.strip() and EXPECTED_VALIDATOR not in text:
            raise AssertionError("rev0689 validator log exists but is missing expected pass line")


def assert_audit() -> None:
    audit = json.loads(AUDIT.read_text())
    if audit.get("revision_id") != "rev0689" or audit.get("parent_revision") != "rev0688":
        raise AssertionError("audit revision lineage mismatch")
    if audit.get("codename") != "mission-reclaim-compass":
        raise AssertionError("audit codename mismatch")
    if audit.get("manifest_kind") != "mission-review-reclaim-compass":
        raise AssertionError("audit manifest kind mismatch")
    if audit.get("product_mission") != "cxx-p2p-file-sync":
        raise AssertionError("audit product mission mismatch")
    if audit.get("active_binary") != ACTIVE_BINARY:
        raise AssertionError("audit active binary mismatch")
    if audit.get("active_binary_sha256") != sha_file(ROOT / ACTIVE_BINARY):
        raise AssertionError("audit active binary sha mismatch")
    if audit.get("cxx_behavior_changed") is not False:
        raise AssertionError("rev0689 must be marked non-code-bearing")
    findings = audit.get("deep_read_findings", {})
    if "crash-surviving daemon worker boundary" not in findings.get("main_gap", ""):
        raise AssertionError("audit main gap mismatch")
    if findings.get("next_code_revision") != "rev0690 split resume transfer claim from execution":
        raise AssertionError("audit next code revision mismatch")
    validation = audit.get("validation", {})
    if validation.get("rev0688_package_validator_rerun") != EXPECTED_PREV_VALIDATOR:
        raise AssertionError("audit prev validator summary mismatch")
    if validation.get("active_sync_domain_selftest_rerun") != EXPECTED_SELFTEST:
        raise AssertionError("audit selftest summary mismatch")
    if validation.get("package_validator_summary") != EXPECTED_VALIDATOR:
        raise AssertionError("audit package validator summary mismatch")


def assert_manifest() -> None:
    manifest = json.loads(MANIFEST.read_text())
    if manifest.get("revision_id") != "rev0689" or manifest.get("parent_revision") != "rev0688":
        raise AssertionError("manifest lineage mismatch")
    if manifest.get("codename") != "mission-reclaim-compass":
        raise AssertionError("manifest codename mismatch")
    if manifest.get("manifest_kind") != "mission-review-reclaim-compass":
        raise AssertionError("manifest kind mismatch")
    if manifest.get("product_mission") != "cxx-p2p-file-sync":
        raise AssertionError("manifest product mission mismatch")
    if manifest.get("active_binary") != ACTIVE_BINARY:
        raise AssertionError("manifest active binary mismatch")
    if manifest.get("active_binary_sha256") != sha_file(ROOT / ACTIVE_BINARY):
        raise AssertionError("manifest active binary sha mismatch")
    if set(manifest.get("excluded_mutable_evidence", [])) != EXCLUDED_MUTABLE:
        raise AssertionError("manifest mutable exclusions mismatch")
    expected_files = []
    for rel in rel_files():
        if rel in EXCLUDED_MUTABLE:
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
