"""rev0059 terminal receipt / idempotency repair / compaction audit fold."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .finalityfold import audit_finality_fold
from .foldmap import audit_fold_map
from .foldregistry import audit_fold_registry
from .ids import DOMAIN, sha256
from .surfaceledger import audit_surface_ledger, entries_for_revision

TERMINAL_FOLD_DOMAIN = DOMAIN + b":terminal-fold-v1:"


@dataclass(frozen=True)
class TerminalFoldFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class TerminalFoldReport:
    revision: str
    artifact_stem: str
    status: str
    finality_predecessor_status: str
    foldmap_status: str
    foldregistry_status: str
    surface_ledger_status: str
    findings: tuple[TerminalFoldFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")


def _exists(root: Path, rel: str, findings: list[TerminalFoldFinding], needle: str = "") -> None:
    target = root / rel
    if not target.exists():
        findings.append(TerminalFoldFinding("error", "missing_path", rel, "rev0059 terminal fold expected this path"))
        return
    if needle:
        text = target.read_text(encoding="utf-8", errors="replace")
        if needle not in text:
            findings.append(TerminalFoldFinding("error", "missing_needle", rel, f"missing {needle!r}"))


def audit_terminal_fold(root: str | Path, *, revision: str = "rev0059", artifact_stem: str = "") -> TerminalFoldReport:
    root_path = Path(root)
    artifact = artifact_stem or root_path.name
    findings: list[TerminalFoldFinding] = []
    for rel, needle in (
        ("src/i2p_dht_lab/terminalreceipt.py", "TerminalReceiptDecisionKind"),
        ("src/i2p_dht_lab/idempotencyrepair.py", "IdempotencyRepairDecisionKind"),
        ("src/i2p_dht_lab/compactionaudit.py", "CompactionAuditDecisionKind"),
        ("src/i2p_dht_lab/settlementstore.py", "SettlementStoreDecisionKind"),
        ("src/i2p_dht_lab/terminalfold.py", "audit_terminal_fold"),
        ("tests/test_rev0059_terminalreceipt_idemrepair_compactionaudit.py", "test_terminal_receipt_accepts_terminal_commit"),
        ("tests/test_rev0059_settlement_attestation_tombrepair.py", "test_settlement_accepts_retry_hold_without_erasing_dead_letter"),
        ("docs/620-rev0059-terminalreceipt-idemrepair-compactionaudit.md", "rev0059"),
        ("docs/621-terminal-receipt-after-finality.md", "terminal receipt"),
        ("docs/622-idempotency-repair-lineage.md", "idempotency"),
        ("docs/623-compaction-audit-hard-negatives.md", "compaction"),
        ("docs/624-terminalfold-audit-refactor.md", "terminalfold"),
    ):
        _exists(root_path, rel, findings, needle)
    try:
        predecessor = audit_finality_fold(root_path, revision="rev0058", artifact_stem=artifact)
        finality_status = predecessor.status
        if predecessor.error_count:
            findings.append(TerminalFoldFinding("error", "finality_predecessor_failed", "src/i2p_dht_lab/finalityfold.py", "rev0058 finality fold failed"))
    except Exception as exc:  # pragma: no cover
        finality_status = "exception"
        findings.append(TerminalFoldFinding("error", "finality_predecessor_exception", "src/i2p_dht_lab/finalityfold.py", str(exc)))
    try:
        fmap = audit_fold_map(root_path, revision=revision, artifact_stem=artifact)
        foldmap_status = fmap.status
        if fmap.error_count:
            findings.append(TerminalFoldFinding("error", "foldmap_failed", "src/i2p_dht_lab/foldmap.py", "rev0059 fold map failed"))
    except Exception as exc:  # pragma: no cover
        foldmap_status = "exception"
        findings.append(TerminalFoldFinding("error", "foldmap_exception", "src/i2p_dht_lab/foldmap.py", str(exc)))
    try:
        registry = audit_fold_registry(root_path, revision=revision)
        foldregistry_status = registry.status
        if registry.error_count:
            findings.append(TerminalFoldFinding("error", "foldregistry_failed", "src/i2p_dht_lab/foldregistry.py", "rev0059 fold registry failed"))
    except Exception as exc:  # pragma: no cover
        foldregistry_status = "exception"
        findings.append(TerminalFoldFinding("error", "foldregistry_exception", "src/i2p_dht_lab/foldregistry.py", str(exc)))
    try:
        ledger = audit_surface_ledger(root_path, entries_for_revision(revision))
        surface_status = "pass" if ledger.ok else "fail"
        if ledger.error_count:
            findings.append(TerminalFoldFinding("error", "surface_ledger_failed", "src/i2p_dht_lab/surfaceledger.py", "rev0059 surface ledger failed"))
    except Exception as exc:  # pragma: no cover
        surface_status = "exception"
        findings.append(TerminalFoldFinding("error", "surface_ledger_exception", "src/i2p_dht_lab/surfaceledger.py", str(exc)))
    status = "pass" if not any(finding.severity == "error" for finding in findings) else "fail"
    digest = sha256(TERMINAL_FOLD_DOMAIN + b":report:" + bencode({
        b"revision": revision,
        b"artifact": artifact,
        b"status": status,
        b"finality": finality_status,
        b"foldmap": foldmap_status,
        b"foldregistry": foldregistry_status,
        b"surface": surface_status,
        b"findings": [finding.bvalue() for finding in findings],
    }))
    return TerminalFoldReport(revision, artifact, status, finality_status, foldmap_status, foldregistry_status, surface_status, tuple(findings), digest)
