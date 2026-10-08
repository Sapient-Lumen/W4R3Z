"""rev0068 audit/refactor fold for archive journal / prune replay / closure audit."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .foldmap import audit_fold_map
from .foldregistry import audit_fold_registry
from .ids import DOMAIN, sha256
from .repairsettlementfold import audit_repair_settlement_fold
from .surfaceledger import audit_surface_ledger, entries_for_revision

ARCHIVE_JOURNAL_FOLD_DOMAIN = DOMAIN + b":archive-journal-fold-v1:"


@dataclass(frozen=True)
class ArchiveJournalFoldFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class ArchiveJournalFoldReport:
    revision: str
    artifact_stem: str
    status: str
    predecessor_status: str
    foldmap_status: str
    foldregistry_status: str
    surface_ledger_status: str
    findings: tuple[ArchiveJournalFoldFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")


def _exists(root: Path, rel: str, needle: str, findings: list[ArchiveJournalFoldFinding]) -> None:
    path = root / rel
    if not path.exists():
        findings.append(ArchiveJournalFoldFinding("error", "missing_path", rel, "rev0068 archivejournalfold expected this path"))
        return
    text = path.read_text(encoding="utf-8", errors="replace")
    if needle not in text:
        findings.append(ArchiveJournalFoldFinding("error", "missing_needle", rel, f"missing needle {needle!r}"))


def audit_archive_journal_fold(root: str | Path, *, revision: str = "rev0068", artifact_stem: str = "") -> ArchiveJournalFoldReport:
    root_path = Path(root)
    artifact = artifact_stem or root_path.name
    findings: list[ArchiveJournalFoldFinding] = []
    checks = {
        "src/i2p_dht_lab/archivejournal.py": "ArchiveJournalDecisionKind",
        "src/i2p_dht_lab/prunereplay.py": "PruneReplayDecisionKind",
        "src/i2p_dht_lab/closureaudit.py": "ClosureAuditDecisionKind",
        "src/i2p_dht_lab/archivejournalfold.py": "audit_archive_journal_fold",
        "tests/test_rev0068_archivejournal_prunereplay_closureaudit.py": "test_archive_journal_prune_replay_and_closure_audit_happy_path",
        "docs/718-rev0068-archivejournal-prunereplay-closureaudit.md": "rev0068",
        "docs/719-archive-journal-after-prune.md": "archive journal",
        "docs/720-prune-replay-resistance.md": "prune replay",
        "docs/721-closure-audit-restart-boundary.md": "closure audit",
        "docs/722-archivejournalfold-audit-refactor.md": "archivejournalfold",
    }
    for rel, needle in checks.items():
        _exists(root_path, rel, needle, findings)
    try:
        predecessor = audit_repair_settlement_fold(root_path, revision="rev0067", artifact_stem="x")
        predecessor_status = predecessor.status
        if predecessor.error_count:
            findings.append(ArchiveJournalFoldFinding("error", "predecessor_failed", "src/i2p_dht_lab/repairsettlementfold.py", "rev0067 predecessor failed"))
    except Exception as exc:  # pragma: no cover
        predecessor_status = "exception"
        findings.append(ArchiveJournalFoldFinding("error", "predecessor_exception", "src/i2p_dht_lab/repairsettlementfold.py", str(exc)))
    try:
        fmap = audit_fold_map(root_path, revision=revision, artifact_stem=artifact)
        foldmap_status = fmap.status
        if fmap.error_count:
            findings.append(ArchiveJournalFoldFinding("error", "foldmap_failed", "src/i2p_dht_lab/foldmap.py", "rev0068 fold map failed"))
    except Exception as exc:  # pragma: no cover
        foldmap_status = "exception"
        findings.append(ArchiveJournalFoldFinding("error", "foldmap_exception", "src/i2p_dht_lab/foldmap.py", str(exc)))
    try:
        registry = audit_fold_registry(root_path, revision=revision)
        foldregistry_status = registry.status
        if registry.error_count:
            findings.append(ArchiveJournalFoldFinding("error", "foldregistry_failed", "src/i2p_dht_lab/foldregistry.py", "rev0068 fold registry failed"))
    except Exception as exc:  # pragma: no cover
        foldregistry_status = "exception"
        findings.append(ArchiveJournalFoldFinding("error", "foldregistry_exception", "src/i2p_dht_lab/foldregistry.py", str(exc)))
    try:
        ledger = audit_surface_ledger(root_path, entries_for_revision(revision))
        surface_ledger_status = "pass" if ledger.ok else "fail"
        if ledger.error_count:
            findings.append(ArchiveJournalFoldFinding("error", "surface_ledger_failed", "src/i2p_dht_lab/surfaceledger.py", "rev0068 surface ledger failed"))
    except Exception as exc:  # pragma: no cover
        surface_ledger_status = "exception"
        findings.append(ArchiveJournalFoldFinding("error", "surface_ledger_exception", "src/i2p_dht_lab/surfaceledger.py", str(exc)))
    status = "pass" if not any(f.severity == "error" for f in findings) else "fail"
    digest = sha256(ARCHIVE_JOURNAL_FOLD_DOMAIN + b":report:" + bencode({
        b"revision": revision,
        b"artifact": artifact,
        b"status": status,
        b"predecessor": predecessor_status,
        b"foldmap": foldmap_status,
        b"foldregistry": foldregistry_status,
        b"surface": surface_ledger_status,
        b"findings": [finding.bvalue() for finding in findings],
    }))
    return ArchiveJournalFoldReport(revision, artifact, status, predecessor_status, foldmap_status, foldregistry_status, surface_ledger_status, tuple(findings), digest)
