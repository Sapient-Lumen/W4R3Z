"""Audit/refactor fold for rev0027 branch reconciliation.

rev0026 accidentally produced two useful branchlets in this cloudtainer: the
spoken schedjoin/custody/transport-shadow path and an unspoken lineage/workmeter
path.  Deleting either would lose pressure-tested ideas.  This fold makes the
merge auditable: both branchlets must be visible, the current rev0027 surfaces
must be visible, and historical branchlet docs must be mapped instead of
silently overwritten.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .ids import DOMAIN, sha256
from .lineagefold import audit_lineage_fold
from .joinfold import audit_join_fold
from .surfaceledger import audit_surface_ledger, entries_for_revision

BRANCH_MERGE_FOLD_DOMAIN = DOMAIN + b":branch-merge-fold-v1:"


@dataclass(frozen=True)
class BranchMergeFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class BranchMergeFoldReport:
    revision: str
    status: str
    checked_paths: tuple[str, ...]
    findings: tuple[BranchMergeFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for item in self.findings if item.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for item in self.findings if item.severity == "warning")


def _contains(path: Path, needle: str) -> bool:
    try:
        return needle in path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return False


def audit_branch_merge_fold(root: str | Path, *, revision: str = "rev0027") -> BranchMergeFoldReport:
    root_path = Path(root)
    required = (
        "src/i2p_dht_lab/persistlane.py",
        "src/i2p_dht_lab/fuzzwire.py",
        "src/i2p_dht_lab/refusalloop.py",
        "src/i2p_dht_lab/branchmergefold.py",
        "src/i2p_dht_lab/lineagewindow.py",
        "src/i2p_dht_lab/claimbundle.py",
        "src/i2p_dht_lab/workmeter.py",
        "src/i2p_dht_lab/schedjoin.py",
        "src/i2p_dht_lab/transportshadow.py",
        "tests/test_rev0027_persist_fuzz_refusal_branchmerge.py",
        "tests/test_rev0026_lineagebundle_workmeter.py",
        "tests/test_rev0026_schedjoin_custodygc_transportshadow.py",
        "docs/258-rev0027-branchmerge-persistfuzz-refusalloop.md",
        "docs/259-persist-lane-crash-reload-pressure.md",
        "docs/260-fuzzwire-generated-malformed-fixtures.md",
        "docs/261-refusal-loop-across-garden-windows.md",
        "docs/262-branchmergefold-audit-refactor.md",
    )
    findings: list[BranchMergeFinding] = []
    for rel in required:
        if not (root_path / rel).exists():
            findings.append(BranchMergeFinding("error", "missing_required_path", rel, "rev0027 branch-merge path is absent"))
    for rel, needle in (
        ("PUBLIC_SURFACE.json", "docs/258-rev0027-branchmerge-persistfuzz-refusalloop.md"),
        ("PUBLIC_SURFACE.json", "docs/250-merged-branchlet-rev0026-lineagebundle-workmeter.md"),
        ("HEAD_REGISTRY.json", "persist_lane"),
        ("HEAD_REGISTRY.json", "merged_lineage_window"),
        ("docs/00-index.md", "rev0027 branchmerge / persistlane / fuzzwire / refusalloop"),
        ("README.md", "rev0027"),
        ("START_HERE.md", "rev0027"),
    ):
        if not _contains(root_path / rel, needle):
            findings.append(BranchMergeFinding("error", "missing_pointer_text", rel, f"expected pointer text not found: {needle}"))
    join = audit_join_fold(root_path, revision="rev0026")
    lineage = audit_lineage_fold(root_path, revision="rev0026")
    if join.error_count:
        findings.append(BranchMergeFinding("error", "joinfold_regression", "src/i2p_dht_lab/joinfold.py", "spoken rev0026 joinfold no longer passes after merge"))
    if lineage.error_count:
        findings.append(BranchMergeFinding("error", "lineagefold_regression", "src/i2p_dht_lab/lineagefold.py", "merged rev0026 lineagefold no longer passes after merge"))
    try:
        ledger = audit_surface_ledger(root_path, entries_for_revision(revision))
        if ledger.error_count:
            findings.append(BranchMergeFinding("error", "surface_ledger_errors", "src/i2p_dht_lab/surfaceledger.py", "rev0027 surface ledger has errors"))
    except Exception as exc:  # pragma: no cover - defensive audit surface only
        findings.append(BranchMergeFinding("error", "surface_ledger_exception", "src/i2p_dht_lab/surfaceledger.py", str(exc)))
    status = "pass" if not any(item.severity == "error" for item in findings) else "fail"
    digest = sha256(BRANCH_MERGE_FOLD_DOMAIN + b":report:" + bencode({
        b"revision": revision,
        b"status": status,
        b"checked": list(required),
        b"findings": [item.bvalue() for item in findings],
    }))
    return BranchMergeFoldReport(revision, status, required, tuple(findings), digest)
