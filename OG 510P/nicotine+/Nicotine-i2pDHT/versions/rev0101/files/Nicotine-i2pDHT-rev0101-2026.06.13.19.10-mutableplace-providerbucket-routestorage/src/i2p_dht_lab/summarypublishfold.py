"""rev0073 audit/refactor fold for summary publication / redaction witness / import-prune audit."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .foldmap import audit_fold_map
from .foldregistry import audit_fold_registry
from .ids import DOMAIN, sha256
from .summaryreceiptfold import audit_summary_receipt_fold
from .surfaceledger import audit_surface_ledger, entries_for_revision

SUMMARY_PUBLISH_FOLD_DOMAIN = DOMAIN + b":summary-publish-fold-v1:"


@dataclass(frozen=True)
class SummaryPublishFoldFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class SummaryPublishFoldReport:
    revision: str
    artifact_stem: str
    status: str
    predecessor_status: str
    foldmap_status: str
    foldregistry_status: str
    surface_ledger_status: str
    findings: tuple[SummaryPublishFoldFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")


def _exists(root: Path, rel: str, needle: str, findings: list[SummaryPublishFoldFinding]) -> None:
    path = root / rel
    if not path.exists():
        findings.append(SummaryPublishFoldFinding("error", "missing_path", rel, "rev0073 summarypublishfold expected this path"))
        return
    text = path.read_text(encoding="utf-8", errors="replace")
    if needle not in text:
        findings.append(SummaryPublishFoldFinding("error", "missing_needle", rel, f"missing needle {needle!r}"))


def audit_summary_publish_fold(root: str | Path, *, revision: str = "rev0073", artifact_stem: str = "") -> SummaryPublishFoldReport:
    root_path = Path(root)
    artifact = artifact_stem or root_path.name
    findings: list[SummaryPublishFoldFinding] = []
    checks = {
        "src/i2p_dht_lab/summarypublish.py": "SummaryPublishDecisionKind",
        "src/i2p_dht_lab/redactionwitness.py": "RedactionWitnessDecisionKind",
        "src/i2p_dht_lab/importpruneaudit.py": "ImportPruneAuditDecisionKind",
        "src/i2p_dht_lab/summarypublishfold.py": "audit_summary_publish_fold",
        "tests/test_rev0073_summarypublish_redactionwitness_importpruneaudit.py": "test_summary_publish_redaction_audit_happy_path",
        "docs/768-rev0073-summarypublish-redactionwitness-importpruneaudit.md": "rev0073",
        "docs/769-summary-publication-after-lineage-prune.md": "summary publication",
        "docs/770-redaction-witness-receipts.md": "redaction witness",
        "docs/771-import-prune-audit-after-restart.md": "import-prune audit",
        "docs/772-summarypublishfold-audit-refactor.md": "summarypublishfold",
    }
    for rel, needle in checks.items():
        _exists(root_path, rel, needle, findings)
    try:
        predecessor = audit_summary_receipt_fold(root_path, revision="rev0072", artifact_stem="x")
        predecessor_status = predecessor.status
        if predecessor.error_count:
            findings.append(SummaryPublishFoldFinding("error", "predecessor_failed", "src/i2p_dht_lab/summaryreceiptfold.py", "rev0072 predecessor failed"))
    except Exception as exc:  # pragma: no cover
        predecessor_status = "exception"
        findings.append(SummaryPublishFoldFinding("error", "predecessor_exception", "src/i2p_dht_lab/summaryreceiptfold.py", str(exc)))
    try:
        fmap = audit_fold_map(root_path, revision=revision, artifact_stem=artifact)
        foldmap_status = fmap.status
        if fmap.error_count:
            findings.append(SummaryPublishFoldFinding("error", "foldmap_failed", "src/i2p_dht_lab/foldmap.py", "rev0073 fold map failed"))
    except Exception as exc:  # pragma: no cover
        foldmap_status = "exception"
        findings.append(SummaryPublishFoldFinding("error", "foldmap_exception", "src/i2p_dht_lab/foldmap.py", str(exc)))
    try:
        registry = audit_fold_registry(root_path, revision=revision)
        foldregistry_status = registry.status
        if registry.error_count:
            findings.append(SummaryPublishFoldFinding("error", "foldregistry_failed", "src/i2p_dht_lab/foldregistry.py", "rev0073 fold registry failed"))
    except Exception as exc:  # pragma: no cover
        foldregistry_status = "exception"
        findings.append(SummaryPublishFoldFinding("error", "foldregistry_exception", "src/i2p_dht_lab/foldregistry.py", str(exc)))
    try:
        ledger = audit_surface_ledger(root_path, entries_for_revision(revision))
        surface_ledger_status = "pass" if ledger.ok else "fail"
        if ledger.error_count:
            findings.append(SummaryPublishFoldFinding("error", "surface_ledger_failed", "src/i2p_dht_lab/surfaceledger.py", "rev0073 surface ledger failed"))
    except Exception as exc:  # pragma: no cover
        surface_ledger_status = "exception"
        findings.append(SummaryPublishFoldFinding("error", "surface_ledger_exception", "src/i2p_dht_lab/surfaceledger.py", str(exc)))
    status = "pass" if not any(finding.severity == "error" for finding in findings) else "fail"
    digest = sha256(SUMMARY_PUBLISH_FOLD_DOMAIN + b":report:" + bencode({
        b"revision": revision,
        b"artifact": artifact,
        b"status": status,
        b"predecessor": predecessor_status,
        b"foldmap": foldmap_status,
        b"foldregistry": foldregistry_status,
        b"surface": surface_ledger_status,
        b"findings": [finding.bvalue() for finding in findings],
    }))
    return SummaryPublishFoldReport(revision, artifact, status, predecessor_status, foldmap_status, foldregistry_status, surface_ledger_status, tuple(findings), digest)
