"""Fold audit for the folded rev0074 summary-settlement branchlet."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from .bencode import bencode
from .ids import DOMAIN, sha256

SUMMARY_SETTLEMENT_FOLD_DOMAIN = DOMAIN + b":summary-settlement-fold-v2:"

@dataclass(frozen=True)
class SummarySettlementFoldFinding:
    severity: str
    code: str
    path: str
    detail: str
    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}

@dataclass(frozen=True)
class SummarySettlementFoldReport:
    revision: str
    artifact_stem: str
    status: str
    predecessor_status: str
    foldmap_status: str
    foldregistry_status: str
    surface_ledger_status: str
    findings: tuple[SummarySettlementFoldFinding, ...]
    report_digest: bytes
    @property
    def error_count(self) -> int: return sum(1 for f in self.findings if f.severity == "error")
    @property
    def warning_count(self) -> int: return sum(1 for f in self.findings if f.severity == "warning")

def _exists(root: Path, rel: str, needle: str, findings: list[SummarySettlementFoldFinding]) -> None:
    path = root / rel
    if not path.exists():
        findings.append(SummarySettlementFoldFinding("error", "missing_path", rel, "folded summary-settlement branchlet expected this path")); return
    if needle not in path.read_text(encoding="utf-8", errors="replace"):
        findings.append(SummarySettlementFoldFinding("error", "missing_needle", rel, f"missing needle {needle!r}"))

def audit_summary_settlement_fold(root: str | Path, *, revision: str = "rev0074", artifact_stem: str = "") -> SummarySettlementFoldReport:
    root_path = Path(root); artifact = artifact_stem or root_path.name; findings: list[SummarySettlementFoldFinding] = []
    checks = {
        "src/i2p_dht_lab/summarysettlement.py": "SummarySettlementDecisionKind",
        "src/i2p_dht_lab/publicledger.py": "PublicLedgerDecisionKind",
        "src/i2p_dht_lab/redactiongc.py": "RedactionGCDecisionKind",
        "src/i2p_dht_lab/summarysettlementfold.py": "audit_summary_settlement_fold",
        "tests/test_rev0074_summarysettlement_publicledger_redactiongc.py": "test_summary_settlement_public_ledger_redaction_gc_happy_path",
        "docs/790-redaction-gc-join-after-archive.md": "summarysettlement branchlet",
        "artifacts/branchlets/rev0074_summarysettlement_publicledger_redactiongc/test_rev0074_summarysettlement_publicledger_redactiongc.py": "summary_settlement_public_ledger",
    }
    for rel, needle in checks.items(): _exists(root_path, rel, needle, findings)
    status = "pass" if not any(f.severity == "error" for f in findings) else "fail"
    digest = sha256(SUMMARY_SETTLEMENT_FOLD_DOMAIN + b":report:" + bencode({b"revision": revision, b"artifact": artifact, b"status": status, b"findings": [f.bvalue() for f in findings]}))
    return SummarySettlementFoldReport(revision, artifact, status, "folded_branchlet", "not_checked", "not_checked", "not_checked", tuple(findings), digest)
