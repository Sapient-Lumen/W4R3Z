#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_VALIDATOR = "rev0667 chunk transfer round package validator passed"
EXPECTED_CTEST = "100% tests passed, 0 tests failed out of 27"
EXPECTED_SELFTEST = "anonsync_core sync domain model selftest passed=167 failed=0"
ACTIVE_BINARY = "bin/rev0667/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
OLD_ACTIVE_BINARY = "bin/rev0666/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
CAPABILITY_MANIFEST = "gateway/rev0648-cpp-ledger-backend-capabilities.json"
AUDIT = ROOT / "audit/rev0667-chunk-transfer-round-audit.json"
MANIFEST = ROOT / "schema/rev0667/slim-cube-manifest.json"

REQUIRED_CURRENT_FILES = [
    "README.md",
    "cpp/anonsync_core/README.md",
    "cpp/anonsync_core/include/anonsync_core.hpp",
    "cpp/anonsync_core/src/sync_domain.cpp",
    ACTIVE_BINARY,
    "bin/HISTORY.md",
    "docs/0001-cpp-core-gameplan.md",
    "docs/0003-next-risk-register.md",
    "docs/0057-rev0667-chunk-transfer-round.md",
    "audit/rev0667-chunk-transfer-round-audit.json",
    "audit/rev0667-chunk-transfer-round-source.patch",
    "audit/logs/rev0667-release-o0-configure.log",
    "audit/logs/rev0667-release-o0-build.log",
    "audit/logs/rev0667-release-o0-ctest.log",
    "audit/logs/rev0667-chunk-transfer-round-selftest.log",
    "audit/logs/rev0667-narrow-asan-ubsan-sync-domain-build.log",
    "audit/logs/rev0667-narrow-asan-ubsan-sync-domain-selftest.log",
    "audit/logs/rev0667-binary-sha256.txt",
    "audit/logs/rev0667-binary-ldd.txt",
    "audit/logs/rev0667-chunk-transfer-round-package-validator.log",
    "tools/validate_rev0667_chunk_transfer_round.py",
]

