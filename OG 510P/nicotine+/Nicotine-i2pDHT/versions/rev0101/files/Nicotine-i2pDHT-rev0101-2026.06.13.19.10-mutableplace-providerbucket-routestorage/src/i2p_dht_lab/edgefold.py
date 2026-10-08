"""rev0052 audit/refactor fold for live-adapter/profile-edge surfaces."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .foldmap import audit_fold_map
from .foldregistry import audit_fold_registry
from .ids import DOMAIN, sha256
from .redteamfold import audit_redteam_fold
from .surfaceledger import audit_surface_ledger, entries_for_revision

EDGE_FOLD_DOMAIN = DOMAIN + b":edge-fold-v1:"


@dataclass(frozen=True)
class EdgeFoldFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class EdgeFoldReport:
    revision: str
    artifact_stem: str
    status: str
    redteam_predecessor_status: str
    foldmap_status: str
    foldregistry_status: str
    surface_ledger_status: str
    findings: tuple[EdgeFoldFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")


def _exists(root: Path, rel: str, findings: list[EdgeFoldFinding]) -> None:
    if not (root / rel).exists():
        findings.append(EdgeFoldFinding("error", "missing_path", rel, "rev0052 edge fold expected this path"))


def audit_edge_fold(root: str | Path, *, revision: str = "rev0052", artifact_stem: str = "") -> EdgeFoldReport:
    root_path = Path(root)
    artifact = artifact_stem or root_path.name
    findings: list[EdgeFoldFinding] = []
    for rel in (
        "src/i2p_dht_lab/liveadapter.py",
        "src/i2p_dht_lab/backpressuremesh.py",
        "src/i2p_dht_lab/profileedge.py",
        "src/i2p_dht_lab/edgefold.py",
        "tests/test_rev0052_liveadapter_backpressure_profileedge.py",
        "docs/548-rev0052-liveadapter-backpressure-profileedge.md",
        "docs/549-live-adapter-no-network-boundary.md",
        "docs/550-backpressure-mesh-shared-edge.md",
        "docs/551-profile-edge-joined-boundary.md",
        "docs/552-edgefold-audit-refactor.md",
    ):
        _exists(root_path, rel, findings)
    try:
        redteam = audit_redteam_fold(root_path, revision="rev0051", artifact_stem=artifact)
        redteam_status = redteam.status
        if redteam.error_count:
            findings.append(EdgeFoldFinding("error", "redteam_predecessor_failed", "src/i2p_dht_lab/redteamfold.py", "rev0051 predecessor fold failed"))
    except Exception as exc:  # pragma: no cover
        redteam_status = "exception"
        findings.append(EdgeFoldFinding("error", "redteam_predecessor_exception", "src/i2p_dht_lab/redteamfold.py", str(exc)))
    try:
        fmap = audit_fold_map(root_path, revision=revision, artifact_stem=artifact)
        foldmap_status = fmap.status
        if fmap.error_count:
            findings.append(EdgeFoldFinding("error", "foldmap_failed", "src/i2p_dht_lab/foldmap.py", "rev0052 fold map failed"))
    except Exception as exc:  # pragma: no cover
        foldmap_status = "exception"
        findings.append(EdgeFoldFinding("error", "foldmap_exception", "src/i2p_dht_lab/foldmap.py", str(exc)))
    try:
        registry = audit_fold_registry(root_path, revision=revision)
        foldregistry_status = registry.status
        if registry.error_count:
            findings.append(EdgeFoldFinding("error", "foldregistry_failed", "src/i2p_dht_lab/foldregistry.py", "rev0052 fold registry failed"))
    except Exception as exc:  # pragma: no cover
        foldregistry_status = "exception"
        findings.append(EdgeFoldFinding("error", "foldregistry_exception", "src/i2p_dht_lab/foldregistry.py", str(exc)))
    try:
        ledger = audit_surface_ledger(root_path, entries_for_revision(revision))
        surface_ledger_status = "pass" if ledger.ok else "fail"
        if ledger.error_count:
            findings.append(EdgeFoldFinding("error", "surface_ledger_failed", "src/i2p_dht_lab/surfaceledger.py", "rev0052 surface ledger failed"))
    except Exception as exc:  # pragma: no cover
        surface_ledger_status = "exception"
        findings.append(EdgeFoldFinding("error", "surface_ledger_exception", "src/i2p_dht_lab/surfaceledger.py", str(exc)))
    status = "pass" if not any(finding.severity == "error" for finding in findings) else "fail"
    digest = sha256(EDGE_FOLD_DOMAIN + b":report:" + bencode({
        b"revision": revision,
        b"artifact": artifact,
        b"status": status,
        b"redteam": redteam_status,
        b"foldmap": foldmap_status,
        b"foldregistry": foldregistry_status,
        b"surface": surface_ledger_status,
        b"findings": [finding.bvalue() for finding in findings],
    }))
    return EdgeFoldReport(revision, artifact, status, redteam_status, foldmap_status, foldregistry_status, surface_ledger_status, tuple(findings), digest)
