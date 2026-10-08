"""rev0039 service-ops fold audit.

The cube is getting large enough that every new risk lane must prove it is not
hidden branch debris.  rev0039 pins service health, safe drain, and continuity
journal restart memory through code, tests, docs, public pointers, foldmap,
foldregistry, surfaceledger, and the rev0038 servicecontinuity predecessor.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .foldmap import audit_fold_map
from .foldregistry import audit_fold_registry
from .ids import DOMAIN, sha256
from .servicecontinuityfold import audit_servicecontinuity_fold
from .surfaceledger import audit_surface_ledger, entries_for_revision

SERVICE_OPS_FOLD_DOMAIN = DOMAIN + b":service-ops-fold-v1:"


@dataclass(frozen=True)
class ServiceOpsFoldFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class ServiceOpsFoldReport:
    revision: str
    artifact_stem: str
    status: str
    predecessor_status: str
    foldmap_status: str
    registry_status: str
    surface_ledger_status: str
    findings: tuple[ServiceOpsFoldFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")


REV0039_PATHS = (
    "src/i2p_dht_lab/servicehealth.py",
    "src/i2p_dht_lab/servicedrain.py",
    "src/i2p_dht_lab/continuityjournal.py",
    "src/i2p_dht_lab/serviceopsfold.py",
    "tests/test_rev0039_serviceops_journal_drain.py",
    "docs/393-rev0039-serviceops-healthdrain-journalfold.md",
    "docs/394-service-health-post-continuity.md",
    "docs/395-service-drain-safe-stop.md",
    "docs/396-continuity-journal-restart-memory.md",
    "docs/397-serviceopsfold-audit-refactor.md",
)
NEEDLES = (
    "rev0039",
    "servicehealth",
    "servicedrain",
    "continuityjournal",
    "serviceopsfold",
)


def _contains(path: Path, needle: str) -> bool:
    try:
        return needle in path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return False


def audit_serviceops_fold(root: str | Path, *, revision: str = "rev0039", artifact_stem: str | None = None) -> ServiceOpsFoldReport:
    if revision != "rev0039":
        raise ValueError("serviceopsfold currently audits rev0039")
    root_path = Path(root)
    artifact_stem = artifact_stem or root_path.name
    findings: list[ServiceOpsFoldFinding] = []
    for rel in REV0039_PATHS:
        if not (root_path / rel).exists():
            findings.append(ServiceOpsFoldFinding("error", "missing_rev0039_path", rel, "rev0039 service-ops path is absent"))
    for surface_path in ("PUBLIC_SURFACE.json", "HEAD_REGISTRY.json", "docs/00-index.md"):
        for needle in NEEDLES:
            if not _contains(root_path / surface_path, needle):
                findings.append(ServiceOpsFoldFinding("error", "surface_missing_needle", surface_path, f"missing {needle}"))
    try:
        predecessor = audit_servicecontinuity_fold(root_path, revision="rev0038", artifact_stem="Nicotine-i2pDHT-rev0038-2026.06.04.05.39-servicecontinuity-branchfold")
        predecessor_status = predecessor.status
        if predecessor.error_count:
            findings.append(ServiceOpsFoldFinding("error", "servicecontinuityfold_failed", "src/i2p_dht_lab/servicecontinuityfold.py", "rev0038 predecessor failed"))
    except Exception as exc:  # pragma: no cover
        predecessor_status = "exception"
        findings.append(ServiceOpsFoldFinding("error", "servicecontinuityfold_exception", "src/i2p_dht_lab/servicecontinuityfold.py", str(exc)))
    try:
        foldmap = audit_fold_map(root_path, revision="rev0039", artifact_stem=artifact_stem)
        foldmap_status = foldmap.status
        if foldmap.error_count:
            findings.append(ServiceOpsFoldFinding("error", "foldmap_failed", "src/i2p_dht_lab/foldmap.py", "rev0039 foldmap failed"))
    except Exception as exc:  # pragma: no cover
        foldmap_status = "exception"
        findings.append(ServiceOpsFoldFinding("error", "foldmap_exception", "src/i2p_dht_lab/foldmap.py", str(exc)))
    try:
        registry = audit_fold_registry(root_path, revision="rev0039")
        registry_status = registry.status
        if registry.error_count:
            findings.append(ServiceOpsFoldFinding("error", "foldregistry_failed", "src/i2p_dht_lab/foldregistry.py", "rev0039 registry failed"))
    except Exception as exc:  # pragma: no cover
        registry_status = "exception"
        findings.append(ServiceOpsFoldFinding("error", "foldregistry_exception", "src/i2p_dht_lab/foldregistry.py", str(exc)))
    try:
        ledger = audit_surface_ledger(root_path, entries_for_revision(revision))
        surface_status = "pass" if ledger.ok else "fail"
        if ledger.error_count:
            findings.append(ServiceOpsFoldFinding("error", "surface_ledger_failed", "src/i2p_dht_lab/surfaceledger.py", "rev0039 surface ledger failed"))
    except Exception as exc:  # pragma: no cover
        surface_status = "exception"
        findings.append(ServiceOpsFoldFinding("error", "surface_ledger_exception", "src/i2p_dht_lab/surfaceledger.py", str(exc)))
    status = "pass" if not any(f.severity == "error" for f in findings) else "fail"
    digest = sha256(SERVICE_OPS_FOLD_DOMAIN + b":report:" + bencode({
        b"revision": revision,
        b"artifact": artifact_stem,
        b"status": status,
        b"predecessor": predecessor_status,
        b"foldmap": foldmap_status,
        b"registry": registry_status,
        b"surface": surface_status,
        b"findings": [f.bvalue() for f in findings],
    }))
    return ServiceOpsFoldReport(revision, artifact_stem, status, predecessor_status, foldmap_status, registry_status, surface_status, tuple(findings), digest)
