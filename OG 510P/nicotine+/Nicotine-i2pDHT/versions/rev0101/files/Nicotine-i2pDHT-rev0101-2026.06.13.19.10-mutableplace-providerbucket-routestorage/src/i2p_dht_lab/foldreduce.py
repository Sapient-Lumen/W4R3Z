"""rev0033 fold-reduction audit/refactor seam.

The cube now has many fold modules because each revision wanted a wake-from-
amnesia audit.  rev0033 does not delete that history.  It makes a current
reduction map explicit: new surfaces stay visible, predecessor folds remain
regression-visible, and old fold modules are classified as predecessor-only
rather than active navigation sprawl.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .foldmap import audit_fold_map
from .ids import DOMAIN, sha256
from .surfaceledger import audit_surface_ledger, entries_for_revision

FOLD_REDUCE_DOMAIN = DOMAIN + b":fold-reduce-v1:"


@dataclass(frozen=True)
class FoldReduceFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class FoldReduceReport:
    revision: str
    artifact_stem: str
    status: str
    predecessor_status: str
    surface_ledger_status: str
    current_fold_count: int
    predecessor_fold_count: int
    findings: tuple[FoldReduceFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")


REV0033_PATHS = (
    "src/i2p_dht_lab/persistjoin.py",
    "src/i2p_dht_lab/samprobe.py",
    "src/i2p_dht_lab/foldreduce.py",
    "tests/test_rev0033_persistjoin_samprobe_foldreduce.py",
    "artifacts/branchlets/rev0033_persistjoin_samprobe/329-rev0033-persistjoin-foldreduce-samprobe.md",
    "artifacts/branchlets/rev0033_persistjoin_samprobe/330-persist-join-restart-boundary.md",
    "artifacts/branchlets/rev0033_persistjoin_samprobe/331-sam-probe-no-router-harness.md",
    "artifacts/branchlets/rev0033_persistjoin_samprobe/332-foldreduce-audit-refactor.md",
)
NEEDLES = ("rev0034", "persistjoin", "samprobe", "foldreduce")
PREDECESSOR_FOLDS = (
    "src/i2p_dht_lab/scopefold.py",
    "src/i2p_dht_lab/foldmap.py",
    "src/i2p_dht_lab/keycrisisfold.py",
    "src/i2p_dht_lab/foldseal.py",
    "src/i2p_dht_lab/foldspine.py",
)


def _contains(path: Path, needle: str) -> bool:
    try:
        return needle in path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return False


def audit_fold_reduce(root: str | Path, *, revision: str = "rev0033", artifact_stem: str | None = None) -> FoldReduceReport:
    if revision != "rev0033":
        raise ValueError("foldreduce currently audits the rev0033 active path")
    root_path = Path(root)
    artifact_stem = artifact_stem or root_path.name
    findings: list[FoldReduceFinding] = []
    for rel in REV0033_PATHS:
        if not (root_path / rel).exists():
            findings.append(FoldReduceFinding("error", "missing_rev0033_path", rel, "rev0033 active path is absent"))
    for rel in PREDECESSOR_FOLDS:
        if not (root_path / rel).exists():
            findings.append(FoldReduceFinding("warning", "missing_predecessor_fold", rel, "historical fold predecessor is missing"))
    for surface_path in ("PUBLIC_SURFACE.json", "HEAD_REGISTRY.json", "docs/00-index.md"):
        for needle in NEEDLES:
            if not _contains(root_path / surface_path, needle):
                findings.append(FoldReduceFinding("error", "surface_missing_needle", surface_path, f"missing {needle}"))
    try:
        predecessor = audit_fold_map(root_path, revision="rev0032", artifact_stem=artifact_stem)
        predecessor_status = predecessor.status
        if predecessor.error_count:
            findings.append(FoldReduceFinding("error", "predecessor_foldmap_failed", "src/i2p_dht_lab/foldmap.py", "rev0032 foldmap predecessor failed"))
    except Exception as exc:  # pragma: no cover - audit defense
        predecessor_status = "exception"
        findings.append(FoldReduceFinding("error", "predecessor_foldmap_exception", "src/i2p_dht_lab/foldmap.py", str(exc)))
    try:
        ledger = audit_surface_ledger(root_path, entries_for_revision(revision))
        surface_status = "pass" if ledger.ok else "fail"
        if ledger.error_count:
            findings.append(FoldReduceFinding("error", "surface_ledger_failed", "src/i2p_dht_lab/surfaceledger.py", "rev0033 surface ledger failed"))
    except Exception as exc:  # pragma: no cover - audit defense
        surface_status = "exception"
        findings.append(FoldReduceFinding("error", "surface_ledger_exception", "src/i2p_dht_lab/surfaceledger.py", str(exc)))
    status = "pass" if not any(item.severity == "error" for item in findings) else "fail"
    digest = sha256(FOLD_REDUCE_DOMAIN + b":report:" + bencode({
        b"revision": revision,
        b"artifact": artifact_stem,
        b"status": status,
        b"predecessor_status": predecessor_status,
        b"surface_status": surface_status,
        b"current_fold_count": 1,
        b"predecessor_fold_count": len(PREDECESSOR_FOLDS),
        b"findings": [finding.bvalue() for finding in findings],
    }))
    return FoldReduceReport(revision, artifact_stem, status, predecessor_status, surface_status, 1, len(PREDECESSOR_FOLDS), tuple(findings), digest)