REQUIRED_PHRASES = {
    "README.md": [
        "C++ peer-to-peer file synchronization system",
        "Rev0667",
        "post-batch transfer-round continuation",
        "SyncChunkTransferRoundResult",
        "accept_sync_chunk_response_batch_and_plan_next",
        "ready to materialize",
        "not yet",
    ],
    "cpp/anonsync_core/README.md": [
        "anonsync_core rev0667",
        "SyncChunkTransferRoundResult",
        "accept_sync_chunk_response_batch_and_plan_next",
        "post-batch transfer-round continuation",
    ],
    "cpp/anonsync_core/include/anonsync_core.hpp": [
        "struct SyncChunkTransferRoundResult",
        "SyncStagedTransferInspectionResult post_batch_inspection;",
        "SyncChunkRequestPlanResult next_request_plan;",
        "bool ready_to_materialize = false;",
        "accept_sync_chunk_response_batch_and_plan_next",
    ],
    "cpp/anonsync_core/src/sync_domain.cpp": [
        "SyncValidationResult accept_sync_chunk_response_batch_and_plan_next",
        "chunk transfer round requires matching write and inspection roots",
        "chunk transfer round post-batch inspection disagrees with acceptance completion state",
        "chunk transfer round re-inspects after a partial batch and emits the next deterministic request",
        "chunk transfer round marks the staged file materialization-ready after the final batch",
    ],
    "docs/0057-rev0667-chunk-transfer-round.md": [
        "chunk transfer round continuation",
        "`SyncChunkTransferRoundResult`",
        "`accept_sync_chunk_response_batch_and_plan_next`",
        "session-layer continuation drift",
        "still does not run a real peer protocol",
    ],
    "docs/0001-cpp-core-gameplan.md": [
        "post-batch transfer-round continuation",
        "accept_sync_chunk_response_batch_and_plan_next",
    ],
    "docs/0003-next-risk-register.md": [
        "Next risk register after rev0667",
        "SyncChunkTransferRoundResult",
        "accept_sync_chunk_response_batch_and_plan_next",
    ],
    "bin/HISTORY.md": [
        "rev0667",
        "chunk transfer round continuation seam",
        "rev0666: historical source/audit only",
    ],
    "audit/rev0667-chunk-transfer-round-audit.json": [
        "chunk-transfer-round",
        "fixed_by_SyncChunkTransferRoundResult",
        "fixed_by_matching_write_and_inspection_root_check",
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
        raise AssertionError("missing required rev0667 files: " + ", ".join(missing))
    if (ROOT / OLD_ACTIVE_BINARY).exists():
        raise AssertionError("rev0667 package must not carry the rev0666 active binary")


def assert_phrases() -> None:
    for rel, phrases in REQUIRED_PHRASES.items():
        text = (ROOT / rel).read_text(errors="replace")
        for phrase in phrases:
            if phrase not in text:
                raise AssertionError(f"required phrase missing from {rel}: {phrase}")


def assert_logs() -> None:
    ctest = (ROOT / "audit/logs/rev0667-release-o0-ctest.log").read_text(errors="replace")
    if EXPECTED_CTEST not in ctest:
        raise AssertionError("release ctest summary missing")
    selftest = (ROOT / "audit/logs/rev0667-chunk-transfer-round-selftest.log").read_text(errors="replace")
    if EXPECTED_SELFTEST not in selftest:
        raise AssertionError("sync-domain selftest summary missing")
    asan = (ROOT / "audit/logs/rev0667-narrow-asan-ubsan-sync-domain-selftest.log").read_text(errors="replace")
    if EXPECTED_SELFTEST not in asan:
        raise AssertionError("narrow asan/ubsan selftest summary missing")
    validator_log = ROOT / "audit/logs/rev0667-chunk-transfer-round-package-validator.log"
    if validator_log.exists() and EXPECTED_VALIDATOR not in validator_log.read_text(errors="replace"):
        raise AssertionError("package validator log exists but is missing expected pass line")


def assert_audit() -> None:
    audit = json.loads(AUDIT.read_text())
    if audit.get("revision_id") != "rev0667" or audit.get("parent_revision") != "rev0666":
        raise AssertionError("audit revision lineage mismatch")
    if audit.get("product_mission") != "cxx-p2p-file-sync":
        raise AssertionError("audit product mission mismatch")
    if audit.get("active_binary") != ACTIVE_BINARY:
        raise AssertionError("audit active binary mismatch")
    if audit.get("active_binary_sha256") != sha_file(ROOT / ACTIVE_BINARY):
        raise AssertionError("audit active binary sha mismatch")
    if not audit.get("cxx_behavior_changed"):
        raise AssertionError("rev0667 must claim C++ behavior changed")
    required_api = {
        "SyncChunkTransferRoundResult added for batch acceptance evidence, post-batch inspection, next request plan, and ready/continuation flags",
        "accept_sync_chunk_response_batch_and_plan_next added to accept a batch, inspect post-write staged receipt state, and build the next request plan",
        "chunk transfer round rejects mismatched write and inspection roots before accepting peer bytes",
        "sync-domain selftest extended with a two-round four-chunk transfer that produces a continuation plan and then a materialization-ready result",
    }
    missing_api = required_api - set(audit.get("cxx_api_changed", []))
    if missing_api:
        raise AssertionError("audit missing API changes: " + ", ".join(sorted(missing_api)))
    findings = audit.get("audit_findings", {})
    if findings.get("post_batch_state_was_left_to_session_glue") != "fixed_by_SyncChunkTransferRoundResult":
        raise AssertionError("audit must record post-batch state fix")
    if findings.get("caller_could_write_one_staging_root_and_inspect_another") != "fixed_by_matching_write_and_inspection_root_check":
        raise AssertionError("audit must record root mismatch fix")
    if findings.get("next_request_could_be_built_from_stale_pre_batch_inspection") != "fixed_by_accept_sync_chunk_response_batch_and_plan_next_post_batch_reinspection":
        raise AssertionError("audit must record stale inspection continuation fix")
    validation = audit.get("validation", {})
    if validation.get("release_ctest_summary") != EXPECTED_CTEST:
        raise AssertionError("audit ctest summary mismatch")
    if validation.get("sync_domain_selftest_summary") != EXPECTED_SELFTEST:
        raise AssertionError("audit sync-domain selftest summary mismatch")
    if validation.get("narrow_asan_ubsan_selftest_summary") != EXPECTED_SELFTEST:
        raise AssertionError("audit narrow asan/ubsan selftest summary mismatch")


def assert_binary_sha() -> None:
    line = (ROOT / "audit/logs/rev0667-binary-sha256.txt").read_text().strip().split()
    if len(line) < 2:
        raise AssertionError("binary sha256 log malformed")
    expected_sha, rel = line[0], line[1]
    if rel != ACTIVE_BINARY:
        raise AssertionError("binary sha256 log points at wrong active binary")
    if sha_file(ROOT / ACTIVE_BINARY) != expected_sha:
        raise AssertionError("active binary sha256 mismatch")


def assert_manifest() -> None:
    manifest = json.loads(MANIFEST.read_text())
    if manifest.get("revision_id") != "rev0667" or manifest.get("parent_revision") != "rev0666":
        raise AssertionError("rev0667 manifest lineage mismatch")
    if manifest.get("manifest_kind") != "code-bearing-chunk-transfer-round":
        raise AssertionError("rev0667 manifest kind mismatch")
    if manifest.get("product_mission") != "cxx-p2p-file-sync":
        raise AssertionError("rev0667 product mission tag mismatch")
    if manifest.get("codename") != "chunk-transfer-round":
        raise AssertionError("rev0667 codename mismatch")
    if manifest.get("active_binary") != ACTIVE_BINARY:
        raise AssertionError("active binary should be rev0667")
    if manifest.get("capability_manifest") != CAPABILITY_MANIFEST:
        raise AssertionError("capability manifest should remain rev0648-bound until sync-ledger capabilities change")
    rows = manifest.get("files", [])
    if manifest.get("file_count") != len(rows):
        raise AssertionError("manifest file_count mismatch")
    files = {item.get("path"): item for item in rows}
    missing = sorted(path for path in REQUIRED_CURRENT_FILES if path not in files)
    if missing:
        raise AssertionError("rev0667 manifest missing paths: " + ", ".join(missing))
    if OLD_ACTIVE_BINARY in files:
        raise AssertionError("manifest must not include old rev0666 active binary")
    if "schema/rev0667/slim-cube-manifest.json" not in set(manifest.get("excluded_mutable_evidence", [])):
        raise AssertionError("manifest must exclude itself")
    for path, item in files.items():
        full = ROOT / path
        if not full.exists():
            raise AssertionError("manifest path missing from package: " + path)
        if item.get("sha256") != sha_file(full):
            raise AssertionError("manifest sha mismatch for " + path)
        if item.get("size_bytes") != full.stat().st_size:
            raise AssertionError("manifest size mismatch for " + path)


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
