"""rev0051 send-valve/effect-ledger/fold-merge audit."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .drainfold import audit_drain_fold
from .foldmap import audit_fold_map
from .foldregistry import audit_fold_registry
from .ids import DOMAIN, sha256
from .surfaceledger import audit_surface_ledger, entries_for_revision

SEND_FOLD_DOMAIN = DOMAIN + b":send-fold-v1:"

REV0051_PATHS = (
    "src/i2p_dht_lab/commitbarrier.py",
    "src/i2p_dht_lab/sendvalve.py",
    "src/i2p_dht_lab/effectledger.py",
    "src/i2p_dht_lab/sendfold.py",
    "tests/test_rev0051_sendvalve_effectledger_foldmerge.py",
    "docs/534-rev0051-sendvalve-effectledger-foldmerge.md",
    "docs/535-send-valve-joined-boundary.md",
    "docs/536-effect-ledger-idempotent-memory.md",
    "docs/537-foldmerge-commitbarrier-branchlet.md",
    "docs/538-sendfold-audit-refactor.md",
)
NEEDLES = ("rev0051", "commitbarrier", "sendvalve", "effectledger", "sendfold")
BRANCHLET_PATHS = (
    "artifacts/branchlets/rev0050_commitbarrier_publicedgefold/publicedgefold.py",
    "artifacts/branchlets/rev0050_commitbarrier_publicedgefold/test_rev0050_commitbarrier_outboxdrain_fold.py",
)


@dataclass(frozen=True)
class SendFoldFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class SendFoldReport:
    revision: str
    artifact_stem: str
    status: str
    drain_predecessor_status: str
    foldmap_status: str
    foldregistry_status: str
    surface_ledger_status: str
    findings: tuple[SendFoldFinding, ...]
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


def audit_send_fold(root: str | Path, *, revision: str = "rev0051", artifact_stem: str | None = None) -> SendFoldReport:
    if revision != "rev0051":
        raise ValueError("sendfold currently audits rev0051")
    root_path = Path(root)
    artifact_stem = artifact_stem or root_path.name
    findings: list[SendFoldFinding] = []
    for rel in REV0051_PATHS:
        if not (root_path / rel).exists():
            findings.append(SendFoldFinding("error", "missing_rev0051_path", rel, "rev0051 send path is absent"))
    for rel in BRANCHLET_PATHS:
        if not (root_path / rel).exists():
            findings.append(SendFoldFinding("error", "missing_folded_branchlet", rel, "folded rev0050 commitbarrier/publicedge branchlet is not visible"))
    for surface_path in ("PUBLIC_SURFACE.json", "HEAD_REGISTRY.json", "docs/00-index.md"):
        for needle in NEEDLES:
            if not _contains(root_path / surface_path, needle):
                findings.append(SendFoldFinding("error", "surface_missing_needle", surface_path, f"missing {needle}"))
    try:
        drain = audit_drain_fold(root_path, revision="rev0050", artifact_stem=artifact_stem)
        drain_status = drain.status
        if drain.error_count:
            findings.append(SendFoldFinding("error", "drainfold_failed", "src/i2p_dht_lab/drainfold.py", "rev0050 drain predecessor failed"))
    except Exception as exc:  # pragma: no cover
        drain_status = "exception"
        findings.append(SendFoldFinding("error", "drainfold_exception", "src/i2p_dht_lab/drainfold.py", str(exc)))
    try:
        foldmap = audit_fold_map(root_path, revision="rev0051", artifact_stem=artifact_stem)
        foldmap_status = foldmap.status
        if foldmap.error_count:
            findings.append(SendFoldFinding("error", "foldmap_failed", "src/i2p_dht_lab/foldmap.py", "rev0051 foldmap failed"))
    except Exception as exc:  # pragma: no cover
        foldmap_status = "exception"
        findings.append(SendFoldFinding("error", "foldmap_exception", "src/i2p_dht_lab/foldmap.py", str(exc)))
    try:
        registry = audit_fold_registry(root_path, revision="rev0051")
        registry_status = registry.status
        if registry.error_count:
            findings.append(SendFoldFinding("error", "foldregistry_failed", "src/i2p_dht_lab/foldregistry.py", "rev0051 foldregistry failed"))
    except Exception as exc:  # pragma: no cover
        registry_status = "exception"
        findings.append(SendFoldFinding("error", "foldregistry_exception", "src/i2p_dht_lab/foldregistry.py", str(exc)))
    try:
        ledger = audit_surface_ledger(root_path, entries_for_revision("rev0051"))
        surface_status = "pass" if ledger.ok else "fail"
        if ledger.error_count:
            findings.append(SendFoldFinding("error", "surfaceledger_failed", "src/i2p_dht_lab/surfaceledger.py", "rev0051 surface ledger failed"))
    except Exception as exc:  # pragma: no cover
        surface_status = "exception"
        findings.append(SendFoldFinding("error", "surfaceledger_exception", "src/i2p_dht_lab/surfaceledger.py", str(exc)))
    status = "pass" if not any(finding.severity == "error" for finding in findings) else "fail"
    digest = sha256(SEND_FOLD_DOMAIN + b":report:" + bencode({
        b"revision": revision,
        b"artifact": artifact_stem,
        b"status": status,
        b"drain": drain_status,
        b"foldmap": foldmap_status,
        b"registry": registry_status,
        b"surface": surface_status,
        b"findings": [finding.bvalue() for finding in findings],
    }))
    return SendFoldReport(revision, artifact_stem, status, drain_status, foldmap_status, registry_status, surface_status, tuple(findings), digest)
