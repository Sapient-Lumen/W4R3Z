"""rev0035 start-boundary fold audit.

This fold pins the current path: startmatrix, routerharness, telemetrydebt, and
this startfold audit.  It keeps rev0034 foldmerge as predecessor history rather
than deleting it.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .foldmap import audit_fold_map
from .foldmerge import audit_fold_merge
from .ids import DOMAIN, sha256
from .surfaceledger import audit_surface_ledger, entries_for_revision

START_FOLD_DOMAIN = DOMAIN + b":start-fold-v1:"


@dataclass(frozen=True)
class StartFoldFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class StartFoldReport:
    revision: str
    artifact_stem: str
    status: str
    predecessor_status: str
    foldmap_status: str
    surface_ledger_status: str
    findings: tuple[StartFoldFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")


REV0035_PATHS = (
    "src/i2p_dht_lab/startmatrix.py",
    "src/i2p_dht_lab/routerharness.py",
    "src/i2p_dht_lab/telemetrydebt.py",
    "src/i2p_dht_lab/startfold.py",
    "tests/test_rev0035_startmatrix_telemetry_router.py",
    "docs/349-rev0035-startmatrix-telemetrydebt-routerharness.md",
    "docs/350-start-profile-matrix.md",
    "docs/351-router-harness-config-capsule.md",
    "docs/352-telemetry-debt-retention.md",
    "docs/353-startfold-audit-refactor.md",
)
NEEDLES = ("rev0035", "startmatrix", "routerharness", "telemetrydebt", "startfold")


def _contains(path: Path, needle: str) -> bool:
    try:
        return needle in path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return False


def audit_start_fold(root: str | Path, *, revision: str = "rev0035", artifact_stem: str | None = None) -> StartFoldReport:
    if revision != "rev0035":
        raise ValueError("startfold currently audits the rev0035 active path")
    root_path = Path(root)
    artifact_stem = artifact_stem or root_path.name
    findings: list[StartFoldFinding] = []
    for rel in REV0035_PATHS:
        if not (root_path / rel).exists():
            findings.append(StartFoldFinding("error", "missing_rev0035_path", rel, "rev0035 active path is absent"))
    for surface_path in ("PUBLIC_SURFACE.json", "HEAD_REGISTRY.json", "docs/00-index.md"):
        for needle in NEEDLES:
            if not _contains(root_path / surface_path, needle):
                findings.append(StartFoldFinding("error", "surface_missing_needle", surface_path, f"missing {needle}"))
    try:
        predecessor = audit_fold_merge(root_path, revision="rev0034", artifact_stem=artifact_stem)
        predecessor_status = predecessor.status
        if predecessor.error_count:
            findings.append(StartFoldFinding("error", "predecessor_foldmerge_failed", "src/i2p_dht_lab/foldmerge.py", "rev0034 foldmerge predecessor failed"))
    except Exception as exc:  # pragma: no cover
        predecessor_status = "exception"
        findings.append(StartFoldFinding("error", "predecessor_foldmerge_exception", "src/i2p_dht_lab/foldmerge.py", str(exc)))
    try:
        foldmap = audit_fold_map(root_path, revision="rev0035", artifact_stem=artifact_stem)
        foldmap_status = foldmap.status
        if foldmap.error_count:
            findings.append(StartFoldFinding("error", "foldmap_failed", "src/i2p_dht_lab/foldmap.py", "rev0035 foldmap failed"))
    except Exception as exc:  # pragma: no cover
        foldmap_status = "exception"
        findings.append(StartFoldFinding("error", "foldmap_exception", "src/i2p_dht_lab/foldmap.py", str(exc)))
    try:
        ledger = audit_surface_ledger(root_path, entries_for_revision(revision))
        surface_status = "pass" if ledger.ok else "fail"
        if ledger.error_count:
            findings.append(StartFoldFinding("error", "surface_ledger_failed", "src/i2p_dht_lab/surfaceledger.py", "rev0035 surface ledger failed"))
    except Exception as exc:  # pragma: no cover
        surface_status = "exception"
        findings.append(StartFoldFinding("error", "surface_ledger_exception", "src/i2p_dht_lab/surfaceledger.py", str(exc)))
    status = "pass" if not any(item.severity == "error" for item in findings) else "fail"
    digest = sha256(START_FOLD_DOMAIN + b":report:" + bencode({
        b"revision": revision,
        b"artifact": artifact_stem,
        b"status": status,
        b"predecessor_status": predecessor_status,
        b"foldmap_status": foldmap_status,
        b"surface_status": surface_status,
        b"findings": [finding.bvalue() for finding in findings],
    }))
    return StartFoldReport(revision, artifact_stem, status, predecessor_status, foldmap_status, surface_status, tuple(findings), digest)
