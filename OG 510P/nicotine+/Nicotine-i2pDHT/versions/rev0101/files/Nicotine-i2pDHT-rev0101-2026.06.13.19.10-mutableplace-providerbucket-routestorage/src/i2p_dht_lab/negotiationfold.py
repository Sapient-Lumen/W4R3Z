"""rev0033 fold audit for negotiation, migration, safe-start, and fold-map.

The audit/refactor lane keeps new risk surfaces visible from public pointers,
HEAD_REGISTRY, docs, tests, and the active surface ledger while preserving the
rev0032 scopefold/foldmap predecessor path.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .foldmap import audit_fold_map
from .ids import DOMAIN, sha256
from .surfaceledger import audit_surface_ledger, entries_for_revision

NEGOTIATION_FOLD_DOMAIN = DOMAIN + b":negotiation-fold-v1:"


@dataclass(frozen=True)
class NegotiationFoldFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class NegotiationFoldReport:
    revision: str
    artifact_stem: str
    status: str
    predecessor_status: str
    foldmap_status: str
    surface_ledger_status: str
    findings: tuple[NegotiationFoldFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")


REV0033_PATHS = (
    "src/i2p_dht_lab/negotiationlane.py",
    "src/i2p_dht_lab/migrationlane.py",
    "src/i2p_dht_lab/safestart.py",
    "src/i2p_dht_lab/negotiationfold.py",
    "tests/test_rev0033_negotiation_migration_safestart.py",
    "docs/329-rev0033-negotiationlane-migrationseal.md",
    "docs/330-protocol-negotiation-downgrade-pressure.md",
    "docs/331-state-migration-hard-negative-preservation.md",
    "docs/332-safe-start-joined-boundary.md",
    "docs/333-negotiationfold-audit-refactor.md",
)
NEEDLES = ("rev0033", "negotiationlane", "migrationlane", "safestart", "negotiationfold")


def _contains(path: Path, needle: str) -> bool:
    try:
        return needle in path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return False


def audit_negotiation_fold(root: str | Path, *, revision: str = "rev0033", artifact_stem: str | None = None) -> NegotiationFoldReport:
    if revision != "rev0033":
        raise ValueError("negotiationfold currently audits the rev0033 active path")
    root_path = Path(root)
    artifact_stem = artifact_stem or root_path.name
    findings: list[NegotiationFoldFinding] = []
    for rel in REV0033_PATHS:
        if not (root_path / rel).exists():
            findings.append(NegotiationFoldFinding("error", "missing_rev0033_path", rel, "rev0033 active path is absent"))
    for surface_path in ("PUBLIC_SURFACE.json", "HEAD_REGISTRY.json", "docs/00-index.md"):
        for needle in NEEDLES:
            if not _contains(root_path / surface_path, needle):
                findings.append(NegotiationFoldFinding("error", "surface_missing_needle", surface_path, f"missing {needle}"))
    try:
        predecessor = __import__("i2p_dht_lab.scopefold", fromlist=["audit_scope_fold"]).audit_scope_fold(root_path, revision="rev0032", artifact_stem=artifact_stem)
        predecessor_status = predecessor.status
        if predecessor.error_count:
            findings.append(NegotiationFoldFinding("error", "predecessor_scopefold_failed", "src/i2p_dht_lab/scopefold.py", "rev0032 scopefold predecessor failed"))
    except Exception as exc:  # pragma: no cover - defensive audit surface
        predecessor_status = "exception"
        findings.append(NegotiationFoldFinding("error", "predecessor_scopefold_exception", "src/i2p_dht_lab/scopefold.py", str(exc)))
    try:
        foldmap = audit_fold_map(root_path, revision="rev0033", artifact_stem=artifact_stem)
        foldmap_status = foldmap.status
        if foldmap.error_count:
            findings.append(NegotiationFoldFinding("error", "foldmap_failed", "src/i2p_dht_lab/foldmap.py", "rev0033 foldmap failed"))
    except Exception as exc:  # pragma: no cover - defensive audit surface
        foldmap_status = "exception"
        findings.append(NegotiationFoldFinding("error", "foldmap_exception", "src/i2p_dht_lab/foldmap.py", str(exc)))
    try:
        ledger = audit_surface_ledger(root_path, entries_for_revision(revision))
        surface_status = "pass" if ledger.ok else "fail"
        if ledger.error_count:
            findings.append(NegotiationFoldFinding("error", "surface_ledger_failed", "src/i2p_dht_lab/surfaceledger.py", "rev0033 surface ledger failed"))
    except Exception as exc:  # pragma: no cover - defensive audit surface
        surface_status = "exception"
        findings.append(NegotiationFoldFinding("error", "surface_ledger_exception", "src/i2p_dht_lab/surfaceledger.py", str(exc)))
    status = "pass" if not any(item.severity == "error" for item in findings) else "fail"
    digest = sha256(NEGOTIATION_FOLD_DOMAIN + b":report:" + bencode({
        b"revision": revision,
        b"artifact": artifact_stem,
        b"status": status,
        b"predecessor_status": predecessor_status,
        b"foldmap_status": foldmap_status,
        b"surface_status": surface_status,
        b"findings": [finding.bvalue() for finding in findings],
    }))
    return NegotiationFoldReport(revision, artifact_stem, status, predecessor_status, foldmap_status, surface_status, tuple(findings), digest)
