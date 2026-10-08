"""rev0064 audit/refactor fold for retry publication and idempotency mesh."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .foldmap import audit_fold_map
from .foldregistry import audit_fold_registry
from .idempotencymesh import IDEMPOTENCY_MESH_DOMAIN
from .ids import DOMAIN, sha256
from .lateackfold import audit_late_ack_fold
from .surfaceledger import audit_surface_ledger, entries_for_revision

RETRY_PUBLISH_FOLD_DOMAIN = DOMAIN + b":retry-publish-fold-v1:"


@dataclass(frozen=True)
class RetryPublishFoldFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class RetryPublishFoldReport:
    revision: str
    artifact_stem: str
    status: str
    predecessor_status: str
    foldmap_status: str
    foldregistry_status: str
    surface_ledger_status: str
    findings: tuple[RetryPublishFoldFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")


def _exists(root: Path, rel: str, needle: str, findings: list[RetryPublishFoldFinding]) -> None:
    path = root / rel
    if not path.exists():
        findings.append(RetryPublishFoldFinding("error", "missing_path", rel, "rev0064 retrypublishfold expected this path"))
        return
    text = path.read_text(encoding="utf-8", errors="replace")
    if needle not in text:
        findings.append(RetryPublishFoldFinding("error", "missing_needle", rel, f"missing needle {needle!r}"))


def audit_retry_publish_fold(root: str | Path, *, revision: str = "rev0064", artifact_stem: str = "") -> RetryPublishFoldReport:
    root_path = Path(root)
    artifact = artifact_stem or root_path.name
    findings: list[RetryPublishFoldFinding] = []
    checks = {
        "src/i2p_dht_lab/retrypublish.py": "RetryPublishDecisionKind",
        "src/i2p_dht_lab/idempotencymesh.py": "IdempotencyMeshDecisionKind",
        "src/i2p_dht_lab/deliveryrepairmesh.py": "DeliveryRepairMeshDecisionKind",
        "src/i2p_dht_lab/retrypublishfold.py": "audit_retry_publish_fold",
        "tests/test_rev0064_retrypublish_idempotencymesh_deliveryrepair.py": "test_retry_delivered_stages_publication_and_mesh_accepts_retry_only",
        "docs/678-rev0064-retrypublish-idempotencymesh-deliveryrepair.md": "rev0064",
        "docs/679-retry-publication-outbox.md": "retry publication",
        "docs/680-idempotency-mesh-lineage.md": "idempotency mesh",
        "docs/681-delivery-repair-remote-witness.md": "remote witness",
        "docs/682-retrypublishfold-audit-refactor.md": "retrypublishfold",
    }
    for rel, needle in checks.items():
        _exists(root_path, rel, needle, findings)
    try:
        predecessor = audit_late_ack_fold(root_path, revision="rev0063", artifact_stem=artifact)
        predecessor_status = predecessor.status
        if predecessor.error_count:
            findings.append(RetryPublishFoldFinding("error", "predecessor_failed", "src/i2p_dht_lab/lateackfold.py", "rev0063 predecessor failed"))
    except Exception as exc:  # pragma: no cover
        predecessor_status = "exception"
        findings.append(RetryPublishFoldFinding("error", "predecessor_exception", "src/i2p_dht_lab/lateackfold.py", str(exc)))
    try:
        fmap = audit_fold_map(root_path, revision=revision, artifact_stem=artifact)
        foldmap_status = fmap.status
        if fmap.error_count:
            findings.append(RetryPublishFoldFinding("error", "foldmap_failed", "src/i2p_dht_lab/foldmap.py", "rev0064 fold map failed"))
    except Exception as exc:  # pragma: no cover
        foldmap_status = "exception"
        findings.append(RetryPublishFoldFinding("error", "foldmap_exception", "src/i2p_dht_lab/foldmap.py", str(exc)))
    try:
        registry = audit_fold_registry(root_path, revision=revision)
        foldregistry_status = registry.status
        if registry.error_count:
            findings.append(RetryPublishFoldFinding("error", "foldregistry_failed", "src/i2p_dht_lab/foldregistry.py", "rev0064 fold registry failed"))
    except Exception as exc:  # pragma: no cover
        foldregistry_status = "exception"
        findings.append(RetryPublishFoldFinding("error", "foldregistry_exception", "src/i2p_dht_lab/foldregistry.py", str(exc)))
    try:
        ledger = audit_surface_ledger(root_path, entries_for_revision(revision))
        surface_ledger_status = "pass" if ledger.ok else "fail"
        if ledger.error_count:
            findings.append(RetryPublishFoldFinding("error", "surface_ledger_failed", "src/i2p_dht_lab/surfaceledger.py", "rev0064 surface ledger failed"))
    except Exception as exc:  # pragma: no cover
        surface_ledger_status = "exception"
        findings.append(RetryPublishFoldFinding("error", "surface_ledger_exception", "src/i2p_dht_lab/surfaceledger.py", str(exc)))
    status = "pass" if not any(f.severity == "error" for f in findings) else "fail"
    digest = sha256(RETRY_PUBLISH_FOLD_DOMAIN + b":report:" + bencode({
        b"revision": revision,
        b"artifact": artifact,
        b"status": status,
        b"predecessor": predecessor_status,
        b"foldmap": foldmap_status,
        b"foldregistry": foldregistry_status,
        b"surface": surface_ledger_status,
        b"findings": [finding.bvalue() for finding in findings],
        b"mesh_domain": IDEMPOTENCY_MESH_DOMAIN,
    }))
    return RetryPublishFoldReport(revision, artifact, status, predecessor_status, foldmap_status, foldregistry_status, surface_ledger_status, tuple(findings), digest)
