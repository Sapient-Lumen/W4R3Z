"""rev0076 audit/refactor fold for summary drain, delivery witness, and settlement fence."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .foldmap import audit_fold_map
from .foldregistry import audit_fold_registry
from .ids import DOMAIN, sha256
from .summarysendfold import audit_summary_send_fold
from .surfaceledger import audit_surface_ledger, entries_for_revision

SUMMARY_DELIVERY_FOLD_DOMAIN = DOMAIN + b":summary-delivery-fold-v1:"


@dataclass(frozen=True)
class SummaryDeliveryFoldFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class SummaryDeliveryFoldReport:
    revision: str
    artifact_stem: str
    status: str
    predecessor_status: str
    foldmap_status: str
    foldregistry_status: str
    surface_ledger_status: str
    findings: tuple[SummaryDeliveryFoldFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")


def _exists(root: Path, rel: str, needle: str, findings: list[SummaryDeliveryFoldFinding]) -> None:
    path = root / rel
    if not path.exists():
        findings.append(SummaryDeliveryFoldFinding("error", "missing_path", rel, "rev0076 expected this path"))
        return
    if needle not in path.read_text(encoding="utf-8", errors="replace"):
        findings.append(SummaryDeliveryFoldFinding("error", "missing_needle", rel, f"missing needle {needle!r}"))


def audit_summary_delivery_fold(root: str | Path, *, revision: str = "rev0076", artifact_stem: str = "") -> SummaryDeliveryFoldReport:
    root_path = Path(root)
    artifact = artifact_stem or root_path.name
    findings: list[SummaryDeliveryFoldFinding] = []
    checks = {
        "src/i2p_dht_lab/summarydrain.py": "SummaryDrainDecisionKind",
        "src/i2p_dht_lab/summarydeliverywitness.py": "SummaryDeliveryDecisionKind",
        "src/i2p_dht_lab/settlementfence.py": "SettlementFenceDecisionKind",
        "src/i2p_dht_lab/summarydeliveryfold.py": "audit_summary_delivery_fold",
        "tests/test_rev0076_summarydrain_deliverywitness_settlementfence.py": "test_summary_delivery_settlement_happy_path",
        "docs/798-rev0076-summarydrain-deliverywitness-settlementfence.md": "rev0076",
        "docs/799-summary-drain-after-canary.md": "summary drain",
        "docs/800-summary-delivery-witness.md": "delivery witness",
        "docs/801-settlement-fence-after-delivery.md": "settlement fence",
        "docs/802-summarydeliveryfold-audit-refactor.md": "summarydeliveryfold",
    }
    for rel, needle in checks.items():
        _exists(root_path, rel, needle, findings)

    try:
        predecessor = audit_summary_send_fold(root_path, revision="rev0075", artifact_stem=artifact)
        predecessor_status = predecessor.status
        if predecessor.error_count:
            findings.append(SummaryDeliveryFoldFinding("error", "predecessor_failed", "src/i2p_dht_lab/summarysendfold.py", "rev0075 predecessor failed"))
    except Exception as exc:  # pragma: no cover - defensive audit surface
        predecessor_status = "exception"
        findings.append(SummaryDeliveryFoldFinding("error", "predecessor_exception", "src/i2p_dht_lab/summarysendfold.py", str(exc)))

    try:
        fmap = audit_fold_map(root_path, revision=revision, artifact_stem=artifact)
        foldmap_status = fmap.status
        if fmap.error_count:
            findings.append(SummaryDeliveryFoldFinding("error", "foldmap_failed", "src/i2p_dht_lab/foldmap.py", "rev0076 fold map failed"))
    except Exception as exc:  # pragma: no cover
        foldmap_status = "exception"
        findings.append(SummaryDeliveryFoldFinding("error", "foldmap_exception", "src/i2p_dht_lab/foldmap.py", str(exc)))

    try:
        registry = audit_fold_registry(root_path, revision=revision)
        foldregistry_status = registry.status
        if registry.error_count:
            findings.append(SummaryDeliveryFoldFinding("error", "foldregistry_failed", "src/i2p_dht_lab/foldregistry.py", "rev0076 fold registry failed"))
    except Exception as exc:  # pragma: no cover
        foldregistry_status = "exception"
        findings.append(SummaryDeliveryFoldFinding("error", "foldregistry_exception", "src/i2p_dht_lab/foldregistry.py", str(exc)))

    try:
        ledger = audit_surface_ledger(root_path, entries_for_revision(revision))
        surface_ledger_status = "pass" if ledger.ok else "fail"
        if ledger.error_count:
            findings.append(SummaryDeliveryFoldFinding("error", "surface_ledger_failed", "src/i2p_dht_lab/surfaceledger.py", "rev0076 surface ledger failed"))
    except Exception as exc:  # pragma: no cover
        surface_ledger_status = "exception"
        findings.append(SummaryDeliveryFoldFinding("error", "surface_ledger_exception", "src/i2p_dht_lab/surfaceledger.py", str(exc)))

    status = "pass" if not any(f.severity == "error" for f in findings) else "fail"
    report_digest = sha256(SUMMARY_DELIVERY_FOLD_DOMAIN + b":report:" + bencode({
        b"revision": revision,
        b"artifact": artifact,
        b"status": status,
        b"predecessor": predecessor_status,
        b"foldmap": foldmap_status,
        b"registry": foldregistry_status,
        b"surface": surface_ledger_status,
        b"findings": [finding.bvalue() for finding in findings],
    }))
    return SummaryDeliveryFoldReport(
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
