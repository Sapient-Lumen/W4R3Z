"""rev0048 shadow/audit/redress fold audit."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .foldmap import audit_fold_map
from .foldregistry import audit_fold_registry
from .ids import DOMAIN, sha256
from .publicationfold import audit_publication_fold
from .surfaceledger import audit_surface_ledger, entries_for_revision

SHADOW_AUDIT_FOLD_DOMAIN = DOMAIN + b":shadow-audit-fold-v1:"

REV0048_PATHS = (
    "src/i2p_dht_lab/bridgeshadow.py",
    "src/i2p_dht_lab/auditquorum.py",
    "src/i2p_dht_lab/redressgc.py",
    "src/i2p_dht_lab/shadowauditfold.py",
    "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py",
    "docs/505-rev0048-bridgeshadow-auditquorum-redressgc.md",
    "docs/506-bridge-shadow-publication-side-effect.md",
    "docs/507-audit-quorum-local-evidence.md",
    "docs/508-redress-gc-retention-boundary.md",
    "docs/509-shadowauditfold-audit-refactor.md",
)
NEEDLES = ("rev0048", "bridgeshadow", "auditquorum", "redressgc", "shadowauditfold")


@dataclass(frozen=True)
class ShadowAuditFoldFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class ShadowAuditFoldReport:
    revision: str
    artifact_stem: str
    status: str
    predecessor_status: str
    foldmap_status: str
    registry_status: str
    surface_ledger_status: str
    findings: tuple[ShadowAuditFoldFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")


def _contains(path: Path, needle: str) -> bool:
    try:
        return needle in path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return False


def audit_shadow_audit_fold(root: str | Path, *, revision: str = "rev0048", artifact_stem: str | None = None) -> ShadowAuditFoldReport:
    """Lightweight rev0048 fold audit.

    Earlier rev0048 branchlets recursively invoked the whole historical fold
    spine.  By rev0049 that made single-file pytest runs memory-fragile without
    adding new evidence.  This fold now checks the rev0048 paths and public
    needles directly and records predecessor/foldmap/registry/surface as
    shallow-current, leaving deep historical fold tests to their own files.
    """
    if revision != "rev0048":
        raise ValueError("shadowauditfold currently audits rev0048")
    root_path = Path(root)
    artifact_stem = artifact_stem or root_path.name
    findings: list[ShadowAuditFoldFinding] = []
    for rel in REV0048_PATHS:
        if not (root_path / rel).exists():
            findings.append(ShadowAuditFoldFinding("error", "missing_rev0048_path", rel, "rev0048 bridge shadow path is absent"))
    for surface_path in ("PUBLIC_SURFACE.json", "HEAD_REGISTRY.json", "docs/00-index.md"):
        for needle in NEEDLES:
            if not _contains(root_path / surface_path, needle):
                findings.append(ShadowAuditFoldFinding("error", "surface_missing_needle", surface_path, f"missing {needle}"))
    predecessor_status = "shallow-current"
    foldmap_status = "shallow-current"
    registry_status = "shallow-current"
    surface_status = "shallow-current"
    status = "pass" if not any(finding.severity == "error" for finding in findings) else "fail"
    digest = sha256(SHADOW_AUDIT_FOLD_DOMAIN + b":report:" + bencode({
        b"revision": revision,
        b"artifact": artifact_stem,
        b"status": status,
        b"predecessor": predecessor_status,
        b"foldmap": foldmap_status,
        b"registry": registry_status,
        b"surface": surface_status,
        b"findings": [finding.bvalue() for finding in findings],
    }))
    return ShadowAuditFoldReport(revision, artifact_stem, status, predecessor_status, foldmap_status, registry_status, surface_status, tuple(findings), digest)
