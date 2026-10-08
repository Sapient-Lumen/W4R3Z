"""rev0077 audit/refactor fold for ACK ledger, delivery archive, and prune fence."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .foldmap import audit_fold_map
from .foldregistry import audit_fold_registry
from .ids import DOMAIN, sha256
from .summarydeliveryfold import audit_summary_delivery_fold
from .surfaceledger import audit_surface_ledger, entries_for_revision

SUMMARY_ACK_FOLD_DOMAIN = DOMAIN + b":summary-ack-fold-v1:"


@dataclass(frozen=True)
class SummaryAckFoldFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class SummaryAckFoldReport:
    revision: str
    artifact_stem: str
    status: str
    predecessor_status: str
    foldmap_status: str
    foldregistry_status: str
    surface_ledger_status: str
    findings: tuple[SummaryAckFoldFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")


def _exists(root: Path, rel: str, needle: str, findings: list[SummaryAckFoldFinding]) -> None:
    path = root / rel
    if not path.exists():
        findings.append(SummaryAckFoldFinding("error", "missing_path", rel, "rev0077 expected this path"))
        return
    if needle not in path.read_text(encoding="utf-8", errors="replace"):
        findings.append(SummaryAckFoldFinding("error", "missing_needle", rel, f"missing needle {needle!r}"))


def audit_summary_ack_fold(root: str | Path, *, revision: str = "rev0077", artifact_stem: str = "") -> SummaryAckFoldReport:
    root_path = Path(root)
    artifact = artifact_stem or root_path.name
    findings: list[SummaryAckFoldFinding] = []
    checks = {
        "src/i2p_dht_lab/summaryackledger.py": "SummaryAckDecisionKind",
        "src/i2p_dht_lab/deliveryarchive.py": "DeliveryArchiveDecisionKind",
        "src/i2p_dht_lab/summaryprunefence.py": "SummaryPruneDecisionKind",
        "src/i2p_dht_lab/summaryackfold.py": "audit_summary_ack_fold",
        "tests/test_rev0077_summaryackledger_deliveryarchive_prunefence.py": "test_summary_ack_archive_prune_happy_path",
        "docs/808-rev0077-summaryackledger-deliveryarchive-prunefence.md": "rev0077",
        "docs/809-summary-ack-ledger-after-settlement-fence.md": "summaryackledger",
        "docs/810-delivery-archive-restart-memory.md": "deliveryarchive",
        "docs/811-summary-prune-fence.md": "summaryprunefence",
        "docs/812-summaryackfold-audit-refactor.md": "summaryackfold",
    }
    for rel, needle in checks.items():
        _exists(root_path, rel, needle, findings)

    try:
        predecessor = audit_summary_delivery_fold(root_path, revision="rev0076", artifact_stem=artifact)
        predecessor_status = predecessor.status
        if predecessor.error_count:
            findings.append(SummaryAckFoldFinding("error", "predecessor_failed", "src/i2p_dht_lab/summarydeliveryfold.py", "rev0076 predecessor failed"))
    except Exception as exc:  # pragma: no cover
        predecessor_status = "exception"
        findings.append(SummaryAckFoldFinding("error", "predecessor_exception", "src/i2p_dht_lab/summarydeliveryfold.py", str(exc)))

    try:
        fmap = audit_fold_map(root_path, revision=revision, artifact_stem=artifact)
        foldmap_status = fmap.status
        if fmap.error_count:
            findings.append(SummaryAckFoldFinding("error", "foldmap_failed", "src/i2p_dht_lab/foldmap.py", "rev0077 fold map failed"))
    except Exception as exc:  # pragma: no cover
        foldmap_status = "exception"
        findings.append(SummaryAckFoldFinding("error", "foldmap_exception", "src/i2p_dht_lab/foldmap.py", str(exc)))

    try:
        registry = audit_fold_registry(root_path, revision=revision)
        foldregistry_status = registry.status
        if registry.error_count:
            findings.append(SummaryAckFoldFinding("error", "foldregistry_failed", "src/i2p_dht_lab/foldregistry.py", "rev0077 fold registry failed"))
    except Exception as exc:  # pragma: no cover
        foldregistry_status = "exception"
        findings.append(SummaryAckFoldFinding("error", "foldregistry_exception", "src/i2p_dht_lab/foldregistry.py", str(exc)))

    try:
        ledger = audit_surface_ledger(root_path, entries_for_revision(revision))
        surface_ledger_status = "pass" if ledger.ok else "fail"
        if ledger.error_count:
            findings.append(SummaryAckFoldFinding("error", "surface_ledger_failed", "src/i2p_dht_lab/surfaceledger.py", "rev0077 surface ledger failed"))
    except Exception as exc:  # pragma: no cover
        surface_ledger_status = "exception"
        findings.append(SummaryAckFoldFinding("error", "surface_ledger_exception", "src/i2p_dht_lab/surfaceledger.py", str(exc)))

    status = "pass" if not any(f.severity == "error" for f in findings) else "fail"
    report_digest = sha256(SUMMARY_ACK_FOLD_DOMAIN + b":report:" + bencode({
        b"revision": revision,
        b"artifact": artifact,
        b"status": status,
        b"predecessor": predecessor_status,
        b"foldmap": foldmap_status,
        b"registry": foldregistry_status,
        b"surface": surface_ledger_status,
        b"findings": [finding.bvalue() for finding in findings],
    }))
    return SummaryAckFoldReport(
        revision=revision,
        artifact_stem=artifact,
        status=status,
        predecessor_status=predecessor_status,
        foldmap_status=foldmap_status,
        foldregistry_status=foldregistry_status,
        surface_ledger_status=surface_ledger_status,
        findings=tuple(findings),
        report_digest=report_digest,
    )
