"""rev0056 audit/refactor fold for recovery mesh, safe cleanup, and chaos budget."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .foldmap import audit_fold_map
from .foldregistry import audit_fold_registry
from .ids import DOMAIN, sha256
from .restartfold import audit_restart_fold
from .surfaceledger import audit_surface_ledger, entries_for_revision

RECOVERY_FOLD_DOMAIN = DOMAIN + b":recovery-fold-v1:"


@dataclass(frozen=True)
class RecoveryFoldFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class RecoveryFoldReport:
    revision: str
    artifact_stem: str
    status: str
    restart_predecessor_status: str
    foldmap_status: str
    foldregistry_status: str
    surface_ledger_status: str
    findings: tuple[RecoveryFoldFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")


def _exists(root: Path, rel: str, findings: list[RecoveryFoldFinding]) -> None:
    if not (root / rel).exists():
        findings.append(RecoveryFoldFinding("error", "missing_path", rel, "rev0056 recovery fold expected this path"))


def audit_recovery_fold(root: str | Path, *, revision: str = "rev0056", artifact_stem: str = "") -> RecoveryFoldReport:
    root_path = Path(root)
    artifact = artifact_stem or root_path.name
    findings: list[RecoveryFoldFinding] = []
    for rel in (
        "src/i2p_dht_lab/recoverymesh.py",
        "src/i2p_dht_lab/safecleanup.py",
        "src/i2p_dht_lab/chaosbudget.py",
        "src/i2p_dht_lab/recoveryfold.py",
        "tests/test_rev0056_recovery_cleanup_chaosbudget.py",
        "docs/590-rev0056-recoverymesh-safecleanup-chaosbudget.md",
        "docs/591-recovery-mesh-after-effect-seal.md",
        "docs/592-safe-cleanup-hard-negative-boundary.md",
        "docs/593-chaos-budget-post-effect-pressure.md",
        "docs/594-recoveryfold-audit-refactor.md",
    ):
        _exists(root_path, rel, findings)
    try:
        predecessor = audit_restart_fold(root_path, revision="rev0055", artifact_stem=artifact)
        predecessor_status = predecessor.status
        if predecessor.error_count:
            findings.append(RecoveryFoldFinding("error", "restart_predecessor_failed", "src/i2p_dht_lab/restartfold.py", "rev0055 predecessor fold failed"))
    except Exception as exc:  # pragma: no cover
        predecessor_status = "exception"
        findings.append(RecoveryFoldFinding("error", "restart_predecessor_exception", "src/i2p_dht_lab/restartfold.py", str(exc)))
    try:
        fmap = audit_fold_map(root_path, revision=revision, artifact_stem=artifact)
        foldmap_status = fmap.status
        if fmap.error_count:
            findings.append(RecoveryFoldFinding("error", "foldmap_failed", "src/i2p_dht_lab/foldmap.py", "rev0056 fold map failed"))
    except Exception as exc:  # pragma: no cover
        foldmap_status = "exception"
        findings.append(RecoveryFoldFinding("error", "foldmap_exception", "src/i2p_dht_lab/foldmap.py", str(exc)))
    try:
        registry = audit_fold_registry(root_path, revision=revision)
        foldregistry_status = registry.status
        if registry.error_count:
            findings.append(RecoveryFoldFinding("error", "foldregistry_failed", "src/i2p_dht_lab/foldregistry.py", "rev0056 fold registry failed"))
    except Exception as exc:  # pragma: no cover
        foldregistry_status = "exception"
        findings.append(RecoveryFoldFinding("error", "foldregistry_exception", "src/i2p_dht_lab/foldregistry.py", str(exc)))
    try:
        ledger = audit_surface_ledger(root_path, entries_for_revision(revision))
        surface_ledger_status = "pass" if ledger.ok else "fail"
        if ledger.error_count:
            findings.append(RecoveryFoldFinding("error", "surface_ledger_failed", "src/i2p_dht_lab/surfaceledger.py", "rev0056 surface ledger failed"))
    except Exception as exc:  # pragma: no cover
        surface_ledger_status = "exception"
        findings.append(RecoveryFoldFinding("error", "surface_ledger_exception", "src/i2p_dht_lab/surfaceledger.py", str(exc)))
    status = "pass" if not any(finding.severity == "error" for finding in findings) else "fail"
    digest = sha256(RECOVERY_FOLD_DOMAIN + b":report:" + bencode({
        b"revision": revision,
        b"artifact": artifact,
        b"status": status,
        b"restart": predecessor_status,
        b"foldmap": foldmap_status,
        b"foldregistry": foldregistry_status,
        b"surface": surface_ledger_status,
        b"findings": [finding.bvalue() for finding in findings],
    }))
    return RecoveryFoldReport(revision, artifact, status, predecessor_status, foldmap_status, foldregistry_status, surface_ledger_status, tuple(findings), digest)
