"""rev0066 audit/refactor fold for repair publish / ACK / closure lane."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .foldmap import audit_fold_map
from .foldregistry import audit_fold_registry
from .ids import DOMAIN, sha256
from .remoterepairfold import audit_remote_repair_fold
from .surfaceledger import audit_surface_ledger, entries_for_revision

REPAIR_PUBLISH_FOLD_DOMAIN = DOMAIN + b":repair-publish-fold-v1:"


@dataclass(frozen=True)
class RepairPublishFoldFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class RepairPublishFoldReport:
    revision: str
    artifact_stem: str
    status: str
    predecessor_status: str
    foldmap_status: str
    foldregistry_status: str
    surface_ledger_status: str
    findings: tuple[RepairPublishFoldFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")


def _exists(root: Path, rel: str, needle: str, findings: list[RepairPublishFoldFinding]) -> None:
    path = root / rel
    if not path.exists():
        findings.append(RepairPublishFoldFinding("error", "missing_path", rel, "rev0066 repairpublishfold expected this path"))
        return
    text = path.read_text(encoding="utf-8", errors="replace")
    if needle not in text:
        findings.append(RepairPublishFoldFinding("error", "missing_needle", rel, f"missing needle {needle!r}"))


def audit_repair_publish_fold(root: str | Path, *, revision: str = "rev0066", artifact_stem: str = "") -> RepairPublishFoldReport:
    root_path = Path(root)
    artifact = artifact_stem or root_path.name
    findings: list[RepairPublishFoldFinding] = []
    checks = {
        "src/i2p_dht_lab/repairpublishgate.py": "RepairPublishDecisionKind",
        "src/i2p_dht_lab/repairackledger.py": "RepairAckDecisionKind",
        "src/i2p_dht_lab/duplicateclosure.py": "DuplicateClosureDecisionKind",
        "src/i2p_dht_lab/repairpublishfold.py": "audit_repair_publish_fold",
        "tests/test_rev0066_repairpublish_ackclosure.py": "test_repair_publish_ack_and_duplicate_closure_happy_path",
        "docs/698-rev0066-repairpublish-ackclosure-duplicatefinality.md": "rev0066",
        "docs/699-repair-publish-gate-after-cooldown.md": "repair publish gate",
        "docs/700-repair-ack-ledger.md": "repair ACK ledger",
        "docs/701-duplicate-closure-finality.md": "duplicate closure",
        "docs/702-repairpublishfold-audit-refactor.md": "repairpublishfold",
    }
    for rel, needle in checks.items():
        _exists(root_path, rel, needle, findings)
    try:
        predecessor = audit_remote_repair_fold(root_path, revision="rev0065", artifact_stem="x")
        predecessor_status = predecessor.status
        if predecessor.error_count:
            findings.append(RepairPublishFoldFinding("error", "predecessor_failed", "src/i2p_dht_lab/remoterepairfold.py", "rev0065 predecessor failed"))
    except Exception as exc:  # pragma: no cover
        predecessor_status = "exception"
        findings.append(RepairPublishFoldFinding("error", "predecessor_exception", "src/i2p_dht_lab/remoterepairfold.py", str(exc)))
    try:
        fmap = audit_fold_map(root_path, revision=revision, artifact_stem=artifact)
        foldmap_status = fmap.status
        if fmap.error_count:
            findings.append(RepairPublishFoldFinding("error", "foldmap_failed", "src/i2p_dht_lab/foldmap.py", "rev0066 fold map failed"))
    except Exception as exc:  # pragma: no cover
        foldmap_status = "exception"
        findings.append(RepairPublishFoldFinding("error", "foldmap_exception", "src/i2p_dht_lab/foldmap.py", str(exc)))
    try:
        registry = audit_fold_registry(root_path, revision=revision)
        foldregistry_status = registry.status
        if registry.error_count:
            findings.append(RepairPublishFoldFinding("error", "foldregistry_failed", "src/i2p_dht_lab/foldregistry.py", "rev0066 fold registry failed"))
    except Exception as exc:  # pragma: no cover
        foldregistry_status = "exception"
        findings.append(RepairPublishFoldFinding("error", "foldregistry_exception", "src/i2p_dht_lab/foldregistry.py", str(exc)))
    try:
        ledger = audit_surface_ledger(root_path, entries_for_revision(revision))
        surface_ledger_status = "pass" if ledger.ok else "fail"
        if ledger.error_count:
            findings.append(RepairPublishFoldFinding("error", "surface_ledger_failed", "src/i2p_dht_lab/surfaceledger.py", "rev0066 surface ledger failed"))
    except Exception as exc:  # pragma: no cover
        surface_ledger_status = "exception"
        findings.append(RepairPublishFoldFinding("error", "surface_ledger_exception", "src/i2p_dht_lab/surfaceledger.py", str(exc)))
    status = "pass" if not any(f.severity == "error" for f in findings) else "fail"
    digest = sha256(REPAIR_PUBLISH_FOLD_DOMAIN + b":report:" + bencode({
        b"revision": revision,
        b"artifact": artifact,
        b"status": status,
        b"predecessor": predecessor_status,
        b"foldmap": foldmap_status,
        b"foldregistry": foldregistry_status,
        b"surface": surface_ledger_status,
        b"findings": [finding.bvalue() for finding in findings],
    }))
    return RepairPublishFoldReport(revision, artifact, status, predecessor_status, foldmap_status, foldregistry_status, surface_ledger_status, tuple(findings), digest)
