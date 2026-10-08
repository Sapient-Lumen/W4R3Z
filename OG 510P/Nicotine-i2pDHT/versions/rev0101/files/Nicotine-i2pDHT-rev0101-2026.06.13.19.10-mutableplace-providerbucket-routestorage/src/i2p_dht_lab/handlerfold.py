"""rev0053 audit/refactor fold for handler capsules and side-effect journals."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .edgefold import audit_edge_fold
from .foldmap import audit_fold_map
from .foldregistry import audit_fold_registry
from .ids import DOMAIN, sha256
from .surfaceledger import audit_surface_ledger, entries_for_revision

HANDLER_FOLD_DOMAIN = DOMAIN + b":handler-fold-v1:"


@dataclass(frozen=True)
class HandlerFoldFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class HandlerFoldReport:
    revision: str
    artifact_stem: str
    status: str
    edge_predecessor_status: str
    foldmap_status: str
    foldregistry_status: str
    surface_ledger_status: str
    findings: tuple[HandlerFoldFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")


def _exists(root: Path, rel: str, findings: list[HandlerFoldFinding]) -> None:
    if not (root / rel).exists():
        findings.append(HandlerFoldFinding("error", "missing_path", rel, "rev0053 handler fold expected this path"))


def audit_handler_fold(root: str | Path, *, revision: str = "rev0053", artifact_stem: str = "") -> HandlerFoldReport:
    root_path = Path(root)
    artifact = artifact_stem or root_path.name
    findings: list[HandlerFoldFinding] = []
    for rel in (
        "src/i2p_dht_lab/handlercapsule.py",
        "src/i2p_dht_lab/sideeffectjournal.py",
        "src/i2p_dht_lab/adapterfuzz.py",
        "src/i2p_dht_lab/handlerfold.py",
        "tests/test_rev0053_handlercapsule_sideeffect_adapterfuzz.py",
        "docs/559-rev0053-handlercapsule-sideeffectjournal-adapterfuzz.md",
        "docs/560-handler-capsule-boundary.md",
        "docs/561-side-effect-journal-boundary.md",
        "docs/562-adapter-fuzz-coverage.md",
        "docs/563-handlerfold-audit-refactor.md",
    ):
        _exists(root_path, rel, findings)
    try:
        predecessor = audit_edge_fold(root_path, revision="rev0052", artifact_stem=artifact)
        predecessor_status = predecessor.status
        if predecessor.error_count:
            findings.append(HandlerFoldFinding("error", "edge_predecessor_failed", "src/i2p_dht_lab/edgefold.py", "rev0052 predecessor fold failed"))
    except Exception as exc:  # pragma: no cover
        predecessor_status = "exception"
        findings.append(HandlerFoldFinding("error", "edge_predecessor_exception", "src/i2p_dht_lab/edgefold.py", str(exc)))
    try:
        fmap = audit_fold_map(root_path, revision=revision, artifact_stem=artifact)
        foldmap_status = fmap.status
        if fmap.error_count:
            findings.append(HandlerFoldFinding("error", "foldmap_failed", "src/i2p_dht_lab/foldmap.py", "rev0053 fold map failed"))
    except Exception as exc:  # pragma: no cover
        foldmap_status = "exception"
        findings.append(HandlerFoldFinding("error", "foldmap_exception", "src/i2p_dht_lab/foldmap.py", str(exc)))
    try:
        registry = audit_fold_registry(root_path, revision=revision)
        foldregistry_status = registry.status
        if registry.error_count:
            findings.append(HandlerFoldFinding("error", "foldregistry_failed", "src/i2p_dht_lab/foldregistry.py", "rev0053 fold registry failed"))
    except Exception as exc:  # pragma: no cover
        foldregistry_status = "exception"
        findings.append(HandlerFoldFinding("error", "foldregistry_exception", "src/i2p_dht_lab/foldregistry.py", str(exc)))
    try:
        ledger = audit_surface_ledger(root_path, entries_for_revision(revision))
        surface_ledger_status = "pass" if ledger.ok else "fail"
        if ledger.error_count:
            findings.append(HandlerFoldFinding("error", "surface_ledger_failed", "src/i2p_dht_lab/surfaceledger.py", "rev0053 surface ledger failed"))
    except Exception as exc:  # pragma: no cover
        surface_ledger_status = "exception"
        findings.append(HandlerFoldFinding("error", "surface_ledger_exception", "src/i2p_dht_lab/surfaceledger.py", str(exc)))
    status = "pass" if not any(finding.severity == "error" for finding in findings) else "fail"
    digest = sha256(HANDLER_FOLD_DOMAIN + b":report:" + bencode({
        b"revision": revision,
        b"artifact": artifact,
        b"status": status,
        b"edge": predecessor_status,
        b"foldmap": foldmap_status,
        b"foldregistry": foldregistry_status,
        b"surface": surface_ledger_status,
        b"findings": [finding.bvalue() for finding in findings],
    }))
    return HandlerFoldReport(revision, artifact, status, predecessor_status, foldmap_status, foldregistry_status, surface_ledger_status, tuple(findings), digest)
