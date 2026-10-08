"""rev0045 bridge-epoch fold audit.

This audit keeps the current public-bridge epoch/key-receipt/shadow-fire path
visible while preserving rev0044's policy/authority branch-seal predecessor.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .branchsealfold import audit_branch_seal
from .foldmap import audit_fold_map
from .foldregistry import audit_fold_registry
from .ids import DOMAIN, sha256
from .surfaceledger import audit_surface_ledger, entries_for_revision

BRIDGE_EPOCH_FOLD_DOMAIN = DOMAIN + b":bridge-epoch-fold-v1:"


@dataclass(frozen=True)
class BridgeEpochFoldFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class BridgeEpochFoldReport:
    revision: str
    artifact_stem: str
    status: str
    predecessor_status: str
    foldmap_status: str
    registry_status: str
    surface_ledger_status: str
    findings: tuple[BridgeEpochFoldFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")


REV0045_PATHS = (
    "src/i2p_dht_lab/bridgeepoch.py",
    "src/i2p_dht_lab/keyreceiptlane.py",
    "src/i2p_dht_lab/shadowfire.py",
    "src/i2p_dht_lab/bridgeepochfold.py",
    "tests/test_rev0045_bridgeepoch_keyreceipt_shadowfire.py",
    "docs/469-rev0045-bridgeepoch-keyreceipt-shadowfire.md",
    "docs/470-public-bridge-epoch-windows.md",
    "docs/471-key-receipt-lane.md",
    "docs/472-shadow-fire-joined-boundary.md",
    "docs/473-bridgeepochfold-audit-refactor.md",
)
NEEDLES = ("rev0045", "bridgeepoch", "keyreceiptlane", "shadowfire", "bridgeepochfold")


def _contains(path: Path, needle: str) -> bool:
    try:
        return needle in path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return False


def audit_bridge_epoch_fold(root: str | Path, *, revision: str = "rev0045", artifact_stem: str | None = None) -> BridgeEpochFoldReport:
    if revision != "rev0045":
        raise ValueError("bridgeepochfold currently audits rev0045")
    root_path = Path(root)
    artifact_stem = artifact_stem or root_path.name
    findings: list[BridgeEpochFoldFinding] = []
    for rel in REV0045_PATHS:
        if not (root_path / rel).exists():
            findings.append(BridgeEpochFoldFinding("error", "missing_rev0045_path", rel, "rev0045 bridge-epoch path is absent"))
    for surface_path in ("PUBLIC_SURFACE.json", "HEAD_REGISTRY.json", "docs/00-index.md"):
        for needle in NEEDLES:
            if not _contains(root_path / surface_path, needle):
                findings.append(BridgeEpochFoldFinding("error", "surface_missing_needle", surface_path, f"missing {needle}"))
    try:
        predecessor = audit_branch_seal(root_path, revision="rev0044", artifact_stem=artifact_stem)
        predecessor_status = predecessor.status
        if predecessor.error_count:
            findings.append(BridgeEpochFoldFinding("error", "branchsealfold_failed", "src/i2p_dht_lab/branchsealfold.py", "rev0044 predecessor fold failed"))
    except Exception as exc:  # pragma: no cover
        predecessor_status = "exception"
        findings.append(BridgeEpochFoldFinding("error", "branchsealfold_exception", "src/i2p_dht_lab/branchsealfold.py", str(exc)))
    try:
        foldmap = audit_fold_map(root_path, revision="rev0045", artifact_stem=artifact_stem)
        foldmap_status = foldmap.status
        if foldmap.error_count:
            findings.append(BridgeEpochFoldFinding("error", "foldmap_failed", "src/i2p_dht_lab/foldmap.py", "rev0045 foldmap failed"))
    except Exception as exc:  # pragma: no cover
        foldmap_status = "exception"
        findings.append(BridgeEpochFoldFinding("error", "foldmap_exception", "src/i2p_dht_lab/foldmap.py", str(exc)))
    try:
        registry = audit_fold_registry(root_path, revision="rev0045")
        registry_status = registry.status
        if registry.error_count:
            findings.append(BridgeEpochFoldFinding("error", "foldregistry_failed", "src/i2p_dht_lab/foldregistry.py", "rev0045 registry failed"))
    except Exception as exc:  # pragma: no cover
        registry_status = "exception"
        findings.append(BridgeEpochFoldFinding("error", "foldregistry_exception", "src/i2p_dht_lab/foldregistry.py", str(exc)))
    try:
        ledger = audit_surface_ledger(root_path, entries_for_revision("rev0045"))
        surface_status = "pass" if ledger.ok else "fail"
        if ledger.error_count:
            findings.append(BridgeEpochFoldFinding("error", "surface_ledger_failed", "src/i2p_dht_lab/surfaceledger.py", "rev0045 surface ledger failed"))
    except Exception as exc:  # pragma: no cover
        surface_status = "exception"
        findings.append(BridgeEpochFoldFinding("error", "surface_ledger_exception", "src/i2p_dht_lab/surfaceledger.py", str(exc)))
    status = "pass" if not any(finding.severity == "error" for finding in findings) else "fail"
    digest = sha256(BRIDGE_EPOCH_FOLD_DOMAIN + b":report:" + bencode({
        b"revision": revision,
        b"artifact": artifact_stem,
        b"status": status,
        b"predecessor": predecessor_status,
        b"foldmap": foldmap_status,
        b"registry": registry_status,
        b"surface": surface_status,
        b"findings": [finding.bvalue() for finding in findings],
    }))
    return BridgeEpochFoldReport(revision, artifact_stem, status, predecessor_status, foldmap_status, registry_status, surface_status, tuple(findings), digest)
