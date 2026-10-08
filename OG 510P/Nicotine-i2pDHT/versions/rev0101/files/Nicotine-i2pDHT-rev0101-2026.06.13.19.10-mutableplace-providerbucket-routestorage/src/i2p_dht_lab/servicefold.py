"""rev0036 service/start fold audit.

This fold pins servicecatalog, loadsheath, profilegc, foldregistry, and this
servicefold audit while preserving rev0035 startfold as predecessor history.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .foldmap import audit_fold_map
from .foldregistry import audit_fold_registry
from .ids import DOMAIN, sha256
from .startfold import audit_start_fold
from .surfaceledger import audit_surface_ledger, entries_for_revision

SERVICE_FOLD_DOMAIN = DOMAIN + b":service-fold-v1:"


@dataclass(frozen=True)
class ServiceFoldFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class ServiceFoldReport:
    revision: str
    artifact_stem: str
    status: str
    predecessor_status: str
    foldmap_status: str
    registry_status: str
    surface_ledger_status: str
    findings: tuple[ServiceFoldFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")


REV0036_PATHS = (
    "src/i2p_dht_lab/servicecatalog.py",
    "src/i2p_dht_lab/loadsheath.py",
    "src/i2p_dht_lab/profilegc.py",
    "src/i2p_dht_lab/foldregistry.py",
    "src/i2p_dht_lab/servicefold.py",
    "tests/test_rev0036_servicecatalog_loadsheath_profilegc.py",
    "docs/360-rev0036-servicecatalog-loadsheath-profilegc.md",
    "docs/361-service-catalog-capsules.md",
    "docs/362-load-sheath-useful-refusal-profiles.md",
    "docs/363-profile-gc-config-change-pressure.md",
    "docs/364-foldregistry-servicefold-audit.md",
)
NEEDLES = ("rev0036", "servicecatalog", "loadsheath", "profilegc", "foldregistry", "servicefold")


def _contains(path: Path, needle: str) -> bool:
    try:
        return needle in path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return False


def audit_service_fold(root: str | Path, *, revision: str = "rev0036", artifact_stem: str | None = None) -> ServiceFoldReport:
    if revision != "rev0036":
        raise ValueError("servicefold currently audits the rev0036 active path")
    root_path = Path(root)
    artifact_stem = artifact_stem or root_path.name
    findings: list[ServiceFoldFinding] = []
    for rel in REV0036_PATHS:
        if not (root_path / rel).exists():
            findings.append(ServiceFoldFinding("error", "missing_rev0036_path", rel, "rev0036 active path is absent"))
    for surface_path in ("PUBLIC_SURFACE.json", "HEAD_REGISTRY.json", "docs/00-index.md"):
        for needle in NEEDLES:
            if not _contains(root_path / surface_path, needle):
                findings.append(ServiceFoldFinding("error", "surface_missing_needle", surface_path, f"missing {needle}"))
    try:
        predecessor = audit_start_fold(root_path, revision="rev0035", artifact_stem=artifact_stem)
        predecessor_status = predecessor.status
        if predecessor.error_count:
            findings.append(ServiceFoldFinding("error", "predecessor_startfold_failed", "src/i2p_dht_lab/startfold.py", "rev0035 startfold predecessor failed"))
    except Exception as exc:  # pragma: no cover
        predecessor_status = "exception"
        findings.append(ServiceFoldFinding("error", "predecessor_startfold_exception", "src/i2p_dht_lab/startfold.py", str(exc)))
    try:
        foldmap = audit_fold_map(root_path, revision="rev0036", artifact_stem=artifact_stem)
        foldmap_status = foldmap.status
        if foldmap.error_count:
            findings.append(ServiceFoldFinding("error", "foldmap_failed", "src/i2p_dht_lab/foldmap.py", "rev0036 foldmap failed"))
    except Exception as exc:  # pragma: no cover
        foldmap_status = "exception"
        findings.append(ServiceFoldFinding("error", "foldmap_exception", "src/i2p_dht_lab/foldmap.py", str(exc)))
    try:
        registry = audit_fold_registry(root_path, revision="rev0036")
        registry_status = registry.status
        if registry.error_count:
            findings.append(ServiceFoldFinding("error", "foldregistry_failed", "src/i2p_dht_lab/foldregistry.py", "rev0036 fold registry failed"))
    except Exception as exc:  # pragma: no cover
        registry_status = "exception"
        findings.append(ServiceFoldFinding("error", "foldregistry_exception", "src/i2p_dht_lab/foldregistry.py", str(exc)))
    try:
        ledger = audit_surface_ledger(root_path, entries_for_revision(revision))
        surface_status = "pass" if ledger.ok else "fail"
        if ledger.error_count:
            findings.append(ServiceFoldFinding("error", "surface_ledger_failed", "src/i2p_dht_lab/surfaceledger.py", "rev0036 surface ledger failed"))
    except Exception as exc:  # pragma: no cover
        surface_status = "exception"
        findings.append(ServiceFoldFinding("error", "surface_ledger_exception", "src/i2p_dht_lab/surfaceledger.py", str(exc)))
    status = "pass" if not any(item.severity == "error" for item in findings) else "fail"
    digest = sha256(SERVICE_FOLD_DOMAIN + b":report:" + bencode({
        b"revision": revision,
        b"artifact": artifact_stem,
        b"status": status,
        b"predecessor_status": predecessor_status,
        b"foldmap_status": foldmap_status,
        b"registry_status": registry_status,
        b"surface_status": surface_status,
        b"findings": [finding.bvalue() for finding in findings],
    }))
    return ServiceFoldReport(revision, artifact_stem, status, predecessor_status, foldmap_status, registry_status, surface_status, tuple(findings), digest)
