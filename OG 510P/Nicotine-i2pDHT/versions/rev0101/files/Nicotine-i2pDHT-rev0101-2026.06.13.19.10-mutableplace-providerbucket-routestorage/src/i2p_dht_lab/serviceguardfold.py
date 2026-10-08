"""rev0037 service announcement/ingress fold audit.

This is a folded branchlet that pressures public service announcements and
inbound ingress before work reaches the ticket lane.  It shares rev0037 with the
ticket/receipt surfaces and uses the same foldregistry/current-surface spine.
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

SERVICE_GUARD_FOLD_DOMAIN = DOMAIN + b":service-guard-fold-v1:"


@dataclass(frozen=True)
class ServiceGuardFoldFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class ServiceGuardFoldReport:
    revision: str
    artifact_stem: str
    status: str
    predecessor_status: str
    foldmap_status: str
    registry_status: str
    surface_ledger_status: str
    findings: tuple[ServiceGuardFoldFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")


REV0037_GUARD_PATHS = (
    "src/i2p_dht_lab/serviceannounce.py",
    "src/i2p_dht_lab/ingressgate.py",
    "src/i2p_dht_lab/serviceguardfold.py",
    "tests/test_rev0037_serviceannounce_ingressgate_registryfold.py",
    "docs/380-service-announcement-redaction.md",
    "docs/381-ingress-gate-announcement-pressure.md",
    "docs/382-serviceguardfold-branchlet.md",
)
NEEDLES = ("serviceannounce", "ingressgate", "serviceguardfold")


def _contains(path: Path, needle: str) -> bool:
    try:
        return needle in path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return False


def audit_serviceguard_fold(root: str | Path, *, revision: str = "rev0037", artifact_stem: str | None = None) -> ServiceGuardFoldReport:
    if revision != "rev0037":
        raise ValueError("serviceguardfold currently audits rev0037")
    root_path = Path(root)
    artifact_stem = artifact_stem or root_path.name
    findings: list[ServiceGuardFoldFinding] = []
    for rel in REV0037_GUARD_PATHS:
        if not (root_path / rel).exists():
            findings.append(ServiceGuardFoldFinding("error", "missing_guard_path", rel, "rev0037 guard path is absent"))
    for surface_path in ("PUBLIC_SURFACE.json", "HEAD_REGISTRY.json", "docs/00-index.md"):
        for needle in NEEDLES:
            if not _contains(root_path / surface_path, needle):
                findings.append(ServiceGuardFoldFinding("error", "surface_missing_guard_needle", surface_path, f"missing {needle}"))
    try:
        predecessor = audit_service_fold(root_path, revision="rev0036", artifact_stem=artifact_stem)
        predecessor_status = predecessor.status
        if predecessor.error_count:
            findings.append(ServiceGuardFoldFinding("error", "predecessor_servicefold_failed", "src/i2p_dht_lab/servicefold.py", "rev0036 servicefold predecessor failed"))
    except Exception as exc:  # pragma: no cover
        predecessor_status = "exception"
        findings.append(ServiceGuardFoldFinding("error", "predecessor_servicefold_exception", "src/i2p_dht_lab/servicefold.py", str(exc)))
    try:
        foldmap = audit_fold_map(root_path, revision="rev0037", artifact_stem=artifact_stem)
        foldmap_status = foldmap.status
        if foldmap.error_count:
            findings.append(ServiceGuardFoldFinding("error", "foldmap_failed", "src/i2p_dht_lab/foldmap.py", "rev0037 foldmap failed"))
    except Exception as exc:  # pragma: no cover
        foldmap_status = "exception"
        findings.append(ServiceGuardFoldFinding("error", "foldmap_exception", "src/i2p_dht_lab/foldmap.py", str(exc)))
    try:
        registry = audit_fold_registry(root_path, revision="rev0037")
        registry_status = registry.status
        if registry.error_count:
            findings.append(ServiceGuardFoldFinding("error", "foldregistry_failed", "src/i2p_dht_lab/foldregistry.py", "rev0037 fold registry failed"))
    except Exception as exc:  # pragma: no cover
        registry_status = "exception"
        findings.append(ServiceGuardFoldFinding("error", "foldregistry_exception", "src/i2p_dht_lab/foldregistry.py", str(exc)))
    try:
        ledger = audit_surface_ledger(root_path, entries_for_revision(revision))
        surface_status = "pass" if ledger.ok else "fail"
        if ledger.error_count:
            findings.append(ServiceGuardFoldFinding("error", "surface_ledger_failed", "src/i2p_dht_lab/surfaceledger.py", "rev0037 surface ledger failed"))
    except Exception as exc:  # pragma: no cover
        surface_status = "exception"
        findings.append(ServiceGuardFoldFinding("error", "surface_ledger_exception", "src/i2p_dht_lab/surfaceledger.py", str(exc)))
    status = "pass" if not any(f.severity == "error" for f in findings) else "fail"
    digest = sha256(SERVICE_GUARD_FOLD_DOMAIN + b":report:" + bencode({
        b"revision": revision,
        b"artifact": artifact_stem,
        b"status": status,
        b"predecessor_status": predecessor_status,
        b"foldmap_status": foldmap_status,
        b"registry_status": registry_status,
        b"surface_status": surface_status,
        b"findings": [finding.bvalue() for finding in findings],
    }))
    return ServiceGuardFoldReport(revision, artifact_stem, status, predecessor_status, foldmap_status, registry_status, surface_status, tuple(findings), digest)
