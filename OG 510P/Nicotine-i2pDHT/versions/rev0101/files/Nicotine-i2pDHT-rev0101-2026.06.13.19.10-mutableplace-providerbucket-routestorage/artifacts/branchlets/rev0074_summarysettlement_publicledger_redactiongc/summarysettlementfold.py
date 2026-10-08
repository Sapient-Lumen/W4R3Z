"""rev0074 audit/refactor fold for summary settlement / public ledger / redaction GC."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .foldmap import audit_fold_map
from .foldregistry import audit_fold_registry
from .ids import DOMAIN, sha256
from .summarypublishfold import audit_summary_publish_fold
from .surfaceledger import audit_surface_ledger, entries_for_revision

SUMMARY_SETTLEMENT_FOLD_DOMAIN = DOMAIN + b":summary-settlement-fold-v1:"


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
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")


def _exists(root: Path, rel: str, needle: str, findings: list[SummarySettlementFoldFinding]) -> None:
    path = root / rel
    if not path.exists():
        findings.append(SummarySettlementFoldFinding("error", "missing_path", rel, "rev0074 summarysettlementfold expected this path"))
        return
    text = path.read_text(encoding="utf-8", errors="replace")
    if needle not in text:
        findings.append(SummarySettlementFoldFinding("error", "missing_needle", rel, f"missing needle {needle!r}"))


def audit_summary_settlement_fold(root: str | Path, *, revision: str = "rev0074", artifact_stem: str = "") -> SummarySettlementFoldReport:
    root_path = Path(root)
    artifact = artifact_stem or root_path.name
    findings: list[SummarySettlementFoldFinding] = []
    checks = {
        "src/i2p_dht_lab/summarysettlement.py": "SummarySettlementDecisionKind",
        "src/i2p_dht_lab/publicledger.py": "PublicLedgerDecisionKind",
        "src/i2p_dht_lab/redactiongc.py": "RedactionGCDecisionKind",
        "src/i2p_dht_lab/summarysettlementfold.py": "audit_summary_settlement_fold",
        "tests/test_rev0074_summarysettlement_publicledger_redactiongc.py": "test_summary_settlement_public_ledger_redaction_gc_happy_path",
        "docs/778-rev0074-summarysettlement-publicledger-redactiongc.md": "rev0074",
        "docs/779-summary-settlement-after-import-prune-audit.md": "summary settlement",
        "docs/780-public-summary-ledger-memory.md": "public-summary ledger",
        "docs/781-redaction-gc-after-public-ledger.md": "redaction GC",
        "docs/782-summarysettlementfold-audit-refactor.md": "summarysettlementfold",
    }
    for rel, needle in checks.items():
        _exists(root_path, rel, needle, findings)
    try:
        predecessor = audit_summary_publish_fold(root_path, revision="rev0073", artifact_stem="x")
        predecessor_status = predecessor.status
        if predecessor.error_count:
            findings.append(SummarySettlementFoldFinding("error", "predecessor_failed", "src/i2p_dht_lab/summarypublishfold.py", "rev0073 predecessor failed"))
    except Exception as exc:  # pragma: no cover
        predecessor_status = "exception"
        findings.append(SummarySettlementFoldFinding("error", "predecessor_exception", "src/i2p_dht_lab/summarypublishfold.py", str(exc)))
    try:
        fmap = audit_fold_map(root_path, revision=revision, artifact_stem=artifact)
        foldmap_status = fmap.status
        if fmap.error_count:
            findings.append(SummarySettlementFoldFinding("error", "foldmap_failed", "src/i2p_dht_lab/foldmap.py", "rev0074 fold map failed"))
    except Exception as exc:  # pragma: no cover
        foldmap_status = "exception"
        findings.append(SummarySettlementFoldFinding("error", "foldmap_exception", "src/i2p_dht_lab/foldmap.py", str(exc)))
    try:
        registry = audit_fold_registry(root_path, revision=revision)
        foldregistry_status = registry.status
        if registry.error_count:
            findings.append(SummarySettlementFoldFinding("error", "foldregistry_failed", "src/i2p_dht_lab/foldregistry.py", "rev0074 fold registry failed"))
    except Exception as exc:  # pragma: no cover
        foldregistry_status = "exception"
        findings.append(SummarySettlementFoldFinding("error", "foldregistry_exception", "src/i2p_dht_lab/foldregistry.py", str(exc)))
    try:
        ledger = audit_surface_ledger(root_path, entries_for_revision(revision))
        surface_ledger_status = "pass" if ledger.ok else "fail"
        if ledger.error_count:
            findings.append(SummarySettlementFoldFinding("error", "surface_ledger_failed", "src/i2p_dht_lab/surfaceledger.py", "rev0074 surface ledger failed"))
    except Exception as exc:  # pragma: no cover
        surface_ledger_status = "exception"
        findings.append(SummarySettlementFoldFinding("error", "surface_ledger_exception", "src/i2p_dht_lab/surfaceledger.py", str(exc)))
    status = "pass" if not any(finding.severity == "error" for finding in findings) else "fail"
    digest = sha256(SUMMARY_SETTLEMENT_FOLD_DOMAIN + b":report:" + bencode({
        b"revision": revision,
        b"artifact": artifact,
        b"status": status,
        b"predecessor": predecessor_status,
        b"foldmap": foldmap_status,
        b"foldregistry": foldregistry_status,
        b"surface": surface_ledger_status,
        b"findings": [finding.bvalue() for finding in findings],
    }))
    return SummarySettlementFoldReport(revision, artifact, status, predecessor_status, foldmap_status, foldregistry_status, surface_ledger_status, tuple(findings), digest)
