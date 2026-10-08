"""rev0049 public-outbox / audit-gap fold audit."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .foldmap import audit_fold_map
from .foldregistry import audit_fold_registry
from .ids import DOMAIN, sha256
from .shadowauditfold import audit_shadow_audit_fold
from .surfaceledger import audit_surface_ledger, entries_for_revision

OUTBOX_FOLD_DOMAIN = DOMAIN + b":outbox-fold-v1:"

REV0049_PATHS = (
    "src/i2p_dht_lab/publicoutbox.py",
    "src/i2p_dht_lab/auditgap.py",
    "src/i2p_dht_lab/outboxfold.py",
    "tests/test_rev0049_publicoutbox_auditgap_fold.py",
    "docs/514-rev0049-outboxlane-auditgap-fold.md",
    "docs/515-public-outbox-side-effect-staging.md",
    "docs/516-audit-gap-repair-planning.md",
    "docs/517-outboxfold-audit-refactor.md",
)
NEEDLES = ("rev0049", "publicoutbox", "auditgap", "outboxfold")


@dataclass(frozen=True)
class OutboxFoldFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class OutboxFoldReport:
    revision: str
    artifact_stem: str
    status: str
    predecessor_status: str
    foldmap_status: str
    registry_status: str
    surface_ledger_status: str
    findings: tuple[OutboxFoldFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")


def _contains(path: Path, needle: str) -> bool:
    try:
        return needle in path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return False


def audit_outbox_fold(root: str | Path, *, revision: str = "rev0049", artifact_stem: str | None = None) -> OutboxFoldReport:
    if revision != "rev0049":
        raise ValueError("outboxfold currently audits rev0049")
    root_path = Path(root)
    artifact_stem = artifact_stem or root_path.name
    findings: list[OutboxFoldFinding] = []
    for rel in REV0049_PATHS:
        if not (root_path / rel).exists():
            findings.append(OutboxFoldFinding("error", "missing_rev0049_path", rel, "rev0049 outbox/audit-gap path is absent"))
    for surface_path in ("PUBLIC_SURFACE.json", "HEAD_REGISTRY.json", "docs/00-index.md"):
        for needle in NEEDLES:
            if not _contains(root_path / surface_path, needle):
                findings.append(OutboxFoldFinding("error", "surface_missing_needle", surface_path, f"missing {needle}"))
    try:
        predecessor = audit_shadow_audit_fold(root_path, revision="rev0048", artifact_stem=artifact_stem)
        predecessor_status = predecessor.status
        if predecessor.error_count:
            findings.append(OutboxFoldFinding("error", "shadowauditfold_failed", "src/i2p_dht_lab/shadowauditfold.py", "rev0048 predecessor fold failed"))
    except Exception as exc:  # pragma: no cover
        predecessor_status = "exception"
        findings.append(OutboxFoldFinding("error", "shadowauditfold_exception", "src/i2p_dht_lab/shadowauditfold.py", str(exc)))
    try:
        foldmap = audit_fold_map(root_path, revision="rev0049", artifact_stem=artifact_stem)
        foldmap_status = foldmap.status
        if foldmap.error_count:
            findings.append(OutboxFoldFinding("error", "foldmap_failed", "src/i2p_dht_lab/foldmap.py", "rev0049 foldmap failed"))
    except Exception as exc:  # pragma: no cover
        foldmap_status = "exception"
        findings.append(OutboxFoldFinding("error", "foldmap_exception", "src/i2p_dht_lab/foldmap.py", str(exc)))
    try:
        registry = audit_fold_registry(root_path, revision="rev0049")
        registry_status = registry.status
        if registry.error_count:
            findings.append(OutboxFoldFinding("error", "foldregistry_failed", "src/i2p_dht_lab/foldregistry.py", "rev0049 fold registry failed"))
    except Exception as exc:  # pragma: no cover
        registry_status = "exception"
        findings.append(OutboxFoldFinding("error", "foldregistry_exception", "src/i2p_dht_lab/foldregistry.py", str(exc)))
    try:
        ledger = audit_surface_ledger(root_path, entries_for_revision("rev0049"))
        surface_status = "pass" if ledger.ok else "fail"
        if ledger.error_count:
            findings.append(OutboxFoldFinding("error", "surface_ledger_failed", "src/i2p_dht_lab/surfaceledger.py", "rev0049 surface ledger failed"))
    except Exception as exc:  # pragma: no cover
        surface_status = "exception"
        findings.append(OutboxFoldFinding("error", "surface_ledger_exception", "src/i2p_dht_lab/surfaceledger.py", str(exc)))
    status = "pass" if not any(finding.severity == "error" for finding in findings) else "fail"
    digest = sha256(OUTBOX_FOLD_DOMAIN + b":report:" + bencode({
        b"revision": revision,
        b"artifact": artifact_stem,
        b"status": status,
        b"predecessor": predecessor_status,
        b"foldmap": foldmap_status,
        b"registry": registry_status,
        b"surface": surface_status,
        b"findings": [finding.bvalue() for finding in findings],
    }))
    return OutboxFoldReport(revision, artifact_stem, status, predecessor_status, foldmap_status, registry_status, surface_status, tuple(findings), digest)
