"""rev0038 service-continuity fold audit.

This fold absorbs the rev0037 service branchlets that were useful but split:
wire catalogs, probes, withdrawals, relays, use gates, handoff, veiled receipts,
and the final ticket/announcement lanes.  The audit is intentionally boring:
current paths must be reachable from code, tests, docs, public pointers, the
fold registry, and the active surface ledger.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .foldmap import audit_fold_map
from .foldregistry import audit_fold_registry
from .ids import DOMAIN, sha256
from .serviceguardfold import audit_serviceguard_fold
from .ticketfold import audit_ticket_fold
from .surfaceledger import audit_surface_ledger, entries_for_revision

SERVICE_CONTINUITY_FOLD_DOMAIN = DOMAIN + b":service-continuity-fold-v1:"


@dataclass(frozen=True)
class ServiceContinuityFoldFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class ServiceContinuityFoldReport:
    revision: str
    artifact_stem: str
    status: str
    ticketfold_status: str
    serviceguard_status: str
    foldmap_status: str
    registry_status: str
    surface_ledger_status: str
    findings: tuple[ServiceContinuityFoldFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")


REV0038_PATHS = (
    "src/i2p_dht_lab/catalogwire.py",
    "src/i2p_dht_lab/serviceprobe.py",
    "src/i2p_dht_lab/profilegcjoin.py",
    "src/i2p_dht_lab/catalogsuccession.py",
    "src/i2p_dht_lab/servicewithdrawal.py",
    "src/i2p_dht_lab/servicerelay.py",
    "src/i2p_dht_lab/serviceusegate.py",
    "src/i2p_dht_lab/handofflane.py",
    "src/i2p_dht_lab/receiptveil.py",
    "src/i2p_dht_lab/servicecontinuity.py",
    "src/i2p_dht_lab/servicecontinuityfold.py",
    "tests/test_rev0038_servicecontinuity_branchfold.py",
    "docs/383-rev0038-servicecontinuity-branchfold.md",
    "docs/384-service-continuity-joined-boundary.md",
    "docs/385-branchlet-fold-service-surfaces.md",
    "docs/386-profile-gc-catalog-succession-joins.md",
    "docs/387-servicecontinuityfold-audit-refactor.md",
)
NEEDLES = (
    "rev0038",
    "servicecontinuity",
    "servicecontinuityfold",
    "catalogwire",
    "serviceprobe",
    "servicewithdrawal",
    "servicerelay",
    "serviceusegate",
    "handofflane",
    "receiptveil",
)


def _contains(path: Path, needle: str) -> bool:
    try:
        return needle in path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return False


def audit_servicecontinuity_fold(root: str | Path, *, revision: str = "rev0038", artifact_stem: str | None = None) -> ServiceContinuityFoldReport:
    if revision != "rev0038":
        raise ValueError("servicecontinuityfold currently audits rev0038")
    root_path = Path(root)
    artifact_stem = artifact_stem or root_path.name
    findings: list[ServiceContinuityFoldFinding] = []
    for rel in REV0038_PATHS:
        if not (root_path / rel).exists():
            findings.append(ServiceContinuityFoldFinding("error", "missing_rev0038_path", rel, "rev0038 service-continuity path is absent"))
    for surface_path in ("PUBLIC_SURFACE.json", "HEAD_REGISTRY.json", "docs/00-index.md"):
        for needle in NEEDLES:
            if not _contains(root_path / surface_path, needle):
                findings.append(ServiceContinuityFoldFinding("error", "surface_missing_needle", surface_path, f"missing {needle}"))
    try:
        ticket = audit_ticket_fold(root_path, revision="rev0037", artifact_stem=artifact_stem)
        ticket_status = ticket.status
        if ticket.error_count:
            findings.append(ServiceContinuityFoldFinding("error", "ticketfold_failed", "src/i2p_dht_lab/ticketfold.py", "rev0037 ticketfold predecessor failed"))
    except Exception as exc:  # pragma: no cover
        ticket_status = "exception"
        findings.append(ServiceContinuityFoldFinding("error", "ticketfold_exception", "src/i2p_dht_lab/ticketfold.py", str(exc)))
    try:
        guard = audit_serviceguard_fold(root_path, revision="rev0037", artifact_stem=artifact_stem)
        guard_status = guard.status
        if guard.error_count:
            findings.append(ServiceContinuityFoldFinding("error", "serviceguard_failed", "src/i2p_dht_lab/serviceguardfold.py", "rev0037 serviceguard predecessor failed"))
    except Exception as exc:  # pragma: no cover
        guard_status = "exception"
        findings.append(ServiceContinuityFoldFinding("error", "serviceguard_exception", "src/i2p_dht_lab/serviceguardfold.py", str(exc)))
    try:
        foldmap = audit_fold_map(root_path, revision="rev0038", artifact_stem=artifact_stem)
        foldmap_status = foldmap.status
        if foldmap.error_count:
            findings.append(ServiceContinuityFoldFinding("error", "foldmap_failed", "src/i2p_dht_lab/foldmap.py", "rev0038 foldmap failed"))
    except Exception as exc:  # pragma: no cover
        foldmap_status = "exception"
        findings.append(ServiceContinuityFoldFinding("error", "foldmap_exception", "src/i2p_dht_lab/foldmap.py", str(exc)))
    try:
        registry = audit_fold_registry(root_path, revision="rev0038")
        registry_status = registry.status
        if registry.error_count:
            findings.append(ServiceContinuityFoldFinding("error", "foldregistry_failed", "src/i2p_dht_lab/foldregistry.py", "rev0038 fold registry failed"))
    except Exception as exc:  # pragma: no cover
        registry_status = "exception"
        findings.append(ServiceContinuityFoldFinding("error", "foldregistry_exception", "src/i2p_dht_lab/foldregistry.py", str(exc)))
    try:
        ledger = audit_surface_ledger(root_path, entries_for_revision(revision))
        surface_status = "pass" if ledger.ok else "fail"
        if ledger.error_count:
            findings.append(ServiceContinuityFoldFinding("error", "surface_ledger_failed", "src/i2p_dht_lab/surfaceledger.py", "rev0038 surface ledger failed"))
    except Exception as exc:  # pragma: no cover
        surface_status = "exception"
        findings.append(ServiceContinuityFoldFinding("error", "surface_ledger_exception", "src/i2p_dht_lab/surfaceledger.py", str(exc)))
    status = "pass" if not any(finding.severity == "error" for finding in findings) else "fail"
    digest = sha256(SERVICE_CONTINUITY_FOLD_DOMAIN + b":report:" + bencode({
        b"revision": revision,
        b"artifact": artifact_stem,
        b"status": status,
        b"ticketfold_status": ticket_status,
        b"serviceguard_status": guard_status,
        b"foldmap_status": foldmap_status,
        b"registry_status": registry_status,
        b"surface_status": surface_status,
        b"findings": [finding.bvalue() for finding in findings],
    }))
    return ServiceContinuityFoldReport(revision, artifact_stem, status, ticket_status, guard_status, foldmap_status, registry_status, surface_status, tuple(findings), digest)
