"""rev0058 audit/refactor fold for finality, retry escrow, and prune guard."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .foldmap import audit_fold_map
from .foldregistry import audit_fold_registry
from .ids import DOMAIN, sha256
from .reconcilefold import audit_reconcile_fold
from .surfaceledger import audit_surface_ledger, entries_for_revision

FINALITY_FOLD_DOMAIN = DOMAIN + b":finality-fold-v1:"


@dataclass(frozen=True)
class FinalityFoldFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class FinalityFoldReport:
    revision: str
    artifact_stem: str
    status: str
    reconcile_predecessor_status: str
    foldmap_status: str
    foldregistry_status: str
    surface_ledger_status: str
    findings: tuple[FinalityFoldFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")


def _exists(root: Path, rel: str, findings: list[FinalityFoldFinding]) -> None:
    if not (root / rel).exists():
        findings.append(FinalityFoldFinding("error", "missing_path", rel, "rev0058 finality fold expected this path"))


def audit_finality_fold(root: str | Path, *, revision: str = "rev0058", artifact_stem: str = "") -> FinalityFoldReport:
    root_path = Path(root)
    artifact = artifact_stem or root_path.name
    findings: list[FinalityFoldFinding] = []
    for rel in (
        "src/i2p_dht_lab/finalityledger.py",
        "src/i2p_dht_lab/retryescrow.py",
        "src/i2p_dht_lab/pruneguard.py",
        "src/i2p_dht_lab/finalityfold.py",
        "tests/test_rev0058_finality_retryescrow_pruneguard.py",
        "docs/610-rev0058-finalityledger-retryescrow-pruneguard.md",
        "docs/611-finality-ledger-after-reconcile.md",
        "docs/612-retry-escrow-deadletter-carry.md",
        "docs/613-prune-guard-terminal-pending.md",
        "docs/614-finalityfold-audit-refactor.md",
    ):
        _exists(root_path, rel, findings)
    try:
        predecessor = audit_reconcile_fold(root_path, revision="rev0057", artifact_stem=artifact)
        reconcile_status = predecessor.status
        if predecessor.error_count:
            findings.append(FinalityFoldFinding("error", "reconcile_predecessor_failed", "src/i2p_dht_lab/reconcilefold.py", "rev0057 predecessor fold failed"))
    except Exception as exc:  # pragma: no cover
        reconcile_status = "exception"
        findings.append(FinalityFoldFinding("error", "reconcile_predecessor_exception", "src/i2p_dht_lab/reconcilefold.py", str(exc)))
    try:
        fmap = audit_fold_map(root_path, revision=revision, artifact_stem=artifact)
        foldmap_status = fmap.status
        if fmap.error_count:
            findings.append(FinalityFoldFinding("error", "foldmap_failed", "src/i2p_dht_lab/foldmap.py", "rev0058 fold map failed"))
    except Exception as exc:  # pragma: no cover
        foldmap_status = "exception"
        findings.append(FinalityFoldFinding("error", "foldmap_exception", "src/i2p_dht_lab/foldmap.py", str(exc)))
    try:
        registry = audit_fold_registry(root_path, revision=revision)
        foldregistry_status = registry.status
        if registry.error_count:
            findings.append(FinalityFoldFinding("error", "foldregistry_failed", "src/i2p_dht_lab/foldregistry.py", "rev0058 fold registry failed"))
    except Exception as exc:  # pragma: no cover
        foldregistry_status = "exception"
        findings.append(FinalityFoldFinding("error", "foldregistry_exception", "src/i2p_dht_lab/foldregistry.py", str(exc)))
    try:
        ledger = audit_surface_ledger(root_path, entries_for_revision(revision))
        surface_status = "pass" if ledger.ok else "fail"
        if ledger.error_count:
            findings.append(FinalityFoldFinding("error", "surface_ledger_failed", "src/i2p_dht_lab/surfaceledger.py", "rev0058 surface ledger failed"))
    except Exception as exc:  # pragma: no cover
        surface_status = "exception"
        findings.append(FinalityFoldFinding("error", "surface_ledger_exception", "src/i2p_dht_lab/surfaceledger.py", str(exc)))
    status = "pass" if not any(finding.severity == "error" for finding in findings) else "fail"
    digest = sha256(FINALITY_FOLD_DOMAIN + b":report:" + bencode({
        b"revision": revision,
        b"artifact": artifact,
        b"status": status,
        b"reconcile": reconcile_status,
        b"foldmap": foldmap_status,
        b"foldregistry": foldregistry_status,
        b"surface": surface_status,
        b"findings": [finding.bvalue() for finding in findings],
    }))
    return FinalityFoldReport(revision, artifact, status, reconcile_status, foldmap_status, foldregistry_status, surface_status, tuple(findings), digest)
