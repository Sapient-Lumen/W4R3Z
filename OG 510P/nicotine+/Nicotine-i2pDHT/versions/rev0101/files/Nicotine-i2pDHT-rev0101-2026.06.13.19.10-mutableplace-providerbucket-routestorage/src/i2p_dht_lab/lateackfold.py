"""rev0063 audit/refactor fold for late ACK, retry settlement, and egress journal."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .egressrepairfold import audit_egress_repair_fold
from .foldmap import audit_fold_map
from .foldregistry import audit_fold_registry
from .ids import DOMAIN, sha256
from .surfaceledger import audit_surface_ledger, entries_for_revision

LATE_ACK_FOLD_DOMAIN = DOMAIN + b":late-ack-fold-v1:"


@dataclass(frozen=True)
class LateAckFoldFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class LateAckFoldReport:
    revision: str
    artifact_stem: str
    status: str
    predecessor_status: str
    foldmap_status: str
    foldregistry_status: str
    surface_ledger_status: str
    findings: tuple[LateAckFoldFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")


def _exists(root: Path, rel: str, needle: str, findings: list[LateAckFoldFinding]) -> None:
    path = root / rel
    if not path.exists():
        findings.append(LateAckFoldFinding("error", "missing_path", rel, "rev0063 lateackfold expected this path"))
        return
    text = path.read_text(encoding="utf-8", errors="replace")
    if needle not in text:
        findings.append(LateAckFoldFinding("error", "missing_needle", rel, f"missing needle {needle!r}"))


def audit_late_ack_fold(root: str | Path, *, revision: str = "rev0063", artifact_stem: str = "") -> LateAckFoldReport:
    root_path = Path(root)
    artifact = artifact_stem or root_path.name
    findings: list[LateAckFoldFinding] = []
    checks = {
        "src/i2p_dht_lab/lateack.py": "LateAckDecisionKind",
        "src/i2p_dht_lab/retrysettlement.py": "RetrySettlementDecisionKind",
        "src/i2p_dht_lab/withdrawrepair.py": "WithdrawRepairDecisionKind",
        "src/i2p_dht_lab/egressjournal.py": "EgressJournalDecisionKind",
        "src/i2p_dht_lab/lateackfold.py": "audit_late_ack_fold",
        "tests/test_rev0063_lateack_retrysettle_egressjournal.py": "test_late_ack_after_retry_fence_aborts_retry_and_journals_cleanly",
        "docs/668-rev0063-lateack-retrysettle-egressjournal.md": "rev0063",
        "docs/669-late-ack-after-retry-fence.md": "late ACK",
        "docs/670-retry-settlement-and-withdraw-repair.md": "retry settlement",
        "docs/671-egress-journal-compaction.md": "egress journal",
        "docs/672-lateackfold-audit-refactor.md": "lateackfold",
    }
    for rel, needle in checks.items():
        _exists(root_path, rel, needle, findings)
    try:
        predecessor = audit_egress_repair_fold(root_path, revision="rev0062", artifact_stem=artifact)
        predecessor_status = predecessor.status
        if predecessor.error_count:
            findings.append(LateAckFoldFinding("error", "predecessor_failed", "src/i2p_dht_lab/egressrepairfold.py", "rev0062 predecessor failed"))
    except Exception as exc:  # pragma: no cover
        predecessor_status = "exception"
        findings.append(LateAckFoldFinding("error", "predecessor_exception", "src/i2p_dht_lab/egressrepairfold.py", str(exc)))
    try:
        fmap = audit_fold_map(root_path, revision=revision, artifact_stem=artifact)
        foldmap_status = fmap.status
        if fmap.error_count:
            findings.append(LateAckFoldFinding("error", "foldmap_failed", "src/i2p_dht_lab/foldmap.py", "rev0063 fold map failed"))
    except Exception as exc:  # pragma: no cover
        foldmap_status = "exception"
        findings.append(LateAckFoldFinding("error", "foldmap_exception", "src/i2p_dht_lab/foldmap.py", str(exc)))
    try:
        registry = audit_fold_registry(root_path, revision=revision)
        foldregistry_status = registry.status
        if registry.error_count:
            findings.append(LateAckFoldFinding("error", "foldregistry_failed", "src/i2p_dht_lab/foldregistry.py", "rev0063 fold registry failed"))
    except Exception as exc:  # pragma: no cover
        foldregistry_status = "exception"
        findings.append(LateAckFoldFinding("error", "foldregistry_exception", "src/i2p_dht_lab/foldregistry.py", str(exc)))
    try:
        ledger = audit_surface_ledger(root_path, entries_for_revision(revision))
        surface_ledger_status = "pass" if ledger.ok else "fail"
        if ledger.error_count:
            findings.append(LateAckFoldFinding("error", "surface_ledger_failed", "src/i2p_dht_lab/surfaceledger.py", "rev0063 surface ledger failed"))
    except Exception as exc:  # pragma: no cover
        surface_ledger_status = "exception"
        findings.append(LateAckFoldFinding("error", "surface_ledger_exception", "src/i2p_dht_lab/surfaceledger.py", str(exc)))
    status = "pass" if not any(f.severity == "error" for f in findings) else "fail"
    digest = sha256(LATE_ACK_FOLD_DOMAIN + b":report:" + bencode({
        b"revision": revision, b"artifact": artifact, b"status": status,
        b"predecessor": predecessor_status, b"foldmap": foldmap_status,
        b"foldregistry": foldregistry_status, b"surface": surface_ledger_status,
        b"findings": [finding.bvalue() for finding in findings],
    }))
    return LateAckFoldReport(revision, artifact, status, predecessor_status, foldmap_status, foldregistry_status, surface_ledger_status, tuple(findings), digest)
