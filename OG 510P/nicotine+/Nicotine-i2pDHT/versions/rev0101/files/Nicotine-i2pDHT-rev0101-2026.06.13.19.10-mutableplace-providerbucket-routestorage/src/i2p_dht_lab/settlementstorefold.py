"""rev0059 audit/refactor fold for settlement store, tomb repair join, and canary join."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .finalityfold import audit_finality_fold
from .foldmap import audit_fold_map
from .foldregistry import audit_fold_registry
from .ids import DOMAIN, sha256
from .settlementfold import audit_settlement_fold
from .surfaceledger import audit_surface_ledger, entries_for_revision

SETTLEMENT_STORE_FOLD_DOMAIN = DOMAIN + b":settlement-store-fold-v1:"


@dataclass(frozen=True)
class SettlementStoreFoldFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class SettlementStoreFoldReport:
    revision: str
    artifact_stem: str
    status: str
    finality_predecessor_status: str
    settlement_branch_status: str
    foldmap_status: str
    foldregistry_status: str
    surface_ledger_status: str
    findings: tuple[SettlementStoreFoldFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")


def _exists(root: Path, rel: str, needle: str, findings: list[SettlementStoreFoldFinding]) -> None:
    path = root / rel
    if not path.exists():
        findings.append(SettlementStoreFoldFinding("error", "missing_path", rel, "rev0059 settlement-store fold expected this path"))
        return
    text = path.read_text(encoding="utf-8", errors="replace")
    if needle not in text:
        findings.append(SettlementStoreFoldFinding("error", "missing_needle", rel, f"missing needle {needle!r}"))


def audit_settlementstore_fold(root: str | Path, *, revision: str = "rev0059", artifact_stem: str = "") -> SettlementStoreFoldReport:
    root_path = Path(root)
    artifact = artifact_stem or root_path.name
    findings: list[SettlementStoreFoldFinding] = []
    checks = {
        "src/i2p_dht_lab/settlementstore.py": "SettlementStoreDecisionKind",
        "src/i2p_dht_lab/tombrepairjoin.py": "TombRepairJoinDecisionKind",
        "src/i2p_dht_lab/canaryjoin.py": "CanaryJoinDecisionKind",
        "src/i2p_dht_lab/settlementstorefold.py": "audit_settlementstore_fold",
        "src/i2p_dht_lab/settlementlane.py": "SettlementDecisionKind",
        "src/i2p_dht_lab/attestationpack.py": "AttestationPackDecisionKind",
        "src/i2p_dht_lab/tombstonerepair.py": "TombstoneRepairDecisionKind",
        "tests/test_rev0059_settlementstore_tombmesh_canaryjoin.py": "test_settlement_store_accepts_terminal_branch_join",
        "tests/test_rev0058_settlement_attestation_tombrepair.py": "test_settlement_accepts_retry_hold_without_erasing_dead_letter",
        "docs/620-rev0059-settlementstore-tombmesh-canaryjoin.md": "rev0059",
        "docs/621-settlement-store-branch-join.md": "settlement store",
        "docs/622-tomb-repair-join-after-prune.md": "tombstone",
        "docs/623-canary-join-after-settlement.md": "canary",
        "docs/624-settlementstorefold-audit-refactor.md": "settlementstorefold",
    }
    for rel, needle in checks.items():
        _exists(root_path, rel, needle, findings)
    try:
        finality = audit_finality_fold(root_path, revision="rev0058", artifact_stem=artifact)
        finality_status = finality.status
        if finality.error_count:
            findings.append(SettlementStoreFoldFinding("error", "finality_predecessor_failed", "src/i2p_dht_lab/finalityfold.py", "rev0058 finality predecessor failed"))
    except Exception as exc:  # pragma: no cover
        finality_status = "exception"
        findings.append(SettlementStoreFoldFinding("error", "finality_predecessor_exception", "src/i2p_dht_lab/finalityfold.py", str(exc)))
    try:
        settlement = audit_settlement_fold(root_path, revision=revision, artifact_stem=artifact)
        settlement_status = settlement.status
        if settlement.error_count:
            findings.append(SettlementStoreFoldFinding("error", "settlement_branch_failed", "src/i2p_dht_lab/settlementfold.py", "folded settlement branchlet failed"))
    except Exception as exc:  # pragma: no cover
        settlement_status = "exception"
        findings.append(SettlementStoreFoldFinding("error", "settlement_branch_exception", "src/i2p_dht_lab/settlementfold.py", str(exc)))
    try:
        fmap = audit_fold_map(root_path, revision=revision, artifact_stem=artifact)
        foldmap_status = fmap.status
        if fmap.error_count:
            findings.append(SettlementStoreFoldFinding("error", "foldmap_failed", "src/i2p_dht_lab/foldmap.py", "rev0059 fold map failed"))
    except Exception as exc:  # pragma: no cover
        foldmap_status = "exception"
        findings.append(SettlementStoreFoldFinding("error", "foldmap_exception", "src/i2p_dht_lab/foldmap.py", str(exc)))
    try:
        registry = audit_fold_registry(root_path, revision=revision)
        foldregistry_status = registry.status
        if registry.error_count:
            findings.append(SettlementStoreFoldFinding("error", "foldregistry_failed", "src/i2p_dht_lab/foldregistry.py", "rev0059 fold registry failed"))
    except Exception as exc:  # pragma: no cover
        foldregistry_status = "exception"
        findings.append(SettlementStoreFoldFinding("error", "foldregistry_exception", "src/i2p_dht_lab/foldregistry.py", str(exc)))
    try:
        ledger = audit_surface_ledger(root_path, entries_for_revision(revision))
        surface_status = "pass" if ledger.ok else "fail"
        if ledger.error_count:
            findings.append(SettlementStoreFoldFinding("error", "surface_ledger_failed", "src/i2p_dht_lab/surfaceledger.py", "rev0059 surface ledger failed"))
    except Exception as exc:  # pragma: no cover
        surface_status = "exception"
        findings.append(SettlementStoreFoldFinding("error", "surface_ledger_exception", "src/i2p_dht_lab/surfaceledger.py", str(exc)))
    status = "pass" if not any(f.severity == "error" for f in findings) else "fail"
    digest = sha256(SETTLEMENT_STORE_FOLD_DOMAIN + b":report:" + bencode({
        b"revision": revision,
        b"artifact": artifact,
        b"status": status,
        b"finality": finality_status,
        b"settlement": settlement_status,
        b"foldmap": foldmap_status,
        b"foldregistry": foldregistry_status,
        b"surface": surface_status,
        b"findings": [finding.bvalue() for finding in findings],
    }))
    return SettlementStoreFoldReport(revision, artifact, status, finality_status, settlement_status, foldmap_status, foldregistry_status, surface_status, tuple(findings), digest)
