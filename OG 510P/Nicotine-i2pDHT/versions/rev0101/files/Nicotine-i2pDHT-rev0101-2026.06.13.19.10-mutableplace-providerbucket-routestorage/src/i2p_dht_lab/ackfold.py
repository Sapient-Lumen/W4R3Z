"""rev0061 audit/refactor fold for delivery settlement, ack archive, and ack prune join."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .fenceaudit import audit_fence_fold
from .foldmap import audit_fold_map
from .foldregistry import audit_fold_registry
from .ids import DOMAIN, sha256
from .surfaceledger import audit_surface_ledger, entries_for_revision

ACK_FOLD_DOMAIN = DOMAIN + b":ack-fold-v1:"


@dataclass(frozen=True)
class AckFoldFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class AckFoldReport:
    revision: str
    artifact_stem: str
    status: str
    predecessor_status: str
    foldmap_status: str
    foldregistry_status: str
    surface_ledger_status: str
    findings: tuple[AckFoldFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")


def _exists(root: Path, rel: str, needle: str, findings: list[AckFoldFinding]) -> None:
    path = root / rel
    if not path.exists():
        findings.append(AckFoldFinding("error", "missing_path", rel, "rev0061 ackfold expected this path"))
        return
    text = path.read_text(encoding="utf-8", errors="replace")
    if needle not in text:
        findings.append(AckFoldFinding("error", "missing_needle", rel, f"missing needle {needle!r}"))


def audit_ack_fold(root: str | Path, *, revision: str = "rev0061", artifact_stem: str = "") -> AckFoldReport:
    root_path = Path(root)
    artifact = artifact_stem or root_path.name
    findings: list[AckFoldFinding] = []
    checks = {
        "src/i2p_dht_lab/deliverysettlement.py": "DeliverySettlementDecisionKind",
        "src/i2p_dht_lab/ackarchive.py": "AckArchiveDecisionKind",
        "src/i2p_dht_lab/ackprunejoin.py": "AckPruneJoinDecisionKind",
        "src/i2p_dht_lab/ackfold.py": "audit_ack_fold",
        "tests/test_rev0061_deliverysettlement_ackarchive_prunejoin.py": "test_delivery_settlement_accepts_diverse_exact_boundary",
        "docs/647-rev0061-deliverysettlement-ackarchive-prunejoin.md": "rev0061",
        "docs/648-delivery-settlement-after-fence.md": "delivery settlement",
        "docs/649-ack-archive-restart-memory.md": "ack archive",
        "docs/650-ack-prune-join-boundary.md": "ack prune join",
        "docs/651-ackfold-audit-refactor.md": "ackfold",
    }
    for rel, needle in checks.items():
        _exists(root_path, rel, needle, findings)
    try:
        predecessor = audit_fence_fold(root_path, revision="rev0060", artifact_stem=artifact)
        predecessor_status = predecessor.status
        if predecessor.error_count:
            findings.append(AckFoldFinding("error", "predecessor_failed", "src/i2p_dht_lab/fenceaudit.py", "rev0060 fenceaudit predecessor failed"))
    except Exception as exc:  # pragma: no cover
        predecessor_status = "exception"
        findings.append(AckFoldFinding("error", "predecessor_exception", "src/i2p_dht_lab/fenceaudit.py", str(exc)))
    try:
        fmap = audit_fold_map(root_path, revision=revision, artifact_stem=artifact)
        foldmap_status = fmap.status
        if fmap.error_count:
            findings.append(AckFoldFinding("error", "foldmap_failed", "src/i2p_dht_lab/foldmap.py", "rev0061 fold map failed"))
    except Exception as exc:  # pragma: no cover
        foldmap_status = "exception"
        findings.append(AckFoldFinding("error", "foldmap_exception", "src/i2p_dht_lab/foldmap.py", str(exc)))
    try:
        registry = audit_fold_registry(root_path, revision=revision)
        foldregistry_status = registry.status
        if registry.error_count:
            findings.append(AckFoldFinding("error", "foldregistry_failed", "src/i2p_dht_lab/foldregistry.py", "rev0061 fold registry failed"))
    except Exception as exc:  # pragma: no cover
        foldregistry_status = "exception"
        findings.append(AckFoldFinding("error", "foldregistry_exception", "src/i2p_dht_lab/foldregistry.py", str(exc)))
    try:
        ledger = audit_surface_ledger(root_path, entries_for_revision(revision))
        surface_status = "pass" if ledger.ok else "fail"
        if ledger.error_count:
            findings.append(AckFoldFinding("error", "surface_ledger_failed", "src/i2p_dht_lab/surfaceledger.py", "rev0061 surface ledger failed"))
    except Exception as exc:  # pragma: no cover
        surface_status = "exception"
        findings.append(AckFoldFinding("error", "surface_ledger_exception", "src/i2p_dht_lab/surfaceledger.py", str(exc)))
    status = "pass" if not any(f.severity == "error" for f in findings) else "fail"
    digest = sha256(ACK_FOLD_DOMAIN + b":report:" + bencode({
        b"revision": revision,
        b"artifact": artifact,
        b"status": status,
        b"predecessor": predecessor_status,
        b"foldmap": foldmap_status,
        b"foldregistry": foldregistry_status,
        b"surface": surface_status,
        b"findings": [finding.bvalue() for finding in findings],
    }))
    return AckFoldReport(revision, artifact, status, predecessor_status, foldmap_status, foldregistry_status, surface_status, tuple(findings), digest)
