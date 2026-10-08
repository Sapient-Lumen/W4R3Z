"""rev0079 audit/refactor fold for export receipt, import gate, and retention audit."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .foldmap import audit_fold_map
from .foldregistry import audit_fold_registry
from .ids import DOMAIN, sha256
from .summaryreplayfold import audit_summary_replay_fold
from .surfaceledger import audit_surface_ledger, entries_for_revision

SUMMARY_EXPORT_RECEIPT_FOLD_DOMAIN = DOMAIN + b":summary-export-receipt-fold-v1:"


@dataclass(frozen=True)
class SummaryExportReceiptFoldFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class SummaryExportReceiptFoldReport:
    revision: str
    artifact_stem: str
    status: str
    predecessor_status: str
    foldmap_status: str
    foldregistry_status: str
    surface_ledger_status: str
    findings: tuple[SummaryExportReceiptFoldFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")


def _exists(root: Path, rel: str, needle: str, findings: list[SummaryExportReceiptFoldFinding]) -> None:
    path = root / rel
    if not path.exists():
        findings.append(SummaryExportReceiptFoldFinding("error", "missing_path", rel, "rev0079 expected this path"))
        return
    if needle not in path.read_text(encoding="utf-8", errors="replace"):
        findings.append(SummaryExportReceiptFoldFinding("error", "missing_needle", rel, f"missing needle {needle!r}"))


def audit_summary_export_receipt_fold(root: str | Path, *, revision: str = "rev0079", artifact_stem: str = "") -> SummaryExportReceiptFoldReport:
    root_path = Path(root)
    artifact = artifact_stem or root_path.name
    findings: list[SummaryExportReceiptFoldFinding] = []
    checks = {
        "src/i2p_dht_lab/summaryexportreceipt.py": "SummaryExportReceiptDecisionKind",
        "src/i2p_dht_lab/summaryimportgate.py": "SummaryImportDecisionKind",
        "src/i2p_dht_lab/exportretentionaudit.py": "ExportRetentionDecisionKind",
        "src/i2p_dht_lab/summaryexportreceiptfold.py": "audit_summary_export_receipt_fold",
        "tests/test_rev0079_summaryexportreceipt_importgate_retentionaudit.py": "test_summary_export_receipt_import_retention_happy_path",
        "docs/828-rev0079-summaryexportreceipt-importgate-retentionaudit.md": "rev0079",
        "docs/829-summary-export-receipt-after-export-fence.md": "summary export receipt",
        "docs/830-summary-import-gate-after-receipt.md": "Summary import gate",
        "docs/831-export-retention-audit.md": "Export retention audit",
        "docs/832-summaryexportreceiptfold-audit-refactor.md": "summaryexportreceiptfold",
    }
    for rel, needle in checks.items():
        _exists(root_path, rel, needle, findings)

    try:
        predecessor = audit_summary_replay_fold(root_path, revision="rev0078", artifact_stem=artifact)
        predecessor_status = predecessor.status
        if predecessor.error_count:
            findings.append(SummaryExportReceiptFoldFinding("error", "predecessor_failed", "src/i2p_dht_lab/summaryreplayfold.py", "rev0078 predecessor failed"))
    except Exception as exc:  # pragma: no cover
        predecessor_status = "exception"
        findings.append(SummaryExportReceiptFoldFinding("error", "predecessor_exception", "src/i2p_dht_lab/summaryreplayfold.py", str(exc)))

    try:
        fmap = audit_fold_map(root_path, revision=revision, artifact_stem=artifact)
        foldmap_status = fmap.status
        if fmap.error_count:
            findings.append(SummaryExportReceiptFoldFinding("error", "foldmap_failed", "src/i2p_dht_lab/foldmap.py", "rev0079 fold map failed"))
    except Exception as exc:  # pragma: no cover
        foldmap_status = "exception"
        findings.append(SummaryExportReceiptFoldFinding("error", "foldmap_exception", "src/i2p_dht_lab/foldmap.py", str(exc)))

    try:
        registry = audit_fold_registry(root_path, revision=revision)
        foldregistry_status = registry.status
        if registry.error_count:
            findings.append(SummaryExportReceiptFoldFinding("error", "foldregistry_failed", "src/i2p_dht_lab/foldregistry.py", "rev0079 fold registry failed"))
    except Exception as exc:  # pragma: no cover
        foldregistry_status = "exception"
        findings.append(SummaryExportReceiptFoldFinding("error", "foldregistry_exception", "src/i2p_dht_lab/foldregistry.py", str(exc)))

    try:
        ledger = audit_surface_ledger(root_path, entries_for_revision(revision))
        surface_ledger_status = "pass" if ledger.ok else "fail"
        if ledger.error_count:
            findings.append(SummaryExportReceiptFoldFinding("error", "surface_ledger_failed", "src/i2p_dht_lab/surfaceledger.py", "rev0079 surface ledger failed"))
    except Exception as exc:  # pragma: no cover
        surface_ledger_status = "exception"
        findings.append(SummaryExportReceiptFoldFinding("error", "surface_ledger_exception", "src/i2p_dht_lab/surfaceledger.py", str(exc)))

    status = "pass" if not any(f.severity == "error" for f in findings) else "fail"
    report_digest = sha256(SUMMARY_EXPORT_RECEIPT_FOLD_DOMAIN + b":report:" + bencode({
        b"revision": revision,
        b"artifact": artifact,
        b"status": status,
        b"predecessor": predecessor_status,
        b"foldmap": foldmap_status,
        b"registry": foldregistry_status,
        b"surface": surface_ledger_status,
        b"findings": [finding.bvalue() for finding in findings],
    }))
    return SummaryExportReceiptFoldReport(revision, artifact, status, predecessor_status, foldmap_status, foldregistry_status, surface_ledger_status, tuple(findings), report_digest)
