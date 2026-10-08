"""rev0030 branch-recovery audit fold.

rev0030 intentionally folds two useful rev0029 branchlets into the active cube:
negative-space/key-crisis pressure and peerbook/delta/live-probe pressure.  This
fold keeps those surfaces visible while proving the rev0029 foldseal predecessor
still passes.  It is a small local audit, not a packaging manifest.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .foldseal import audit_fold_seal
from .ids import DOMAIN, sha256
from .surfaceledger import audit_surface_ledger, entries_for_revision

BRANCH_RECOVER_FOLD_DOMAIN = DOMAIN + b":branch-recover-fold-v1:"


@dataclass(frozen=True)
class BranchRecoverFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class BranchRecoverReport:
    revision: str
    artifact_stem: str
    status: str
    predecessor_status: str
    findings: tuple[BranchRecoverFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for item in self.findings if item.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for item in self.findings if item.severity == "warning")


REV0030_MODULES = (
    "src/i2p_dht_lab/absencegate.py",
    "src/i2p_dht_lab/keycrisis.py",
    "src/i2p_dht_lab/peerbook.py",
    "src/i2p_dht_lab/deltasketch.py",
    "src/i2p_dht_lab/liveprobe.py",
    "src/i2p_dht_lab/rangesetdelta.py",
    "src/i2p_dht_lab/branchrecoverfold.py",
)
REV0030_TESTS = ("tests/test_rev0030_negspace_peerdelta_keycrisis.py",)
REV0030_DOCS = (
    "docs/289-rev0030-negspace-peerdelta-keycrisisfold.md",
    "docs/290-negative-space-absence-pressure.md",
    "docs/291-peerbook-delta-reconciliation.md",
    "docs/292-key-crisis-gating.md",
    "docs/293-keycrisisfold-audit-refactor.md",
    "docs/294-python-surface-rev0030.md",
    "docs/295-wake-from-amnesia-rev0030.md",
    "docs/296-risk-register-rev0030.md",
    "docs/297-proof-obligation-rev0030.md",
    "docs/298-research-notes-2026-06-03-rev0030.md",
)
HEAD_NEEDLES = (
    "absence_gate",
    "key_crisis",
    "peerbook",
    "delta_sketch",
    "live_probe",
    "range_set_delta",
    "branchrecoverfold",
)
PUBLIC_NEEDLES = (
    "rev0030",
    "docs/289-rev0030-negspace-peerdelta-keycrisisfold.md",
    "absencegate",
    "peerbook",
    "keycrisis",
)
INDEX_NEEDLES = ("rev0030 negspace / peerdelta / keycrisisfold",)
SUPERSESSION_NEEDLES = (
    "rev0029_negspace_keycrisis_branchlet",
    "rev0029_peerbook_deltasketch_liveprobe_branchlet",
)


def _contains(path: Path, needle: str) -> bool:
    try:
        return needle in path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return False


def audit_branch_recover_fold(root: str | Path, *, revision: str = "rev0030", artifact_stem: str | None = None) -> BranchRecoverReport:
    if revision != "rev0030":
        raise ValueError("branchrecoverfold currently pins the rev0030 active fold")
    root_path = Path(root)
    artifact_stem = artifact_stem or root_path.name
    findings: list[BranchRecoverFinding] = []
    for rel in REV0030_MODULES + REV0030_TESTS + REV0030_DOCS:
        if not (root_path / rel).exists():
            findings.append(BranchRecoverFinding("error", "missing_branchrecover_path", rel, "rev0030 branch-recovery path is absent"))
    for needle in HEAD_NEEDLES:
        if not _contains(root_path / "HEAD_REGISTRY.json", needle):
            findings.append(BranchRecoverFinding("error", "head_registry_missing_needle", "HEAD_REGISTRY.json", f"missing {needle}"))
    for needle in PUBLIC_NEEDLES:
        if not _contains(root_path / "PUBLIC_SURFACE.json", needle):
            findings.append(BranchRecoverFinding("error", "public_surface_missing_needle", "PUBLIC_SURFACE.json", f"missing {needle}"))
    for needle in INDEX_NEEDLES:
        if not _contains(root_path / "docs/00-index.md", needle):
            findings.append(BranchRecoverFinding("error", "index_missing_needle", "docs/00-index.md", f"missing {needle}"))
    for needle in SUPERSESSION_NEEDLES:
        if not _contains(root_path / "HISTORICAL_SUPERSESSION.json", needle):
            findings.append(BranchRecoverFinding("warning", "supersession_missing_branchlet", "HISTORICAL_SUPERSESSION.json", f"missing {needle}"))
    if not _contains(root_path / "README.md", revision):
        findings.append(BranchRecoverFinding("error", "readme_revision_drift", "README.md", "README does not name rev0030"))
    if not _contains(root_path / "START_HERE.md", revision):
        findings.append(BranchRecoverFinding("error", "start_here_revision_drift", "START_HERE.md", "START_HERE does not name rev0030"))
    try:
        predecessor = audit_fold_seal(root_path, revision="rev0029", artifact_stem=artifact_stem)
        predecessor_status = f"rev0029_foldseal:{predecessor.status}"
        if predecessor.status != "pass":
            findings.append(BranchRecoverFinding("error", "predecessor_fold_failed", "src/i2p_dht_lab/foldseal.py", predecessor_status))
    except Exception as exc:  # pragma: no cover - defensive audit surface
        predecessor_status = "rev0029_foldseal:exception"
        findings.append(BranchRecoverFinding("error", "predecessor_fold_exception", "src/i2p_dht_lab/foldseal.py", str(exc)))
    try:
        ledger = audit_surface_ledger(root_path, entries_for_revision(revision))
        if ledger.error_count:
            findings.append(BranchRecoverFinding("error", "surface_ledger_errors", "src/i2p_dht_lab/surfaceledger.py", "surface ledger does not pass for rev0030"))
    except Exception as exc:  # pragma: no cover
        findings.append(BranchRecoverFinding("error", "surface_ledger_exception", "src/i2p_dht_lab/surfaceledger.py", str(exc)))
    status = "pass" if not any(item.severity == "error" for item in findings) else "fail"
    digest = sha256(BRANCH_RECOVER_FOLD_DOMAIN + b":report:" + bencode({
        b"revision": revision,
        b"artifact": artifact_stem,
        b"status": status,
        b"predecessor": predecessor_status,
        b"findings": [item.bvalue() for item in findings],
    }))
    return BranchRecoverReport(revision, artifact_stem, status, predecessor_status, tuple(findings), digest)
