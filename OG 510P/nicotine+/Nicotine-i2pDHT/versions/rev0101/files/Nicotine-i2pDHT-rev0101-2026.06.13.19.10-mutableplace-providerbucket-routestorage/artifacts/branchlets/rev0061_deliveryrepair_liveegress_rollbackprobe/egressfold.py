"""rev0061 audit/refactor fold for delivery repair, rollback probes, and live egress."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .fenceaudit import audit_fence_fold
from .foldmap import audit_fold_map
from .foldregistry import audit_fold_registry
from .ids import DOMAIN, sha256
from .surfaceledger import audit_surface_ledger, entries_for_revision

EGRESS_FOLD_DOMAIN = DOMAIN + b":egress-fold-v1:"


@dataclass(frozen=True)
class EgressFoldFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class EgressFoldReport:
    revision: str
    artifact_stem: str
    status: str
    predecessor_status: str
    foldmap_status: str
    foldregistry_status: str
    surface_ledger_status: str
    findings: tuple[EgressFoldFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")


def _exists(root: Path, rel: str, needle: str, findings: list[EgressFoldFinding]) -> None:
    path = root / rel
    if not path.exists():
        findings.append(EgressFoldFinding("error", "missing_path", rel, "rev0061 egress fold expected this path"))
        return
    text = path.read_text(encoding="utf-8", errors="replace")
    if needle not in text:
        findings.append(EgressFoldFinding("error", "missing_needle", rel, f"missing needle {needle!r}"))


def audit_egress_fold(root: str | Path, *, revision: str = "rev0061", artifact_stem: str = "") -> EgressFoldReport:
    root_path = Path(root)
    artifact = artifact_stem or root_path.name
    findings: list[EgressFoldFinding] = []
    checks = {
        "src/i2p_dht_lab/deliveryrepair.py": "DeliveryRepairDecisionKind",
        "src/i2p_dht_lab/rollbackprobe.py": "RollbackProbeDecisionKind",
        "src/i2p_dht_lab/liveegress.py": "LiveEgressDecisionKind",
        "src/i2p_dht_lab/egressfold.py": "audit_egress_fold",
        "tests/test_rev0061_deliveryrepair_liveegress_rollbackprobe.py": "test_delivery_repair_accepts_missing_ack_probe",
        "docs/647-rev0061-deliveryrepair-liveegress-rollbackprobe.md": "rev0061",
        "docs/648-delivery-repair-after-missing-ack.md": "delivery repair",
        "docs/649-rollback-probe-before-retry.md": "rollback probe",
        "docs/650-live-egress-retry-gate.md": "live egress",
        "docs/651-egressfold-audit-refactor.md": "egressfold",
    }
    for rel, needle in checks.items():
        _exists(root_path, rel, needle, findings)
    try:
        predecessor = audit_fence_fold(root_path, revision="rev0060", artifact_stem=artifact)
        predecessor_status = predecessor.status
        if predecessor.error_count:
            findings.append(EgressFoldFinding("error", "predecessor_failed", "src/i2p_dht_lab/fenceaudit.py", "rev0060 fenceaudit predecessor failed"))
    except Exception as exc:  # pragma: no cover
        predecessor_status = "exception"
        findings.append(EgressFoldFinding("error", "predecessor_exception", "src/i2p_dht_lab/fenceaudit.py", str(exc)))
    try:
        fmap = audit_fold_map(root_path, revision=revision, artifact_stem=artifact)
        foldmap_status = fmap.status
        if fmap.error_count:
            findings.append(EgressFoldFinding("error", "foldmap_failed", "src/i2p_dht_lab/foldmap.py", "rev0061 fold map failed"))
    except Exception as exc:  # pragma: no cover
        foldmap_status = "exception"
        findings.append(EgressFoldFinding("error", "foldmap_exception", "src/i2p_dht_lab/foldmap.py", str(exc)))
    try:
        registry = audit_fold_registry(root_path, revision=revision)
        foldregistry_status = registry.status
        if registry.error_count:
            findings.append(EgressFoldFinding("error", "foldregistry_failed", "src/i2p_dht_lab/foldregistry.py", "rev0061 fold registry failed"))
    except Exception as exc:  # pragma: no cover
        foldregistry_status = "exception"
        findings.append(EgressFoldFinding("error", "foldregistry_exception", "src/i2p_dht_lab/foldregistry.py", str(exc)))
    try:
        ledger = audit_surface_ledger(root_path, entries_for_revision(revision))
        surface_status = "pass" if ledger.ok else "fail"
        if ledger.error_count:
            findings.append(EgressFoldFinding("error", "surface_ledger_failed", "src/i2p_dht_lab/surfaceledger.py", "rev0061 surface ledger failed"))
    except Exception as exc:  # pragma: no cover
        surface_status = "exception"
        findings.append(EgressFoldFinding("error", "surface_ledger_exception", "src/i2p_dht_lab/surfaceledger.py", str(exc)))
    status = "pass" if not any(f.severity == "error" for f in findings) else "fail"
    digest = sha256(EGRESS_FOLD_DOMAIN + b":report:" + bencode({
        b"revision": revision,
        b"artifact": artifact,
        b"status": status,
        b"predecessor": predecessor_status,
        b"foldmap": foldmap_status,
        b"foldregistry": foldregistry_status,
        b"surface": surface_status,
        b"findings": [finding.bvalue() for finding in findings],
    }))
    return EgressFoldReport(revision, artifact, status, predecessor_status, foldmap_status, foldregistry_status, surface_status, tuple(findings), digest)
