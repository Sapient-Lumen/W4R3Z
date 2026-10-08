"""rev0048 bridge-shadow / audit-quorum / redress-GC fold audit."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .foldmap import audit_fold_map
from .foldregistry import audit_fold_registry
from .ids import DOMAIN, sha256
from .publicationfold import audit_publication_fold
from .surfaceledger import audit_surface_ledger, entries_for_revision

BRIDGE_GOVERNANCE_FOLD_DOMAIN = DOMAIN + b":bridge-governance-fold-v1:"


@dataclass(frozen=True)
class BridgeGovernanceFoldFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class BridgeGovernanceFoldReport:
    revision: str
    artifact_stem: str
    status: str
    predecessor_status: str
    foldmap_status: str
    registry_status: str
    surface_ledger_status: str
    findings: tuple[BridgeGovernanceFoldFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")


REV0048_PATHS = (
    "src/i2p_dht_lab/bridgeshadow.py",
    "src/i2p_dht_lab/auditquorum.py",
    "src/i2p_dht_lab/redressgc.py",
    "src/i2p_dht_lab/bridgegovernancefold.py",
    "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py",
    "docs/505-rev0048-bridgeshadow-auditquorum-redressgc.md",
    "docs/506-bridge-shadow-publication-side-effect.md",
    "docs/507-audit-quorum-local-evidence.md",
    "docs/508-redress-gc-retention-boundary.md",
    "docs/509-shadowauditfold-audit-refactor.md",
)
NEEDLES = ("rev0048", "bridgeshadow", "auditquorum", "redressgc", "bridgegovernancefold")


def _contains(path: Path, needle: str) -> bool:
    try:
        return needle in path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return False


def audit_bridge_governance_fold(root: str | Path, *, revision: str = "rev0048", artifact_stem: str | None = None) -> BridgeGovernanceFoldReport:
    if revision != "rev0048":
        raise ValueError("bridgegovernancefold currently audits rev0048")
    root_path = Path(root)
    artifact_stem = artifact_stem or root_path.name
    findings: list[BridgeGovernanceFoldFinding] = []
    for rel in REV0048_PATHS:
        if not (root_path / rel).exists():
            findings.append(BridgeGovernanceFoldFinding("error", "missing_rev0048_path", rel, "rev0048 bridge-governance path is absent"))
    for surface_path in ("PUBLIC_SURFACE.json", "HEAD_REGISTRY.json", "docs/00-index.md"):
        for needle in NEEDLES:
            if not _contains(root_path / surface_path, needle):
                findings.append(BridgeGovernanceFoldFinding("error", "surface_missing_needle", surface_path, f"missing {needle}"))
    try:
        predecessor = audit_publication_fold(root_path, revision="rev0047", artifact_stem=artifact_stem)
        predecessor_status = predecessor.status
        if predecessor.error_count:
            findings.append(BridgeGovernanceFoldFinding("error", "publicationfold_failed", "src/i2p_dht_lab/publicationfold.py", "rev0047 predecessor fold failed"))
    except Exception as exc:  # pragma: no cover
        predecessor_status = "exception"
        findings.append(BridgeGovernanceFoldFinding("error", "publicationfold_exception", "src/i2p_dht_lab/publicationfold.py", str(exc)))
    try:
        foldmap = audit_fold_map(root_path, revision="rev0048", artifact_stem=artifact_stem)
        foldmap_status = foldmap.status
        if foldmap.error_count:
            findings.append(BridgeGovernanceFoldFinding("error", "foldmap_failed", "src/i2p_dht_lab/foldmap.py", "rev0048 foldmap failed"))
    except Exception as exc:  # pragma: no cover
        foldmap_status = "exception"
        findings.append(BridgeGovernanceFoldFinding("error", "foldmap_exception", "src/i2p_dht_lab/foldmap.py", str(exc)))
    try:
        registry = audit_fold_registry(root_path, revision="rev0048")
        registry_status = registry.status
        if registry.error_count:
            findings.append(BridgeGovernanceFoldFinding("error", "foldregistry_failed", "src/i2p_dht_lab/foldregistry.py", "rev0048 registry failed"))
    except Exception as exc:  # pragma: no cover
        registry_status = "exception"
        findings.append(BridgeGovernanceFoldFinding("error", "foldregistry_exception", "src/i2p_dht_lab/foldregistry.py", str(exc)))
    try:
        ledger = audit_surface_ledger(root_path, entries_for_revision("rev0048"))
        surface_ledger_status = "pass" if ledger.ok else "fail"
        if ledger.error_count:
            findings.append(BridgeGovernanceFoldFinding("error", "surface_ledger_failed", "src/i2p_dht_lab/surfaceledger.py", "rev0048 surface ledger failed"))
    except Exception as exc:  # pragma: no cover
        surface_ledger_status = "exception"
        findings.append(BridgeGovernanceFoldFinding("error", "surface_ledger_exception", "src/i2p_dht_lab/surfaceledger.py", str(exc)))
    status = "pass" if not any(finding.severity == "error" for finding in findings) else "fail"
    digest = sha256(BRIDGE_GOVERNANCE_FOLD_DOMAIN + b":report:" + bencode({
        b"revision": revision,
        b"artifact": artifact_stem,
        b"status": status,
        b"predecessor": predecessor_status,
        b"foldmap": foldmap_status,
        b"registry": registry_status,
        b"surface": surface_ledger_status,
        b"findings": [finding.bvalue() for finding in findings],
    }))
    return BridgeGovernanceFoldReport(revision, artifact_stem, status, predecessor_status, foldmap_status, registry_status, surface_ledger_status, tuple(findings), digest)
