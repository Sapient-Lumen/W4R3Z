"""rev0046 moderation/redress/bridge-ledger fold audit."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .bridgeepochfold import audit_bridge_epoch_fold
from .foldmap import audit_fold_map
from .foldregistry import audit_fold_registry
from .ids import DOMAIN, sha256
from .surfaceledger import audit_surface_ledger, entries_for_revision

MODERATION_FOLD_DOMAIN = DOMAIN + b":moderation-fold-v1:"


@dataclass(frozen=True)
class ModerationFoldFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class ModerationFoldReport:
    revision: str
    artifact_stem: str
    status: str
    predecessor_status: str
    foldmap_status: str
    registry_status: str
    surface_ledger_status: str
    findings: tuple[ModerationFoldFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")


REV0046_PATHS = (
    "src/i2p_dht_lab/moderationquarantine.py",
    "src/i2p_dht_lab/redresslane.py",
    "src/i2p_dht_lab/bridgeledger.py",
    "src/i2p_dht_lab/moderationfold.py",
    "tests/test_rev0046_moderation_redress_bridgeledger.py",
    "docs/479-rev0046-moderationquarantine-redresslane-bridgeledger.md",
    "docs/480-moderation-quarantine-as-allegation.md",
    "docs/481-redress-lane-appeal-receipts.md",
    "docs/482-bridge-ledger-policy-replay.md",
    "docs/483-moderationfold-audit-refactor.md",
)
NEEDLES = ("rev0046", "moderationquarantine", "redresslane", "bridgeledger", "moderationfold")


def _contains(path: Path, needle: str) -> bool:
    try:
        return needle in path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return False


def audit_moderation_fold(root: str | Path, *, revision: str = "rev0046", artifact_stem: str | None = None) -> ModerationFoldReport:
    if revision != "rev0046":
        raise ValueError("moderationfold currently audits rev0046")
    root_path = Path(root)
    artifact_stem = artifact_stem or root_path.name
    findings: list[ModerationFoldFinding] = []
    for rel in REV0046_PATHS:
        if not (root_path / rel).exists():
            findings.append(ModerationFoldFinding("error", "missing_rev0046_path", rel, "rev0046 moderation/redress path is absent"))
    for surface_path in ("PUBLIC_SURFACE.json", "HEAD_REGISTRY.json", "docs/00-index.md"):
        for needle in NEEDLES:
            if not _contains(root_path / surface_path, needle):
                findings.append(ModerationFoldFinding("error", "surface_missing_needle", surface_path, f"missing {needle}"))
    try:
        predecessor = audit_bridge_epoch_fold(root_path, revision="rev0045", artifact_stem=artifact_stem)
        predecessor_status = predecessor.status
        if predecessor.error_count:
            findings.append(ModerationFoldFinding("error", "bridgeepochfold_failed", "src/i2p_dht_lab/bridgeepochfold.py", "rev0045 predecessor fold failed"))
    except Exception as exc:  # pragma: no cover
        predecessor_status = "exception"
        findings.append(ModerationFoldFinding("error", "bridgeepochfold_exception", "src/i2p_dht_lab/bridgeepochfold.py", str(exc)))
    try:
        foldmap = audit_fold_map(root_path, revision="rev0046", artifact_stem=artifact_stem)
        foldmap_status = foldmap.status
        if foldmap.error_count:
            findings.append(ModerationFoldFinding("error", "foldmap_failed", "src/i2p_dht_lab/foldmap.py", "rev0046 foldmap failed"))
    except Exception as exc:  # pragma: no cover
        foldmap_status = "exception"
        findings.append(ModerationFoldFinding("error", "foldmap_exception", "src/i2p_dht_lab/foldmap.py", str(exc)))
    try:
        registry = audit_fold_registry(root_path, revision="rev0046")
        registry_status = registry.status
        if registry.error_count:
            findings.append(ModerationFoldFinding("error", "foldregistry_failed", "src/i2p_dht_lab/foldregistry.py", "rev0046 registry failed"))
    except Exception as exc:  # pragma: no cover
        registry_status = "exception"
        findings.append(ModerationFoldFinding("error", "foldregistry_exception", "src/i2p_dht_lab/foldregistry.py", str(exc)))
    try:
        ledger = audit_surface_ledger(root_path, entries_for_revision("rev0046"))
        surface_status = "pass" if ledger.ok else "fail"
        if ledger.error_count:
            findings.append(ModerationFoldFinding("error", "surface_ledger_failed", "src/i2p_dht_lab/surfaceledger.py", "rev0046 surface ledger failed"))
    except Exception as exc:  # pragma: no cover
        surface_status = "exception"
        findings.append(ModerationFoldFinding("error", "surface_ledger_exception", "src/i2p_dht_lab/surfaceledger.py", str(exc)))
    status = "pass" if not any(finding.severity == "error" for finding in findings) else "fail"
    digest = sha256(MODERATION_FOLD_DOMAIN + b":report:" + bencode({
        b"revision": revision,
        b"artifact": artifact_stem,
        b"status": status,
        b"predecessor": predecessor_status,
        b"foldmap": foldmap_status,
        b"registry": registry_status,
        b"surface": surface_status,
        b"findings": [finding.bvalue() for finding in findings],
    }))
    return ModerationFoldReport(revision, artifact_stem, status, predecessor_status, foldmap_status, registry_status, surface_status, tuple(findings), digest)
