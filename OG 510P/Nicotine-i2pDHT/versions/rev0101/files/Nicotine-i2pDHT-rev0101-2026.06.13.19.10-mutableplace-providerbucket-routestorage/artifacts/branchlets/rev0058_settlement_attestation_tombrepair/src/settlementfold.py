"""rev0058 settlement fold audit."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .ids import DOMAIN, sha256

SETTLEMENT_FOLD_DOMAIN = DOMAIN + b":settlement-fold-v1:"


@dataclass(frozen=True)
class SettlementFoldFinding:
    severity: str
    code: str
    path: str
    detail: str


@dataclass(frozen=True)
class SettlementFoldReport:
    revision: str
    status: str
    findings: tuple[SettlementFoldFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == "warning")


def _need(root: Path, findings: list[SettlementFoldFinding], path: str, needle: str) -> None:
    target = root / path
    if not target.exists():
        findings.append(SettlementFoldFinding("error", "missing_path", path, "required settlement surface missing"))
        return
    text = target.read_text(encoding="utf-8", errors="replace")
    if needle not in text:
        findings.append(SettlementFoldFinding("error", "missing_needle", path, f"missing needle {needle!r}"))


def audit_settlement_fold(root: Path, *, revision: str = "rev0058", artifact_stem: str | None = None) -> SettlementFoldReport:
    findings: list[SettlementFoldFinding] = []
    expected_stem = artifact_stem or root.name
    checks = {
        "src/i2p_dht_lab/settlementlane.py": "SettlementDecisionKind",
        "src/i2p_dht_lab/attestationpack.py": "AttestationPackDecisionKind",
        "src/i2p_dht_lab/tombstonerepair.py": "TombstoneRepairDecisionKind",
        "src/i2p_dht_lab/settlementfold.py": "audit_settlement_fold",
        "tests/test_rev0058_settlement_attestation_tombrepair.py": "test_settlement_accepts_retry_hold_without_erasing_dead_letter",
        "docs/610-rev0058-settleledger-attestationpack-tombrepair.md": "rev0058",
        "docs/611-settlement-lane-after-reconcile.md": "settlement",
        "docs/612-attestation-pack-not-oracle.md": "attestation",
        "docs/613-tombstone-repair-after-settlement.md": "tombstone",
        "docs/614-settlementfold-audit-refactor.md": "settlementfold",
        "PUBLIC_SURFACE.json": revision,
        "HEAD_REGISTRY.json": revision,
        "VERSION": revision,
    }
    for path, needle in checks.items():
        _need(root, findings, path, needle)
    if expected_stem and expected_stem not in (root / "PUBLIC_SURFACE.json").read_text(encoding="utf-8", errors="replace"):
        findings.append(SettlementFoldFinding("error", "artifact_stem_drift", "PUBLIC_SURFACE.json", "current artifact stem is not public"))
    predecessor = (root / "src/i2p_dht_lab/reconcilefold.py")
    if predecessor.exists() and "audit_reconcile_fold" not in predecessor.read_text(encoding="utf-8", errors="replace"):
        findings.append(SettlementFoldFinding("error", "predecessor_drift", "src/i2p_dht_lab/reconcilefold.py", "rev0057 predecessor fold lost audit function"))
    status = "pass" if not any(f.severity == "error" for f in findings) else "fail"
    body = {b"revision": revision, b"status": status, b"findings": [{b"severity": f.severity, b"code": f.code, b"path": f.path, b"detail": f.detail} for f in findings]}
    return SettlementFoldReport(revision, status, tuple(findings), sha256(SETTLEMENT_FOLD_DOMAIN + b":report:" + bencode(body)))
