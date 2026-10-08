"""rev0097 native archive-replay fold audit."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .foldmap import audit_fold_map
from .foldregistry import audit_fold_registry
from .ids import DOMAIN, sha256
from .nativearchivefold import audit_native_archive_fold
from .nativefoldspine import audit_native_fold_spine
from .surfaceledger import audit_surface_ledger, entries_for_revision

NATIVE_ARCHIVE_REPLAY_FOLD_DOMAIN = DOMAIN + b":native-archive-replay-fold-v1:"


@dataclass(frozen=True)
class NativeArchiveReplayFoldFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class NativeArchiveReplayFoldReport:
    revision: str
    artifact_stem: str
    status: str
    predecessor_status: str
    fold_map_status: str
    fold_registry_status: str
    surface_ledger_status: str
    native_spine_status: str
    findings: tuple[NativeArchiveReplayFoldFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")


def audit_native_archive_replay_fold(root: str | Path, *, revision: str = "rev0097") -> NativeArchiveReplayFoldReport:
    root_path = Path(root)
    artifact = root_path.name
    findings: list[NativeArchiveReplayFoldFinding] = []
    predecessor = audit_native_archive_fold(root_path, revision="rev0096")
    fold_map = audit_fold_map(root_path, revision=revision, artifact_stem=artifact)
    fold_registry = audit_fold_registry(root_path, revision=revision)
    ledger = audit_surface_ledger(root_path, entries_for_revision(revision))
    native_spine = audit_native_fold_spine(root_path, revision=revision)
    required = (
        "src/i2p_dht_lab/nativearchivereplay.py",
        "src/i2p_dht_lab/nativepromotereview.py",
        "src/i2p_dht_lab/nativearchivereplayfold.py",
        "tests/test_rev0097_nativearchivereplay_promotereview_spinecompact.py",
        "docs/1008-rev0097-nativearchivereplay-promotereview-spinecompact.md",
    )
    for rel in required:
        if not (root_path / rel).exists():
            findings.append(NativeArchiveReplayFoldFinding("error", "missing_rev0097_path", rel, "rev0097 native archive replay path missing"))
    for label, status in (("predecessor", predecessor.status), ("fold_map", fold_map.status), ("fold_registry", fold_registry.status), ("native_spine", native_spine.status)):
        if status != "pass":
            findings.append(NativeArchiveReplayFoldFinding("error", f"{label}_failed", label, f"{label} audit did not pass"))
    if not ledger.ok:
        findings.append(NativeArchiveReplayFoldFinding("error", "surface_ledger_failed", "surfaceledger", "rev0097 surface ledger failed"))
    status = "pass" if not any(f.severity == "error" for f in findings) else "fail"
    digest = sha256(NATIVE_ARCHIVE_REPLAY_FOLD_DOMAIN + bencode({
        b"revision": revision,
        b"artifact": artifact,
        b"status": status,
        b"predecessor": predecessor.status,
        b"fold_map": fold_map.status,
        b"fold_registry": fold_registry.status,
        b"surface_ledger": 1 if ledger.ok else 0,
        b"native_spine": native_spine.status,
        b"findings": [finding.bvalue() for finding in findings],
    }))
    return NativeArchiveReplayFoldReport(revision, artifact, status, predecessor.status, fold_map.status, fold_registry.status, "pass" if ledger.ok else "fail", native_spine.status, tuple(findings), digest)
