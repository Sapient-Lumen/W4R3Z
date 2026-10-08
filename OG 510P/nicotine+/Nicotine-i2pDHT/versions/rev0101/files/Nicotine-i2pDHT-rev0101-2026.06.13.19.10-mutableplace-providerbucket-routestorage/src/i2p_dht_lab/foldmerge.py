"""rev0034 fold-merge audit for launch quorum, metrics veil, and branchlets."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .foldmap import audit_fold_map
from .ids import DOMAIN, sha256
from .surfaceledger import audit_surface_ledger, entries_for_revision

FOLD_MERGE_DOMAIN = DOMAIN + b":fold-merge-v1:"


@dataclass(frozen=True)
class FoldMergeFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class FoldMergeReport:
    revision: str
    artifact_stem: str
    status: str
    predecessor_status: str
    branchlet_status: str
    surface_ledger_status: str
    findings: tuple[FoldMergeFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")


REV0034_PATHS = (
    "src/i2p_dht_lab/launchquorum.py",
    "src/i2p_dht_lab/metricsveil.py",
    "src/i2p_dht_lab/foldmerge.py",
    "tests/test_rev0034_launch_metrics_foldmerge.py",
    "docs/339-rev0034-launchquorum-metricsveil-foldmerge.md",
    "docs/340-launch-quorum-cold-start-boundary.md",
    "docs/341-metrics-veil-observability-pressure.md",
    "docs/342-foldmerge-audit-refactor.md",
)
BRANCHLET_PATHS = (
    "src/i2p_dht_lab/persistjoin.py",
    "src/i2p_dht_lab/samprobe.py",
    "src/i2p_dht_lab/foldreduce.py",
    "tests/test_rev0033_persistjoin_samprobe_foldreduce.py",
    "artifacts/branchlets/rev0033_persistjoin_samprobe/329-rev0033-persistjoin-foldreduce-samprobe.md",
)
NEEDLES = ("rev0034", "launchquorum", "metricsveil", "foldmerge", "persistjoin", "samprobe")


def _contains(path: Path, needle: str) -> bool:
    try:
        return needle in path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return False


def audit_fold_merge(root: str | Path, *, revision: str = "rev0034", artifact_stem: str | None = None) -> FoldMergeReport:
    if revision != "rev0034":
        raise ValueError("foldmerge currently audits the rev0034 active path")
    root_path = Path(root)
    artifact_stem = artifact_stem or root_path.name
    findings: list[FoldMergeFinding] = []
    for rel in REV0034_PATHS:
        if not (root_path / rel).exists():
            findings.append(FoldMergeFinding("error", "missing_rev0034_path", rel, "rev0034 active path is absent"))
    branchlet_errors = 0
    for rel in BRANCHLET_PATHS:
        if not (root_path / rel).exists():
            branchlet_errors += 1
            findings.append(FoldMergeFinding("error", "missing_folded_branchlet", rel, "folded rev0033 branchlet path is absent"))
    for surface_path in ("PUBLIC_SURFACE.json", "HEAD_REGISTRY.json", "docs/00-index.md"):
        for needle in NEEDLES:
            if not _contains(root_path / surface_path, needle):
                findings.append(FoldMergeFinding("error", "surface_missing_needle", surface_path, f"missing {needle}"))
    try:
        predecessor = audit_fold_map(root_path, revision="rev0033", artifact_stem=artifact_stem)
        predecessor_status = predecessor.status
        if predecessor.error_count:
            findings.append(FoldMergeFinding("error", "predecessor_foldmap_failed", "src/i2p_dht_lab/foldmap.py", "rev0033 foldmap predecessor failed"))
    except Exception as exc:  # pragma: no cover
        predecessor_status = "exception"
        findings.append(FoldMergeFinding("error", "predecessor_foldmap_exception", "src/i2p_dht_lab/foldmap.py", str(exc)))
    try:
        ledger = audit_surface_ledger(root_path, entries_for_revision(revision))
        surface_status = "pass" if ledger.ok else "fail"
        if ledger.error_count:
            findings.append(FoldMergeFinding("error", "surface_ledger_failed", "src/i2p_dht_lab/surfaceledger.py", "rev0034 surface ledger failed"))
    except Exception as exc:  # pragma: no cover
        surface_status = "exception"
        findings.append(FoldMergeFinding("error", "surface_ledger_exception", "src/i2p_dht_lab/surfaceledger.py", str(exc)))
    branchlet_status = "pass" if branchlet_errors == 0 else "fail"
    status = "pass" if not any(item.severity == "error" for item in findings) else "fail"
    digest = sha256(FOLD_MERGE_DOMAIN + b":report:" + bencode({
        b"revision": revision,
        b"artifact": artifact_stem,
        b"status": status,
        b"predecessor_status": predecessor_status,
        b"branchlet_status": branchlet_status,
        b"surface_status": surface_status,
        b"findings": [finding.bvalue() for finding in findings],
    }))
    return FoldMergeReport(revision, artifact_stem, status, predecessor_status, branchlet_status, surface_status, tuple(findings), digest)
