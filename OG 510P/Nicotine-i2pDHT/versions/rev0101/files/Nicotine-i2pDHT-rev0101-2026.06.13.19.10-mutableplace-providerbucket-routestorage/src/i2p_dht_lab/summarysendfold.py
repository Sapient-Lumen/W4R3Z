"""rev0075 audit/refactor fold for summary send canary and outbox settlement."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from .bencode import bencode
from .foldmap import audit_fold_map
from .foldregistry import audit_fold_registry
from .ids import DOMAIN, sha256
from .summaryoutboxfold import audit_summary_outbox_fold
from .surfaceledger import audit_surface_ledger, entries_for_revision
SUMMARY_SEND_FOLD_DOMAIN = DOMAIN + b":summary-send-fold-v2:"

@dataclass(frozen=True)
class SummarySendFoldFinding:
    severity: str; code: str; path: str; detail: str
    def bvalue(self) -> dict[bytes, object]: return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}

@dataclass(frozen=True)
class SummarySendFoldReport:
    revision: str; artifact_stem: str; status: str; predecessor_status: str; sibling_branch_status: str; foldmap_status: str; foldregistry_status: str; surface_ledger_status: str; findings: tuple[SummarySendFoldFinding, ...]; report_digest: bytes
    @property
    def error_count(self) -> int: return sum(1 for f in self.findings if f.severity == "error")
    @property
    def warning_count(self) -> int: return sum(1 for f in self.findings if f.severity == "warning")

def _exists(root: Path, rel: str, needle: str, findings: list[SummarySendFoldFinding]) -> None:
    path = root / rel
    if not path.exists(): findings.append(SummarySendFoldFinding("error", "missing_path", rel, "rev0075 summarysendfold expected this path")); return
    if needle not in path.read_text(encoding="utf-8", errors="replace"): findings.append(SummarySendFoldFinding("error", "missing_needle", rel, f"missing needle {needle!r}"))

def audit_summary_send_fold(root: str | Path, *, revision: str = "rev0075", artifact_stem: str = "") -> SummarySendFoldReport:
    root_path = Path(root); artifact = artifact_stem or root_path.name; findings: list[SummarySendFoldFinding] = []
    checks = {
        "src/i2p_dht_lab/outboxsettlement.py": "OutboxSettlementDecisionKind",
        "src/i2p_dht_lab/summarysendcanary.py": "SummarySendCanaryDecisionKind",
        "src/i2p_dht_lab/summarysettlement.py": "SummarySettlementDecisionKind",
        "src/i2p_dht_lab/publicledger.py": "PublicLedgerDecisionKind",
        "src/i2p_dht_lab/redactiongc.py": "RedactionGCDecisionKind",
        "src/i2p_dht_lab/summarysendfold.py": "audit_summary_send_fold",
        "tests/test_rev0075_summarysendcanary_redactiongc_outboxsettlement.py": "test_summary_send_canary_happy_path",
        "tests/test_rev0074_summarysettlement_publicledger_redactiongc.py": "test_summary_settlement_public_ledger_redaction_gc_happy_path",
        "docs/788-rev0075-summarysendcanary-redactiongc-outboxsettlement.md": "rev0075",
        "docs/791-outbox-settlement-prepared-aborted-suppressed.md": "outbox settlement",
        "docs/789-summary-send-canary-before-live-write.md": "summary send canary",
        "docs/790-redaction-gc-join-after-archive.md": "summarysettlement branchlet",
        "docs/792-summarysendfold-audit-refactor.md": "summarysendfold",
        "artifacts/branchlets/rev0074_summarysettlement_publicledger_redactiongc/test_rev0074_summarysettlement_publicledger_redactiongc.py": "summary_settlement_public_ledger",
    }
    for rel, needle in checks.items(): _exists(root_path, rel, needle, findings)
    try:
        pred = audit_summary_outbox_fold(root_path, revision="rev0074", artifact_stem="x"); predecessor_status = pred.status
        if pred.error_count: findings.append(SummarySendFoldFinding("error", "predecessor_failed", "src/i2p_dht_lab/summaryoutboxfold.py", "rev0074 predecessor failed"))
    except Exception as exc:
        predecessor_status = "exception"; findings.append(SummarySendFoldFinding("error", "predecessor_exception", "src/i2p_dht_lab/summaryoutboxfold.py", str(exc)))
    sibling_branch_status = "pass"
    try:
        fmap = audit_fold_map(root_path, revision=revision, artifact_stem=artifact); foldmap_status = fmap.status
        if fmap.error_count: findings.append(SummarySendFoldFinding("error", "foldmap_failed", "src/i2p_dht_lab/foldmap.py", "rev0075 fold map failed"))
    except Exception as exc:
        foldmap_status = "exception"; findings.append(SummarySendFoldFinding("error", "foldmap_exception", "src/i2p_dht_lab/foldmap.py", str(exc)))
    try:
        reg = audit_fold_registry(root_path, revision=revision); foldregistry_status = reg.status
        if reg.error_count: findings.append(SummarySendFoldFinding("error", "foldregistry_failed", "src/i2p_dht_lab/foldregistry.py", "rev0075 fold registry failed"))
    except Exception as exc:
        foldregistry_status = "exception"; findings.append(SummarySendFoldFinding("error", "foldregistry_exception", "src/i2p_dht_lab/foldregistry.py", str(exc)))
    try:
        led = audit_surface_ledger(root_path, entries_for_revision(revision)); surface_ledger_status = "pass" if led.ok else "fail"
        if led.error_count: findings.append(SummarySendFoldFinding("error", "surface_ledger_failed", "src/i2p_dht_lab/surfaceledger.py", "rev0075 surface ledger failed"))
    except Exception as exc:
        surface_ledger_status = "exception"; findings.append(SummarySendFoldFinding("error", "surface_ledger_exception", "src/i2p_dht_lab/surfaceledger.py", str(exc)))
    status = "pass" if not any(f.severity == "error" for f in findings) else "fail"
    digest = sha256(SUMMARY_SEND_FOLD_DOMAIN + b":report:" + bencode({b"revision": revision, b"artifact": artifact, b"status": status, b"predecessor": predecessor_status, b"sibling": sibling_branch_status, b"foldmap": foldmap_status, b"registry": foldregistry_status, b"surface": surface_ledger_status, b"findings": [f.bvalue() for f in findings]}))
    return SummarySendFoldReport(revision, artifact, status, predecessor_status, sibling_branch_status, foldmap_status, foldregistry_status, surface_ledger_status, tuple(findings), digest)
