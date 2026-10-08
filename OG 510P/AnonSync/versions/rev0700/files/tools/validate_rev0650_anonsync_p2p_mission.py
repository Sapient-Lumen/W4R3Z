#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "schema" / "rev0650" / "slim-cube-manifest.json"
MISSION_DOC = ROOT / "docs" / "0040-rev0650-anonsync-p2p-sync-mission-correction.md"
AUDIT = ROOT / "audit" / "rev0650-anonsync-p2p-sync-mission-correction-audit.json"

REQUIRED_CURRENT_FILES = [
    "README.md",
    "cpp/anonsync_core/README.md",
    "docs/0001-cpp-core-gameplan.md",
    "docs/0003-next-risk-register.md",
    "docs/0034-rev0644-deep-mission-review.md",
    "docs/0039-rev0649-mission-kernel-boundary-compass.md",
    "docs/0040-rev0650-anonsync-p2p-sync-mission-correction.md",
    "audit/rev0650-anonsync-p2p-sync-mission-correction-audit.json",
    "tools/validate_rev0650_anonsync_p2p_mission.py",
]

REQUIRED_PHRASES = {
    "README.md": [
        "C++ peer-to-peer file synchronization system",
        "Resilio Sync-style local folder replication",
        "Rev0650 is a mission correction only",
        "not yet implement the whole sync product",
    ],
    "cpp/anonsync_core/README.md": [
        "peer-to-peer file synchronization system",
        "future sync mutation ledger",
        "Python remains packaging/validation glue; product code belongs in `cpp/anonsync_core`",
    ],
    "docs/0001-cpp-core-gameplan.md": [
        "C++ peer-to-peer file synchronization engine",
        "Product behavior should land in `cpp/anonsync_core`",
    ],
    "docs/0003-next-risk-register.md": [
        "make AnonSync actually sync files",
        "Define the C++ sync domain model",
        "fake authenticated peer session",
    ],
    "docs/0039-rev0649-mission-kernel-boundary-compass.md": [
        "superseded by rev0650",
        "incorrectly reframed AnonSync away from synchronization",
    ],
    "docs/0040-rev0650-anonsync-p2p-sync-mission-correction.md": [
        "Resilio Sync-style peer-to-peer folder synchronization engine",
        "The next code-bearing revision should add a small C++ sync-domain slice",
        "stop adding generic features",
    ],
}

FORBIDDEN_CURRENT_PHRASES = {
    "README.md": [
        "local authorization-and-idempotency evidence kernel",
        "not anonymity, synchronization",
    ],
    "cpp/anonsync_core/README.md": [
        "local authorization, replay-reservation, outbox, relay-recovery, and evidence kernel",
    ],
    "docs/0001-cpp-core-gameplan.md": [
        "small policy decision and idempotency kernel",
    ],
    "docs/0003-next-risk-register.md": [
        "rename the project",
        "avoid an anonymity implication",
    ],
}


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def assert_contains(path: str, phrase: str) -> None:
    text = (ROOT / path).read_text()
    if phrase not in text:
        raise AssertionError(f"missing required phrase in {path!r}: {phrase!r}")


def assert_not_contains(path: str, phrase: str) -> None:
    text = (ROOT / path).read_text()
    if phrase in text:
        raise AssertionError(f"forbidden stale phrase in {path!r}: {phrase!r}")


def assert_mission_docs() -> None:
    for path, phrases in REQUIRED_PHRASES.items():
        for phrase in phrases:
            assert_contains(path, phrase)
    for path, phrases in FORBIDDEN_CURRENT_PHRASES.items():
        for phrase in phrases:
            assert_not_contains(path, phrase)
    audit = json.loads(AUDIT.read_text())
    if audit.get("product_mission") != "AnonSync is a C++ peer-to-peer file synchronization system aiming at Resilio Sync-style folder replication across authorized devices.":
        raise AssertionError("audit product mission mismatch")
    if audit.get("cxx_behavior_changed") is not False:
        raise AssertionError("rev0650 must not claim C++ behavior changed")


def assert_manifest() -> None:
    manifest = json.loads(MANIFEST.read_text())
    if manifest.get("revision_id") != "rev0650" or manifest.get("parent_revision") != "rev0649":
        raise AssertionError("rev0650 manifest lineage mismatch")
    if manifest.get("manifest_kind") != "mission-correction-overlay-manifest":
        raise AssertionError("rev0650 manifest kind mismatch")
    if manifest.get("product_mission") != "cxx-p2p-file-sync":
        raise AssertionError("rev0650 product mission tag mismatch")
    rows = manifest.get("files", [])
    if manifest.get("file_count") != len(rows):
        raise AssertionError("manifest file_count mismatch")
    by_path = {row["path"]: row for row in rows}
    for path in REQUIRED_CURRENT_FILES:
        if path not in by_path:
            raise AssertionError(f"mission file missing from manifest: {path}")
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
    if manifest.get("active_binary") != "bin/rev0648/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3":
        raise AssertionError("active binary should remain rev0648")
    if manifest.get("capability_manifest") != "gateway/rev0648-cpp-ledger-backend-capabilities.json":
        raise AssertionError("capability manifest should remain rev0648")


def main() -> int:
    assert_mission_docs()
    assert_manifest()
    print("rev0650 AnonSync P2P sync mission validator passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
