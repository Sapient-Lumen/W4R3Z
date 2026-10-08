#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_VALIDATOR = "rev0665 chunk response envelope package validator passed"
EXPECTED_CTEST = "100% tests passed, 0 tests failed out of 27"
EXPECTED_SELFTEST = "anonsync_core sync domain model selftest passed=149 failed=0"
ACTIVE_BINARY = "bin/rev0665/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
OLD_ACTIVE_BINARY = "bin/rev0664/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
CAPABILITY_MANIFEST = "gateway/rev0648-cpp-ledger-backend-capabilities.json"
AUDIT = ROOT / "audit/rev0665-chunk-response-envelope-audit.json"
MANIFEST = ROOT / "schema/rev0665/slim-cube-manifest.json"

REQUIRED_CURRENT_FILES = [
    "README.md",
    "cpp/anonsync_core/README.md",
    "cpp/anonsync_core/include/anonsync_core.hpp",
    "cpp/anonsync_core/src/sync_domain.cpp",
    ACTIVE_BINARY,
    "bin/HISTORY.md",
    "docs/0001-cpp-core-gameplan.md",
    "docs/0003-next-risk-register.md",
    "docs/0055-rev0665-chunk-response-envelope.md",
    "audit/rev0665-chunk-response-envelope-audit.json",
    "audit/rev0665-chunk-response-envelope-source.patch",
    "audit/logs/rev0665-release-o0-configure.log",
    "audit/logs/rev0665-release-o0-build.log",
    "audit/logs/rev0665-release-o0-ctest.log",
    "audit/logs/rev0665-chunk-response-envelope-selftest.log",
    "audit/logs/rev0665-narrow-asan-ubsan-sync-domain-build.log",
    "audit/logs/rev0665-narrow-asan-ubsan-sync-domain-selftest.log",
    "audit/logs/rev0665-binary-sha256.txt",
    "audit/logs/rev0665-binary-ldd.txt",
    "audit/logs/rev0665-chunk-response-envelope-package-validator.log",
    "tools/validate_rev0665_chunk_response_envelope.py",
]

