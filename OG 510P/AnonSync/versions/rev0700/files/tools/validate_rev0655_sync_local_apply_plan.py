#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "schema" / "rev0655" / "slim-cube-manifest.json"
AUDIT = ROOT / "audit" / "rev0655-sync-local-apply-plan-audit.json"
ACTIVE_BINARY = "bin/rev0655/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
CAPABILITY_MANIFEST = "gateway/rev0648-cpp-ledger-backend-capabilities.json"
EXPECTED_SELFTEST = "anonsync_core sync domain model selftest passed=62 failed=0"
EXPECTED_CTEST = "100% tests passed, 0 tests failed out of 27"
EXPECTED_VALIDATOR = "rev0655 sync local apply plan package validator passed"

REQUIRED_CURRENT_FILES = [
    "README.md",
    "bin/HISTORY.md",
    ACTIVE_BINARY,
    "cpp/anonsync_core/CMakeLists.txt",
    "cpp/anonsync_core/README.md",
    "cpp/anonsync_core/include/anonsync_core.hpp",
    "cpp/anonsync_core/src/anonsync_core.cpp",
    "cpp/anonsync_core/src/sync_domain.cpp",
    "docs/0001-cpp-core-gameplan.md",
    "docs/0003-next-risk-register.md",
    "docs/0045-rev0655-sync-local-apply-plan.md",
    "audit/rev0655-sync-local-apply-plan-audit.json",
    "audit/rev0655-sync-local-apply-plan-source.patch",
    "audit/logs/rev0655-release-o0-configure.log",
    "audit/logs/rev0655-release-o0-build.log",
    "audit/logs/rev0655-release-o0-ctest.log",
    "audit/logs/rev0655-sync-local-apply-plan-selftest.log",
    "audit/logs/rev0655-narrow-asan-ubsan-sync-domain-build.log",
    "audit/logs/rev0655-narrow-asan-ubsan-sync-domain-selftest.log",
    "audit/logs/rev0655-binary-sha256.txt",
    "audit/logs/rev0655-binary-ldd.txt",
    "audit/logs/rev0655-sync-local-apply-plan-package-validator.log",
    "tools/validate_rev0655_sync_local_apply_plan.py",
]

REQUIRED_PHRASES = {
    "README.md": [
        "C++ peer-to-peer file synchronization system",
        "Rev0655 adds `SyncLocalApplyOptions`",
        "build_sync_local_apply_plan",
        "sync-local-apply:v1:",
        "Self-validates constructed manifest diff and local apply plans",
        "not yet",
    ],
    "cpp/anonsync_core/README.md": [
        "anonsync_core rev0655",
        "SyncLocalApplyPlan",
        "build_sync_local_apply_plan",
        "The constructed diff and apply plans are self-validated before success is returned",
        "Known ceiling after rev0655",
    ],
    "cpp/anonsync_core/include/anonsync_core.hpp": [
        "enum class SyncLocalApplyAction",
        "struct SyncLocalApplyOptions",
        "struct SyncLocalApplyPlanEntry",
        "struct SyncLocalApplyPlan",
        "SyncValidationResult build_sync_local_apply_plan",
    ],
    "cpp/anonsync_core/src/sync_domain.cpp": [
        "local_apply_action_for_plan_action",
        "local_apply_idempotency_key",
        "remote_staging_relative_path_for_entry_or_throw",
        "conflict_copy_relative_path_for_entry_or_throw",
        "validate_local_apply_plan_shape",
        "build_sync_local_apply_plan",
        "built sync manifest diff plan invalid",
        "built sync local apply plan invalid",
        "local apply plan rejects staging roots inside the synchronized folder tree",
        "local apply plan preserves local conflicts and stages the remote conflict version",
    ],
    "cpp/anonsync_core/src/anonsync_core.cpp": [
        "--selftest-sync-domain-model",
        "run_sync_domain_model_selftest",
    ],
    "cpp/anonsync_core/CMakeLists.txt": [
        "src/sync_domain.cpp",
        "anonsync_core_sync_domain_model_selftest",
    ],
    "docs/0001-cpp-core-gameplan.md": [
        "turned into safe local filesystem intents in rev0655",
        "partial-file staging",
        "manifest/path/index/diff",
    ],
    "docs/0003-next-risk-register.md": [
        "Next risk register after rev0655",
        "local apply planning",
        "Add real staged chunk receipt and apply",
    ],
    "docs/0045-rev0655-sync-local-apply-plan.md": [
        "C++ sync local apply-plan seam",
        "SyncLocalApplyAction",
        "sync-local-apply:v1:",
        "staging root must be separate from the synchronized folder tree",
        "does not write chunk bytes",
    ],
    "audit/logs/rev0655-sync-local-apply-plan-selftest.log": [
        EXPECTED_SELFTEST,
    ],
    "audit/logs/rev0655-narrow-asan-ubsan-sync-domain-selftest.log": [
        EXPECTED_SELFTEST,
    ],
    "audit/logs/rev0655-release-o0-ctest.log": [
        EXPECTED_CTEST,
    ],
    "audit/logs/rev0655-sync-local-apply-plan-package-validator.log": [
        EXPECTED_VALIDATOR,
    ],
    "bin/HISTORY.md": [
        "rev0655",
        "local apply-plan seam",
        "rev0654 runnable binary is intentionally omitted",
    ],
}

