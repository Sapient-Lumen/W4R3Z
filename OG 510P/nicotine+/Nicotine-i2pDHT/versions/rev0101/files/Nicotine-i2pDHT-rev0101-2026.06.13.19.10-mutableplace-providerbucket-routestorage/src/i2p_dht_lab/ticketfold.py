"""rev0037 ticket/receipt fold audit.

This fold pins serviceticket, servicereceipt, and ticketfold while preserving
rev0036 servicefold as predecessor history and using the declarative fold
registry introduced in rev0036.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .foldmap import audit_fold_map
from .foldregistry import audit_fold_registry
from .ids import DOMAIN, sha256
from .servicefold import audit_service_fold
from .surfaceledger import audit_surface_ledger, entries_for_revision

TICKET_FOLD_DOMAIN = DOMAIN + b":ticket-fold-v1:"


@dataclass(frozen=True)
class TicketFoldFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class TicketFoldReport:
    revision: str
    artifact_stem: str
    status: str
    predecessor_status: str
    foldmap_status: str
    registry_status: str
    surface_ledger_status: str
    findings: tuple[TicketFoldFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")


REV0037_PATHS = (
    "src/i2p_dht_lab/serviceticket.py",
    "src/i2p_dht_lab/servicereceipt.py",
    "src/i2p_dht_lab/ticketfold.py",
    "tests/test_rev0037_service_ticket_receipt_fold.py",
    "docs/371-rev0037-ticketlane-servicereceipt-registryfold.md",
    "docs/372-service-ticket-exact-scope-grants.md",
    "docs/373-service-receipts-and-refusal-loops.md",
    "docs/374-ticketfold-audit-refactor.md",
)
NEEDLES = ("rev0037", "serviceticket", "servicereceipt", "ticketfold")


def _contains(path: Path, needle: str) -> bool:
    try:
        return needle in path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return False


def audit_ticket_fold(root: str | Path, *, revision: str = "rev0037", artifact_stem: str | None = None) -> TicketFoldReport:
    if revision != "rev0037":
        raise ValueError("ticketfold currently audits the rev0037 active path")
    root_path = Path(root)
    artifact_stem = artifact_stem or root_path.name
    findings: list[TicketFoldFinding] = []
    for rel in REV0037_PATHS:
        if not (root_path / rel).exists():
            findings.append(TicketFoldFinding("error", "missing_rev0037_path", rel, "rev0037 active path is absent"))
    for surface_path in ("PUBLIC_SURFACE.json", "HEAD_REGISTRY.json", "docs/00-index.md"):
        for needle in NEEDLES:
            if not _contains(root_path / surface_path, needle):
                findings.append(TicketFoldFinding("error", "surface_missing_needle", surface_path, f"missing {needle}"))
    try:
        predecessor = audit_service_fold(root_path, revision="rev0036", artifact_stem=artifact_stem)
        predecessor_status = predecessor.status
        if predecessor.error_count:
            findings.append(TicketFoldFinding("error", "predecessor_servicefold_failed", "src/i2p_dht_lab/servicefold.py", "rev0036 servicefold predecessor failed"))
    except Exception as exc:  # pragma: no cover
        predecessor_status = "exception"
        findings.append(TicketFoldFinding("error", "predecessor_servicefold_exception", "src/i2p_dht_lab/servicefold.py", str(exc)))
    try:
        foldmap = audit_fold_map(root_path, revision="rev0037", artifact_stem=artifact_stem)
        foldmap_status = foldmap.status
        if foldmap.error_count:
            findings.append(TicketFoldFinding("error", "foldmap_failed", "src/i2p_dht_lab/foldmap.py", "rev0037 foldmap failed"))
    except Exception as exc:  # pragma: no cover
        foldmap_status = "exception"
        findings.append(TicketFoldFinding("error", "foldmap_exception", "src/i2p_dht_lab/foldmap.py", str(exc)))
    try:
        registry = audit_fold_registry(root_path, revision="rev0037")
        registry_status = registry.status
        if registry.error_count:
            findings.append(TicketFoldFinding("error", "foldregistry_failed", "src/i2p_dht_lab/foldregistry.py", "rev0037 fold registry failed"))
    except Exception as exc:  # pragma: no cover
        registry_status = "exception"
        findings.append(TicketFoldFinding("error", "foldregistry_exception", "src/i2p_dht_lab/foldregistry.py", str(exc)))
    try:
        ledger = audit_surface_ledger(root_path, entries_for_revision(revision))
        surface_status = "pass" if ledger.ok else "fail"
        if ledger.error_count:
            findings.append(TicketFoldFinding("error", "surface_ledger_failed", "src/i2p_dht_lab/surfaceledger.py", "rev0037 surface ledger failed"))
    except Exception as exc:  # pragma: no cover
        surface_status = "exception"
        findings.append(TicketFoldFinding("error", "surface_ledger_exception", "src/i2p_dht_lab/surfaceledger.py", str(exc)))
    status = "pass" if not any(item.severity == "error" for item in findings) else "fail"
    digest = sha256(TICKET_FOLD_DOMAIN + b":report:" + bencode({
        b"revision": revision,
        b"artifact": artifact_stem,
        b"status": status,
        b"predecessor_status": predecessor_status,
        b"foldmap_status": foldmap_status,
        b"registry_status": registry_status,
        b"surface_status": surface_status,
        b"findings": [finding.bvalue() for finding in findings],
    }))
    return TicketFoldReport(revision, artifact_stem, status, predecessor_status, foldmap_status, registry_status, surface_status, tuple(findings), digest)
