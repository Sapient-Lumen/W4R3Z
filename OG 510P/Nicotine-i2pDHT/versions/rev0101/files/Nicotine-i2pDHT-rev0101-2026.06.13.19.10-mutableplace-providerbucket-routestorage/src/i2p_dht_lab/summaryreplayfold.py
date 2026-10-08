"""rev0078 audit/refactor fold for replay, ACK closure, and export fence."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .foldmap import audit_fold_map
from .foldregistry import audit_fold_registry
from .ids import DOMAIN, sha256
from .summaryackfold import audit_summary_ack_fold
from .surfaceledger import audit_surface_ledger, entries_for_revision

SUMMARY_REPLAY_FOLD_DOMAIN = DOMAIN + b":summary-replay-fold-v1:"


@dataclass(frozen=True)
class SummaryReplayFoldFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class SummaryReplayFoldReport:
    revision: str
    artifact_stem: str
    status: str
    predecessor_status: str
    foldmap_status: str
    foldregistry_status: str
    surface_ledger_status: str
    findings: tuple[SummaryReplayFoldFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")


def _exists(root: Path, rel: str, needle: str, findings: list[SummaryReplayFoldFinding]) -> None:
    path = root / rel
    if not path.exists():
        findings.append(SummaryReplayFoldFinding("error", "missing_path", rel, "rev0078 expected this path"))
        return
    if needle not in path.read_text(encoding="utf-8", errors="replace"):
        findings.append(SummaryReplayFoldFinding("error", "missing_needle", rel, f"missing needle {needle!r}"))


def audit_summary_replay_fold(root: str | Path, *, revision: str = "rev0078", artifact_stem: str = "") -> SummaryReplayFoldReport:
    root_path = Path(root)
    artifact = artifact_stem or root_path.name
    findings: list[SummaryReplayFoldFinding] = []
    checks = {
        "src/i2p_dht_lab/summaryreplay.py": "SummaryReplayDecisionKind",
        "src/i2p_dht_lab/ackclosure.py": "AckClosureDecisionKind",
        "src/i2p_dht_lab/summaryexportfence.py": "SummaryExportDecisionKind",
        "src/i2p_dht_lab/summaryreplayfold.py": "audit_summary_replay_fold",
        "tests/test_rev0078_summaryreplay_ackclosure_exportfence.py": "test_summary_replay_closure_export_happy_path",
        "docs/818-rev0078-summaryreplay-ackclosure-exportfence.md": "rev0078",
        "docs/819-summary-replay-after-prune-fence.md": "summaryreplay",
        "docs/820-ack-closure-after-restart-replay.md": "ackclosure",
        "docs/821-summary-export-fence.md": "summaryexportfence",
        "docs/822-summaryreplayfold-audit-refactor.md": "summaryreplayfold",
    }
    for rel, needle in checks.items():
        _exists(root_path, rel, needle, findings)

    try:
        predecessor = audit_summary_ack_fold(root_path, revision="rev0077", artifact_stem=artifact)
        predecessor_status = predecessor.status
        if predecessor.error_count:
            findings.append(SummaryReplayFoldFinding("error", "predecessor_failed", "src/i2p_dht_lab/summaryackfold.py", "rev0077 predecessor failed"))
    except Exception as exc:  # pragma: no cover
        predecessor_status = "exception"
        findings.append(SummaryReplayFoldFinding("error", "predecessor_exception", "src/i2p_dht_lab/summaryackfold.py", str(exc)))

    try:
        fmap = audit_fold_map(root_path, revision=revision, artifact_stem=artifact)
        foldmap_status = fmap.status
        if fmap.error_count:
            findings.append(SummaryReplayFoldFinding("error", "foldmap_failed", "src/i2p_dht_lab/foldmap.py", "rev0078 fold map failed"))
    except Exception as exc:  # pragma: no cover
        foldmap_status = "exception"
        findings.append(SummaryReplayFoldFinding("error", "foldmap_exception", "src/i2p_dht_lab/foldmap.py", str(exc)))

    try:
        registry = audit_fold_registry(root_path, revision=revision)
        foldregistry_status = registry.status
        if registry.error_count:
            findings.append(SummaryReplayFoldFinding("error", "foldregistry_failed", "src/i2p_dht_lab/foldregistry.py", "rev0078 fold registry failed"))
    except Exception as exc:  # pragma: no cover
        foldregistry_status = "exception"
        findings.append(SummaryReplayFoldFinding("error", "foldregistry_exception", "src/i2p_dht_lab/foldregistry.py", str(exc)))

    try:
        ledger = audit_surface_ledger(root_path, entries_for_revision(revision))
        surface_ledger_status = "pass" if ledger.ok else "fail"
        if ledger.error_count:
            findings.append(SummaryReplayFoldFinding("error", "surface_ledger_failed", "src/i2p_dht_lab/surfaceledger.py", "rev0078 surface ledger failed"))
    except Exception as exc:  # pragma: no cover
        surface_ledger_status = "exception"
        findings.append(SummaryReplayFoldFinding("error", "surface_ledger_exception", "src/i2p_dht_lab/surfaceledger.py", str(exc)))

    status = "pass" if not any(f.severity == "error" for f in findings) else "fail"
    report_digest = sha256(SUMMARY_REPLAY_FOLD_DOMAIN + b":report:" + bencode({
        b"revision": revision,
        b"artifact": artifact,
        b"status": status,
        b"predecessor": predecessor_status,
        b"foldmap": foldmap_status,
        b"registry": foldregistry_status,
        b"surface": surface_ledger_status,
        b"findings": [finding.bvalue() for finding in findings],
    }))
    return SummaryReplayFoldReport(revision, artifact, status, predecessor_status, foldmap_status, foldregistry_status, surface_ledger_status, tuple(findings), report_digest)