FORBIDDEN_CURRENT_PHRASES = {
    "README.md": [
        "Rev0654 adds `SyncManifestDiffPlan`",
        "local authorization-and-idempotency evidence kernel",
    ],
    "cpp/anonsync_core/README.md": [
        "# anonsync_core rev0654",
        "Known ceiling after rev0654",
    ],
    "docs/0003-next-risk-register.md": [
        "Next risk register after rev0654",
    ],
}


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def text(path: str) -> str:
    return (ROOT / path).read_text(errors="replace")


def assert_contains(path: str, phrase: str) -> None:
    if phrase not in text(path):
        raise AssertionError(f"missing required phrase in {path!r}: {phrase!r}")


def assert_not_contains(path: str, phrase: str) -> None:
    if phrase in text(path):
        raise AssertionError(f"forbidden stale phrase in {path!r}: {phrase!r}")


def assert_docs_and_code() -> None:
    for path in REQUIRED_CURRENT_FILES:
        if not (ROOT / path).exists():
            raise AssertionError(f"required rev0655 file missing: {path}")
    for stale in [
        "bin/rev0654/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3",
        "bin/rev0653/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3",
        "bin/rev0652/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3",
        "bin/rev0651/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3",
    ]:
        if (ROOT / stale).exists():
            raise AssertionError(f"stale runnable binary should not be packaged: {stale}")
    for path, phrases in REQUIRED_PHRASES.items():
        for phrase in phrases:
            assert_contains(path, phrase)
    for path, phrases in FORBIDDEN_CURRENT_PHRASES.items():
        for phrase in phrases:
            assert_not_contains(path, phrase)
    audit = json.loads(AUDIT.read_text())
    if audit.get("revision_id") != "rev0655" or audit.get("parent_revision") != "rev0654":
        raise AssertionError("audit lineage mismatch")
    if audit.get("product_mission") != "cxx-p2p-file-sync":
        raise AssertionError("audit product mission mismatch")
    if audit.get("cxx_behavior_changed") is not True:
        raise AssertionError("rev0655 must claim C++ behavior changed")
    findings = audit.get("audit_findings", {})
    if findings.get("diff_plan_too_abstract_for_disk_safety") != "fixed":
        raise AssertionError("audit must record local apply planning fix")
    if findings.get("staging_under_sync_root_risk") != "rejected":
        raise AssertionError("audit must record staging-root rejection")
    if findings.get("constructed_plan_shape_trust") != "self_validated":
        raise AssertionError("audit must record constructed plan self-validation")
    validation = audit.get("validation", {})
    if validation.get("release_ctest_summary") != EXPECTED_CTEST:
        raise AssertionError("audit ctest summary mismatch")
    if validation.get("sync_domain_selftest_summary") != EXPECTED_SELFTEST:
        raise AssertionError("audit sync-domain selftest summary mismatch")
    if validation.get("narrow_asan_ubsan_sync_domain_selftest_summary") != EXPECTED_SELFTEST:
        raise AssertionError("audit narrow sanitizer selftest summary mismatch")


def assert_binary_sha() -> None:
    line = (ROOT / "audit/logs/rev0655-binary-sha256.txt").read_text().strip().split()
    if len(line) < 2:
        raise AssertionError("binary sha256 log malformed")
    expected_sha, rel = line[0], line[1]
    if rel != ACTIVE_BINARY:
        raise AssertionError("binary sha256 log points at wrong active binary")
    if sha_file(ROOT / ACTIVE_BINARY) != expected_sha:
        raise AssertionError("active binary sha256 mismatch")


def assert_manifest() -> None:
    manifest = json.loads(MANIFEST.read_text())
    if manifest.get("revision_id") != "rev0655" or manifest.get("parent_revision") != "rev0654":
        raise AssertionError("rev0655 manifest lineage mismatch")
    if manifest.get("manifest_kind") != "code-bearing-sync-local-apply-plan":
        raise AssertionError("rev0655 manifest kind mismatch")
    if manifest.get("product_mission") != "cxx-p2p-file-sync":
        raise AssertionError("rev0655 product mission tag mismatch")
    if manifest.get("active_binary") != ACTIVE_BINARY:
        raise AssertionError("active binary should be rev0655")
    if manifest.get("capability_manifest") != CAPABILITY_MANIFEST:
        raise AssertionError("capability manifest should remain rev0648 until ledger schema changes")
    rows = manifest.get("files", [])
    if manifest.get("file_count") != len(rows):
        raise AssertionError("manifest file_count mismatch")
    by_path = {row["path"]: row for row in rows}
    for path in REQUIRED_CURRENT_FILES:
        if path not in by_path:
            raise AssertionError(f"rev0655 file missing from manifest: {path}")
    excluded = set(manifest.get("excluded_mutable_evidence", []))
    if "schema/rev0655/slim-cube-manifest.json" not in excluded:
        raise AssertionError("manifest must exclude itself")
    for row in rows:
        rel = row["path"]
        p = ROOT / rel
        if not p.exists():
            raise AssertionError(f"manifest file missing on disk: {rel}")
        data = p.read_bytes()
        if len(data) != row["size_bytes"]:
            raise AssertionError(f"manifest size mismatch: {rel}")
        if hashlib.sha256(data).hexdigest() != row["sha256"]:
            raise AssertionError(f"manifest sha mismatch: {rel}")
    if manifest.get("active_binary_sha256") != sha_file(ROOT / ACTIVE_BINARY):
        raise AssertionError("active binary sha not bound in manifest")


def main() -> int:
    assert_docs_and_code()
    assert_binary_sha()
    assert_manifest()
    print(EXPECTED_VALIDATOR)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
