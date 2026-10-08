"""rev0067 audit/refactor fold for repair settlement / closure archive / repair prune."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .foldmap import audit_fold_map
from .foldregistry import audit_fold_registry
from .ids import DOMAIN, sha256
from .repairpublishfold import audit_repair_publish_fold
from .surfaceledger import audit_surface_ledger, entries_for_revision

REPAIR_SETTLEMENT_FOLD_DOMAIN = DOMAIN + b":repair-settlement-fold-v1:"


@dataclass(frozen=True)
class RepairSettlementFoldFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class RepairSettlementFoldReport:
    revision: str
    artifact_stem: str
    status: str
    predecessor_status: str
    foldmap_status: str
    foldregistry_status: str
    surface_ledger_status: str
    findings: tuple[RepairSettlementFoldFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")


def _exists(root: Path, rel: str, needle: str, findings: list[RepairSettlementFoldFinding]) -> None:
    path = root / rel
    if not path.exists():
        findings.append(RepairSettlementFoldFinding("error", "missing_path", rel, "rev0067 repairsettlementfold expected this path"))
        return
    text = path.read_text(encoding="utf-8", errors="replace")
    if needle not in text:
        findings.append(RepairSettlementFoldFinding("error", "missing_needle", rel, f"missing needle {needle!r}"))


def audit_repair_settlement_fold(root: str | Path, *, revision: str = "rev0067", artifact_stem: str = "") -> RepairSettlementFoldReport:
    root_path = Path(root)
    artifact = artifact_stem or root_path.name
    findings: list[RepairSettlementFoldFinding] = []
    checks = {
        "src/i2p_dht_lab/repairsettlement.py": "RepairSettlementDecisionKind",
        "src/i2p_dht_lab/closurearchive.py": "ClosureArchiveDecisionKind",
        "src/i2p_dht_lab/repairprune.py": "RepairPruneDecisionKind",
        "src/i2p_dht_lab/repairsettlementfold.py": "audit_repair_settlement_fold",
        "tests/test_rev0067_repairsettlement_archive_prune.py": "test_repair_settlement_archive_and_prune_happy_path",
        "docs/708-rev0067-repairsettlement-closurearchive-repairprune.md": "rev0067",
        "docs/709-repair-settlement-after-duplicate-closure.md": "repair settlement",
        "docs/710-closure-archive-restart-memory.md": "closure archive",
        "docs/711-repair-prune-protected-memory.md": "repair prune",
        "docs/712-repairsettlementfold-audit-refactor.md": "repairsettlementfold",
    }
    for rel, needle in checks.items():
        _exists(root_path, rel, needle, findings)
    try:
        predecessor = audit_repair_publish_fold(root_path, revision="rev0066", artifact_stem="x")
        predecessor_status = predecessor.status
        if predecessor.error_count:
            findings.append(RepairSettlementFoldFinding("error", "predecessor_failed", "src/i2p_dht_lab/repairpublishfold.py", "rev0066 predecessor failed"))
    except Exception as exc:  # pragma: no cover
        predecessor_status = "exception"
        findings.append(RepairSettlementFoldFinding("error", "predecessor_exception", "src/i2p_dht_lab/repairpublishfold.py", str(exc)))
    try:
        fmap = audit_fold_map(root_path, revision=revision, artifact_stem=artifact)
        foldmap_status = fmap.status
        if fmap.error_count:
            findings.append(RepairSettlementFoldFinding("error", "foldmap_failed", "src/i2p_dht_lab/foldmap.py", "rev0067 fold map failed"))
    except Exception as exc:  # pragma: no cover
        foldmap_status = "exception"
        findings.append(RepairSettlementFoldFinding("error", "foldmap_exception", "src/i2p_dht_lab/foldmap.py", str(exc)))
    try:
        registry = audit_fold_registry(root_path, revision=revision)
        foldregistry_status = registry.status
        if registry.error_count:
            findings.append(RepairSettlementFoldFinding("error", "foldregistry_failed", "src/i2p_dht_lab/foldregistry.py", "rev0067 fold registry failed"))
    except Exception as exc:  # pragma: no cover
        foldregistry_status = "exception"
        findings.append(RepairSettlementFoldFinding("error", "foldregistry_exception", "src/i2p_dht_lab/foldregistry.py", str(exc)))
    try:
        ledger = audit_surface_ledger(root_path, entries_for_revision(revision))
        surface_ledger_status = "pass" if ledger.ok else "fail"
        if ledger.error_count:
            findings.append(RepairSettlementFoldFinding("error", "surface_ledger_failed", "src/i2p_dht_lab/surfaceledger.py", "rev0067 surface ledger failed"))
    except Exception as exc:  # pragma: no cover
        surface_ledger_status = "exception"
        findings.append(RepairSettlementFoldFinding("error", "surface_ledger_exception", "src/i2p_dht_lab/surfaceledger.py", str(exc)))
    status = "pass" if not any(f.severity == "error" for f in findings) else "fail"
    digest = sha256(REPAIR_SETTLEMENT_FOLD_DOMAIN + b":report:" + bencode({
        b"revision": revision,
        b"artifact": artifact,
        b"status": status,
        b"predecessor": predecessor_status,
        b"foldmap": foldmap_status,
        b"foldregistry": foldregistry_status,
        b"surface": surface_ledger_status,
        b"findings": [finding.bvalue() for finding in findings],
    }))
    return RepairSettlementFoldReport(revision, artifact, status, predecessor_status, foldmap_status, foldregistry_status, surface_ledger_status, tuple(findings), digest)
