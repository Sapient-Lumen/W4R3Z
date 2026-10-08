"""rev0055 audit/refactor fold for restart chaos, effect seal, and fuzz shrink."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .foldmap import audit_fold_map
from .foldregistry import audit_fold_registry
from .ids import DOMAIN, sha256
from .replayfold import audit_replay_fold
from .surfaceledger import audit_surface_ledger, entries_for_revision

RESTART_FOLD_DOMAIN = DOMAIN + b":restart-fold-v1:"


@dataclass(frozen=True)
class RestartFoldFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class RestartFoldReport:
    revision: str
    artifact_stem: str
    status: str
    replay_predecessor_status: str
    foldmap_status: str
    foldregistry_status: str
    surface_ledger_status: str
    findings: tuple[RestartFoldFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")


def _exists(root: Path, rel: str, findings: list[RestartFoldFinding]) -> None:
    if not (root / rel).exists():
        findings.append(RestartFoldFinding("error", "missing_path", rel, "rev0055 restart fold expected this path"))


def audit_restart_fold(root: str | Path, *, revision: str = "rev0055", artifact_stem: str = "") -> RestartFoldReport:
    root_path = Path(root)
    artifact = artifact_stem or root_path.name
    findings: list[RestartFoldFinding] = []
    for rel in (
        "src/i2p_dht_lab/restartchaos.py",
        "src/i2p_dht_lab/effectseal.py",
        "src/i2p_dht_lab/fuzzshrink.py",
        "src/i2p_dht_lab/restartfold.py",
        "tests/test_rev0055_restartchaos_effectseal_fuzzshrink.py",
        "docs/580-rev0055-restartchaos-effectseal-fuzzshrink.md",
        "docs/581-restart-chaos-crash-cut-boundary.md",
        "docs/582-effect-seal-joined-boundary.md",
        "docs/583-fuzz-shrink-coverage-compaction.md",
        "docs/584-restartfold-audit-refactor.md",
    ):
        _exists(root_path, rel, findings)
    try:
        predecessor = audit_replay_fold(root_path, revision="rev0054", artifact_stem=artifact)
        predecessor_status = predecessor.status
        if predecessor.error_count:
            findings.append(RestartFoldFinding("error", "replay_predecessor_failed", "src/i2p_dht_lab/replayfold.py", "rev0054 predecessor fold failed"))
    except Exception as exc:  # pragma: no cover
        predecessor_status = "exception"
        findings.append(RestartFoldFinding("error", "replay_predecessor_exception", "src/i2p_dht_lab/replayfold.py", str(exc)))
    try:
        fmap = audit_fold_map(root_path, revision=revision, artifact_stem=artifact)
        foldmap_status = fmap.status
        if fmap.error_count:
            findings.append(RestartFoldFinding("error", "foldmap_failed", "src/i2p_dht_lab/foldmap.py", "rev0055 fold map failed"))
    except Exception as exc:  # pragma: no cover
        foldmap_status = "exception"
        findings.append(RestartFoldFinding("error", "foldmap_exception", "src/i2p_dht_lab/foldmap.py", str(exc)))
    try:
        registry = audit_fold_registry(root_path, revision=revision)
        foldregistry_status = registry.status
        if registry.error_count:
            findings.append(RestartFoldFinding("error", "foldregistry_failed", "src/i2p_dht_lab/foldregistry.py", "rev0055 fold registry failed"))
    except Exception as exc:  # pragma: no cover
        foldregistry_status = "exception"
        findings.append(RestartFoldFinding("error", "foldregistry_exception", "src/i2p_dht_lab/foldregistry.py", str(exc)))
    try:
        ledger = audit_surface_ledger(root_path, entries_for_revision(revision))
        surface_ledger_status = "pass" if ledger.ok else "fail"
        if ledger.error_count:
            findings.append(RestartFoldFinding("error", "surface_ledger_failed", "src/i2p_dht_lab/surfaceledger.py", "rev0055 surface ledger failed"))
    except Exception as exc:  # pragma: no cover
        surface_ledger_status = "exception"
        findings.append(RestartFoldFinding("error", "surface_ledger_exception", "src/i2p_dht_lab/surfaceledger.py", str(exc)))
    status = "pass" if not any(finding.severity == "error" for finding in findings) else "fail"
    digest = sha256(RESTART_FOLD_DOMAIN + b":report:" + bencode({
        b"revision": revision,
        b"artifact": artifact,
        b"status": status,
        b"replay": predecessor_status,
        b"foldmap": foldmap_status,
        b"foldregistry": foldregistry_status,
        b"surface": surface_ledger_status,
        b"findings": [finding.bvalue() for finding in findings],
    }))
    return RestartFoldReport(revision, artifact, status, predecessor_status, foldmap_status, foldregistry_status, surface_ledger_status, tuple(findings), digest)