REQUIRED_PHRASES = {
    "README.md": [
        "C++ peer-to-peer file synchronization system",
        "Rev0665",
        "response-envelope binding",
        "SyncChunkResponseEnvelope",
        "accept_sync_chunk_response_envelope",
        "sync-chunk-response:v1:",
        "not yet",
    ],
    "cpp/anonsync_core/README.md": [
        "anonsync_core rev0665",
        "SyncChunkResponseEnvelope",
        "build_sync_chunk_response_envelope",
        "accept_sync_chunk_response_envelope",
        "response-envelope-checked peer chunk acceptance evidence",
    ],
    "cpp/anonsync_core/include/anonsync_core.hpp": [
        "struct SyncChunkResponseEnvelope",
        "std::string response_idempotency_key;",
        "bool response_envelope_checked = false;",
        "build_sync_chunk_response_envelope",
        "accept_sync_chunk_response_envelope",
    ],
    "cpp/anonsync_core/src/sync_domain.cpp": [
        "chunk_response_envelope_idempotency_key",
        "SyncValidationResult build_sync_chunk_response_envelope",
        "SyncValidationResult accept_sync_chunk_response_envelope",
        "chunk response envelope acceptance response envelope does not match request/entry evidence",
        "chunk response envelope acceptance rejects stale request ids before writing peer bytes",
        "chunk response envelope acceptance binds peer chunk bytes to verified request and response evidence before writing",
    ],
    "docs/0055-rev0665-chunk-response-envelope.md": [
        "chunk response envelope",
        "`SyncChunkResponseEnvelope`",
        "`build_sync_chunk_response_envelope`",
        "`accept_sync_chunk_response_envelope`",
        "cross-batch response confusion",
        "does not run a real or fake peer session",
    ],
    "docs/0001-cpp-core-gameplan.md": [
        "response-envelope-bound peer chunk acceptance",
        "accept_sync_chunk_response_envelope",
    ],
    "docs/0003-next-risk-register.md": [
        "Next risk register after rev0665",
        "SyncChunkResponseEnvelope",
        "accept_sync_chunk_response_envelope",
    ],
    "bin/HISTORY.md": [
        "rev0665",
        "chunk response envelope seam",
        "rev0664: historical source/audit only",
    ],
    "audit/rev0665-chunk-response-envelope-audit.json": [
        "chunk-response-envelope",
        "fixed_by_SyncChunkResponseEnvelope",
        "fixed_by_sync_chunk_response_v1_idempotency_key",
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
        raise AssertionError("missing required rev0665 files: " + ", ".join(missing))
    if (ROOT / OLD_ACTIVE_BINARY).exists():
        raise AssertionError("rev0665 package must not carry the rev0664 active binary")


def assert_phrases() -> None:
    for rel, phrases in REQUIRED_PHRASES.items():
        text = (ROOT / rel).read_text(errors="replace")
        for phrase in phrases:
            if phrase not in text:
                raise AssertionError(f"required phrase missing from {rel}: {phrase}")


def assert_logs() -> None:
    ctest = (ROOT / "audit/logs/rev0665-release-o0-ctest.log").read_text(errors="replace")
    if EXPECTED_CTEST not in ctest:
        raise AssertionError("release ctest summary missing")
    selftest = (ROOT / "audit/logs/rev0665-chunk-response-envelope-selftest.log").read_text(errors="replace")
    if EXPECTED_SELFTEST not in selftest:
        raise AssertionError("sync-domain selftest summary missing")
    asan = (ROOT / "audit/logs/rev0665-narrow-asan-ubsan-sync-domain-selftest.log").read_text(errors="replace")
    if EXPECTED_SELFTEST not in asan:
        raise AssertionError("narrow asan/ubsan selftest summary missing")
    validator_log = (ROOT / "audit/logs/rev0665-chunk-response-envelope-package-validator.log").read_text(errors="replace")
    if EXPECTED_VALIDATOR not in validator_log:
        raise AssertionError("package validator log missing expected pass line")


def assert_audit() -> None:
    audit = json.loads(AUDIT.read_text())
    if audit.get("revision_id") != "rev0665" or audit.get("parent_revision") != "rev0664":
        raise AssertionError("audit revision lineage mismatch")
    if audit.get("product_mission") != "cxx-p2p-file-sync":
        raise AssertionError("audit product mission mismatch")
    if audit.get("active_binary") != ACTIVE_BINARY:
        raise AssertionError("audit active binary mismatch")
    if audit.get("active_binary_sha256") != sha_file(ROOT / ACTIVE_BINARY):
        raise AssertionError("audit active binary sha mismatch")
    if not audit.get("cxx_behavior_changed"):
        raise AssertionError("rev0665 must claim C++ behavior changed")
    required_api = {
        "SyncChunkResponseEnvelope added for network-facing chunk response evidence",
        "SyncRequestedChunkAcceptanceResult extended with response_idempotency_key and response_envelope_checked",
        "build_sync_chunk_response_envelope added to construct deterministic sync-chunk-response:v1 evidence for selected request chunks",
        "accept_sync_chunk_response_envelope added to rebuild request and response envelope evidence before staging peer bytes",
        "chunk response envelope acceptance rejects stale request ids, forged response ids, inconsistent request batches, and unselected chunks before disk writes",
    }
    missing_api = required_api - set(audit.get("cxx_api_changed", []))
    if missing_api:
        raise AssertionError("audit missing API changes: " + ", ".join(sorted(missing_api)))
    findings = audit.get("audit_findings", {})
    if findings.get("peer_response_metadata_was_not_explicitly_modeled") != "fixed_by_SyncChunkResponseEnvelope":
        raise AssertionError("audit must record explicit response envelope fix")
    if findings.get("future_session_layer_could_confuse_stale_request_ids") != "fixed_by_accept_sync_chunk_response_envelope_request_id_check":
        raise AssertionError("audit must record stale request id fix")
    if findings.get("future_session_layer_had_no_response_commitment_key") != "fixed_by_sync_chunk_response_v1_idempotency_key":
        raise AssertionError("audit must record response commitment key fix")
    validation = audit.get("validation", {})
    if validation.get("release_ctest_summary") != EXPECTED_CTEST:
        raise AssertionError("audit ctest summary mismatch")
    if validation.get("sync_domain_selftest_summary") != EXPECTED_SELFTEST:
        raise AssertionError("audit sync-domain selftest summary mismatch")
    if validation.get("narrow_asan_ubsan_selftest_summary") != EXPECTED_SELFTEST:
        raise AssertionError("audit narrow asan/ubsan selftest summary mismatch")


def assert_binary_sha() -> None:
    line = (ROOT / "audit/logs/rev0665-binary-sha256.txt").read_text().strip().split()
    if len(line) < 2:
        raise AssertionError("binary sha256 log malformed")
    expected_sha, rel = line[0], line[1]
    if rel != ACTIVE_BINARY:
        raise AssertionError("binary sha256 log points at wrong active binary")
    if sha_file(ROOT / ACTIVE_BINARY) != expected_sha:
        raise AssertionError("active binary sha256 mismatch")


def assert_manifest() -> None:
    manifest = json.loads(MANIFEST.read_text())
    if manifest.get("revision_id") != "rev0665" or manifest.get("parent_revision") != "rev0664":
        raise AssertionError("rev0665 manifest lineage mismatch")
    if manifest.get("manifest_kind") != "code-bearing-chunk-response-envelope":
        raise AssertionError("rev0665 manifest kind mismatch")
    if manifest.get("product_mission") != "cxx-p2p-file-sync":
        raise AssertionError("rev0665 product mission tag mismatch")
    if manifest.get("codename") != "chunk-response-envelope":
        raise AssertionError("rev0665 codename mismatch")
    if manifest.get("active_binary") != ACTIVE_BINARY:
        raise AssertionError("active binary should be rev0665")
    if manifest.get("capability_manifest") != CAPABILITY_MANIFEST:
        raise AssertionError("capability manifest should remain rev0648 until ledger schema changes")
    rows = manifest.get("files", [])
    if manifest.get("file_count") != len(rows):
        raise AssertionError("manifest file_count mismatch")
    by_path = {row["path"]: row for row in rows}
    for path in REQUIRED_CURRENT_FILES:
        if path not in by_path:
            raise AssertionError(f"rev0665 file missing from manifest: {path}")
    if OLD_ACTIVE_BINARY in by_path:
        raise AssertionError("manifest must not include old rev0664 active binary")
    if "schema/rev0665/slim-cube-manifest.json" not in set(manifest.get("excluded_mutable_evidence", [])):
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
