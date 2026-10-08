"""rev0039 continuity-repair fold audit.

This audit pins the current rev0039 path after rev0038 service continuity:
continuityjournal, probeloop, successionrepair, and this fold module.  It also
keeps the rev0038 servicecontinuityfold predecessor visible so the new restart,
probe-loop, and succession-repair surfaces do not float away from the joined
service boundary they are extending.
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

CONTINUITY_REPAIR_FOLD_DOMAIN = DOMAIN + b":continuity-repair-fold-v1:"


@dataclass(frozen=True)
class ContinuityRepairFoldFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class ContinuityRepairFoldReport:
    revision: str
    artifact_stem: str
    status: str
    predecessor_status: str
    foldmap_status: str
    registry_status: str
    surface_ledger_status: str
    findings: tuple[ContinuityRepairFoldFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")


REV0039_PATHS = (
    "src/i2p_dht_lab/continuityjournal.py",
    "src/i2p_dht_lab/probeloop.py",
    "src/i2p_dht_lab/successionrepair.py",
    "src/i2p_dht_lab/continuityrepairfold.py",
    "tests/test_rev0039_continuityjournal_probeloop_successionrepair.py",
    "docs/393-rev0039-continuityjournal-probeloop-successionrepair.md",
    "docs/395-continuity-journal-restart-memory.md",
    "docs/396-probe-loop-health-pressure.md",
    "docs/398-succession-repair-pressure.md",
    "docs/397-continuityrepairfold-audit-refactor.md",
)

NEEDLES = (
    "rev0039",
    "continuityjournal",
    "probeloop",
    "successionrepair",
    "continuityrepairfold",
)


def _contains(path: Path, needle: str) -> bool:
    try:
        return needle in path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return False


def audit_continuity_repair_fold(root: str | Path, *, revision: str = "rev0039", artifact_stem: str | None = None) -> ContinuityRepairFoldReport:
    if revision != "rev0039":
        raise ValueError("continuityrepairfold currently audits rev0039")
    root_path = Path(root)
    artifact_stem = artifact_stem or root_path.name
    findings: list[ContinuityRepairFoldFinding] = []
    for rel in REV0039_PATHS:
        if not (root_path / rel).exists():
            findings.append(ContinuityRepairFoldFinding("error", "missing_rev0039_path", rel, "rev0039 continuity-repair path is absent"))
    for surface_path in ("PUBLIC_SURFACE.json", "HEAD_REGISTRY.json", "docs/00-index.md"):
        for needle in NEEDLES:
            if not _contains(root_path / surface_path, needle):
                findings.append(ContinuityRepairFoldFinding("error", "surface_missing_needle", surface_path, f"missing {needle}"))
    try:
        predecessor = audit_servicecontinuity_fold(root_path, revision="rev0038", artifact_stem=artifact_stem)
        predecessor_status = predecessor.status
        if predecessor.error_count:
            findings.append(ContinuityRepairFoldFinding("error", "servicecontinuityfold_failed", "src/i2p_dht_lab/servicecontinuityfold.py", "rev0038 servicecontinuityfold predecessor failed"))
    except Exception as exc:  # pragma: no cover
        predecessor_status = "exception"
        findings.append(ContinuityRepairFoldFinding("error", "servicecontinuityfold_exception", "src/i2p_dht_lab/servicecontinuityfold.py", str(exc)))
    try:
        foldmap = audit_fold_map(root_path, revision="rev0039", artifact_stem=artifact_stem)
        foldmap_status = foldmap.status
        if foldmap.error_count:
            findings.append(ContinuityRepairFoldFinding("error", "foldmap_failed", "src/i2p_dht_lab/foldmap.py", "rev0039 foldmap failed"))
    except Exception as exc:  # pragma: no cover
        foldmap_status = "exception"
        findings.append(ContinuityRepairFoldFinding("error", "foldmap_exception", "src/i2p_dht_lab/foldmap.py", str(exc)))
    try:
        registry = audit_fold_registry(root_path, revision="rev0039")
        registry_status = registry.status
        if registry.error_count:
            findings.append(ContinuityRepairFoldFinding("error", "foldregistry_failed", "src/i2p_dht_lab/foldregistry.py", "rev0039 fold registry failed"))
    except Exception as exc:  # pragma: no cover
        registry_status = "exception"
        findings.append(ContinuityRepairFoldFinding("error", "foldregistry_exception", "src/i2p_dht_lab/foldregistry.py", str(exc)))
    try:
        ledger = audit_surface_ledger(root_path, entries_for_revision(revision))
        surface_status = "pass" if ledger.ok else "fail"
        if ledger.error_count:
            findings.append(ContinuityRepairFoldFinding("error", "surface_ledger_failed", "src/i2p_dht_lab/surfaceledger.py", "rev0039 surface ledger failed"))
    except Exception as exc:  # pragma: no cover
        surface_status = "exception"
        findings.append(ContinuityRepairFoldFinding("error", "surface_ledger_exception", "src/i2p_dht_lab/surfaceledger.py", str(exc)))
    status = "pass" if not any(finding.severity == "error" for finding in findings) else "fail"
    digest = sha256(CONTINUITY_REPAIR_FOLD_DOMAIN + b":report:" + bencode({
        b"revision": revision,
        b"artifact": artifact_stem,
        b"status": status,
        b"predecessor_status": predecessor_status,
        b"foldmap_status": foldmap_status,
        b"registry_status": registry_status,
        b"surface_status": surface_status,
        b"findings": [finding.bvalue() for finding in findings],
    }))
    return ContinuityRepairFoldReport(revision, artifact_stem, status, predecessor_status, foldmap_status, registry_status, surface_status, tuple(findings), digest)
