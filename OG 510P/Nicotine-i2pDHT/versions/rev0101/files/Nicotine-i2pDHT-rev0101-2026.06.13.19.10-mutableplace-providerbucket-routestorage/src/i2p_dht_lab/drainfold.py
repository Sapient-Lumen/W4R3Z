"""rev0050 outbox-drain / SAM-canary / compact-join fold audit."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .foldmap import audit_fold_map
from .foldregistry import audit_fold_registry
from .ids import DOMAIN, sha256
from .outboxfold import audit_outbox_fold
from .publishdryrunfold import audit_publish_dryrun_fold
from .surfaceledger import audit_surface_ledger, entries_for_revision

DRAIN_FOLD_DOMAIN = DOMAIN + b":drain-fold-v1:"

REV0050_PATHS = (
    "src/i2p_dht_lab/outboxdrain.py",
    "src/i2p_dht_lab/samcanary.py",
    "src/i2p_dht_lab/compactjoin.py",
    "src/i2p_dht_lab/drainfold.py",
    "tests/test_rev0050_outboxdrain_samcanary_compactjoin.py",
    "docs/524-rev0050-outboxdrain-samcanary-compactjoin.md",
    "docs/525-outbox-drain-commit-receipts.md",
    "docs/526-sam-canary-before-live-send.md",
    "docs/527-compact-join-negative-evidence.md",
    "docs/528-drainfold-audit-refactor.md",
)
NEEDLES = ("rev0050", "outboxdrain", "samcanary", "compactjoin", "drainfold")


@dataclass(frozen=True)
class DrainFoldFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class DrainFoldReport:
    revision: str
    artifact_stem: str
    status: str
    publish_predecessor_status: str
    outbox_predecessor_status: str
    foldmap_status: str
    registry_status: str
    surface_ledger_status: str
    findings: tuple[DrainFoldFinding, ...]
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


def audit_drain_fold(root: str | Path, *, revision: str = "rev0050", artifact_stem: str | None = None) -> DrainFoldReport:
    if revision != "rev0050":
        raise ValueError("drainfold currently audits rev0050")
    root_path = Path(root)
    artifact_stem = artifact_stem or root_path.name
    findings: list[DrainFoldFinding] = []
    for rel in REV0050_PATHS:
        if not (root_path / rel).exists():
            findings.append(DrainFoldFinding("error", "missing_rev0050_path", rel, "rev0050 drain/canary/compact path is absent"))
    for surface_path in ("PUBLIC_SURFACE.json", "HEAD_REGISTRY.json", "docs/00-index.md"):
        for needle in NEEDLES:
            if not _contains(root_path / surface_path, needle):
                findings.append(DrainFoldFinding("error", "surface_missing_needle", surface_path, f"missing {needle}"))
    try:
        publish = audit_publish_dryrun_fold(root_path, revision="rev0049", artifact_stem=artifact_stem)
        publish_status = publish.status
        if publish.error_count:
            findings.append(DrainFoldFinding("error", "publishdryrunfold_failed", "src/i2p_dht_lab/publishdryrunfold.py", "rev0049 publish predecessor failed"))
    except Exception as exc:  # pragma: no cover
        publish_status = "exception"
        findings.append(DrainFoldFinding("error", "publishdryrunfold_exception", "src/i2p_dht_lab/publishdryrunfold.py", str(exc)))
    try:
        outbox = audit_outbox_fold(root_path, revision="rev0049", artifact_stem=artifact_stem)
        outbox_status = outbox.status
        if outbox.error_count:
            findings.append(DrainFoldFinding("error", "outboxfold_failed", "src/i2p_dht_lab/outboxfold.py", "rev0049 outbox predecessor failed"))
    except Exception as exc:  # pragma: no cover
        outbox_status = "exception"
        findings.append(DrainFoldFinding("error", "outboxfold_exception", "src/i2p_dht_lab/outboxfold.py", str(exc)))
    try:
        foldmap = audit_fold_map(root_path, revision="rev0050", artifact_stem=artifact_stem)
        foldmap_status = foldmap.status
        if foldmap.error_count:
            findings.append(DrainFoldFinding("error", "foldmap_failed", "src/i2p_dht_lab/foldmap.py", "rev0050 foldmap failed"))
    except Exception as exc:  # pragma: no cover
        foldmap_status = "exception"
        findings.append(DrainFoldFinding("error", "foldmap_exception", "src/i2p_dht_lab/foldmap.py", str(exc)))
    try:
        registry = audit_fold_registry(root_path, revision="rev0050")
        registry_status = registry.status
        if registry.error_count:
            findings.append(DrainFoldFinding("error", "foldregistry_failed", "src/i2p_dht_lab/foldregistry.py", "rev0050 foldregistry failed"))
    except Exception as exc:  # pragma: no cover
        registry_status = "exception"
        findings.append(DrainFoldFinding("error", "foldregistry_exception", "src/i2p_dht_lab/foldregistry.py", str(exc)))
    try:
        ledger = audit_surface_ledger(root_path, entries_for_revision("rev0050"))
        surface_status = "pass" if ledger.ok else "fail"
        if ledger.error_count:
            findings.append(DrainFoldFinding("error", "surface_ledger_failed", "src/i2p_dht_lab/surfaceledger.py", "rev0050 surface ledger failed"))
    except Exception as exc:  # pragma: no cover
        surface_status = "exception"
        findings.append(DrainFoldFinding("error", "surface_ledger_exception", "src/i2p_dht_lab/surfaceledger.py", str(exc)))
    status = "pass" if not any(finding.severity == "error" for finding in findings) else "fail"
    digest = sha256(DRAIN_FOLD_DOMAIN + b":report:" + bencode({
        b"revision": revision,
        b"artifact": artifact_stem,
        b"status": status,
        b"publish": publish_status,
        b"outbox": outbox_status,
        b"foldmap": foldmap_status,
        b"registry": registry_status,
        b"surface": surface_status,
        b"findings": [finding.bvalue() for finding in findings],
    }))
    return DrainFoldReport(revision, artifact_stem, status, publish_status, outbox_status, foldmap_status, registry_status, surface_status, tuple(findings), digest)
