"""Current-revision risk-surface audit for rev0025.

Older fold modules audit particular families of surfaces.  rev0025 adds a small
cross-cutting audit for the new surfaces that deliberately join hard boundaries:
capability-gated dispatch, evidence GC, and partition merge.  The audit stays
boring: make sure code, tests, docs, public pointers, and active ledger entries
all mention the current risk surfaces.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .bencode import bencode
from .ids import DOMAIN, sha256
from .surfaceledger import audit_surface_ledger, entries_for_revision

RISK_FOLD_DOMAIN = DOMAIN + b":risk-fold-v1:"


@dataclass(frozen=True)
class RiskFoldFinding:
    severity: str
    code: str
    path: str
    detail: str


@dataclass(frozen=True)
class RiskFoldReport:
    revision: str
    status: str
    findings: tuple[RiskFoldFinding, ...]
    checked_paths: tuple[str, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for item in self.findings if item.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for item in self.findings if item.severity == "warning")


def _contains(path: Path, needle: str) -> bool:
    try:
        return needle in path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return False


def audit_risk_fold(root: str | Path, *, revision: str = "rev0025") -> RiskFoldReport:
    root_path = Path(root)
    required = (
        "src/i2p_dht_lab/capgate.py",
        "src/i2p_dht_lab/evidencegc.py",
        "src/i2p_dht_lab/splitmerge.py",
        "src/i2p_dht_lab/riskfold.py",
        "tests/test_rev0025_capgate_evidence_splitmerge.py",
        "docs/231-rev0025-capgate-evidencegc-splitmerge.md",
        "docs/232-capability-dispatch-gate.md",
        "docs/233-evidence-gc-and-memory-pressure.md",
        "docs/234-partition-merge-and-split-brain.md",
        "docs/235-riskfold-audit-refactor.md",
    )
    findings: list[RiskFoldFinding] = []
    for rel in required:
        if not (root_path / rel).exists():
            findings.append(RiskFoldFinding("error", "missing_required_path", rel, "rev0025 risk fold required path is absent"))
    for rel, needle in (
        ("PUBLIC_SURFACE.json", "docs/231-rev0025-capgate-evidencegc-splitmerge.md"),
        ("HEAD_REGISTRY.json", "capability_dispatch_gate"),
        ("docs/00-index.md", "rev0025 capgate / evidencegc / splitmerge"),
    ):
        if not _contains(root_path / rel, needle):
            findings.append(RiskFoldFinding("error", "missing_pointer_text", rel, f"expected pointer text not found: {needle}"))
    try:
        ledger = audit_surface_ledger(root_path, entries_for_revision(revision))
        if ledger.error_count:
            findings.append(RiskFoldFinding("error", "surface_ledger_errors", "src/i2p_dht_lab/surfaceledger.py", "surface ledger has current revision errors"))
    except Exception as exc:  # pragma: no cover - audit defensive only
        findings.append(RiskFoldFinding("error", "surface_ledger_exception", "src/i2p_dht_lab/surfaceledger.py", str(exc)))
    status = "pass" if not any(item.severity == "error" for item in findings) else "fail"
    digest = sha256(RISK_FOLD_DOMAIN + b":report:" + bencode({
        b"revision": revision,
        b"status": status,
        b"checked": list(required),
        b"findings": [{b"severity": item.severity, b"code": item.code, b"path": item.path, b"detail": item.detail} for item in findings],
    }))
    return RiskFoldReport(revision, status, tuple(findings), required, digest)
