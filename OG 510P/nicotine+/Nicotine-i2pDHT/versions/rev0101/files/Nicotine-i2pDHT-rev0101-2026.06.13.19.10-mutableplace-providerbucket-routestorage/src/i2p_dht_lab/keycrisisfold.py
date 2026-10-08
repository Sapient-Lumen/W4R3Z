"""rev0030 audit/refactor fold for negative-space, peer deltas, and key crisis.

The cube now has enough local boundaries that navigation itself becomes a risk:
new surfaces can exist but not be reachable from docs, public pointers, tests,
or the active surface ledger.  This fold keeps rev0030 visible while preserving
rev0029's foldseal predecessor.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .foldseal import audit_fold_seal
from .ids import DOMAIN, sha256
from .surfaceledger import audit_surface_ledger, entries_for_revision

KEYCRISIS_FOLD_DOMAIN = DOMAIN + b":keycrisis-fold-v1:"


@dataclass(frozen=True)
class KeyCrisisFoldFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class KeyCrisisFoldReport:
    revision: str
    artifact_stem: str
    status: str
    predecessor_status: str
    findings: tuple[KeyCrisisFoldFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")


REV0030_MODULES = (
    "src/i2p_dht_lab/negspace.py",
    "src/i2p_dht_lab/peerbook.py",
    "src/i2p_dht_lab/peerdelta.py",
    "src/i2p_dht_lab/keycrisis.py",
    "src/i2p_dht_lab/absencegate.py",
    "src/i2p_dht_lab/liveprobe.py",
    "src/i2p_dht_lab/livesmoke.py",
    "src/i2p_dht_lab/bootstrapjoin.py",
    "src/i2p_dht_lab/deltasketch.py",
    "src/i2p_dht_lab/deltarepairjoin.py",
    "src/i2p_dht_lab/keycrisisjoin.py",
    "src/i2p_dht_lab/keycrisisfold.py",
)
REV0030_TESTS = (
    "tests/test_rev0030_negspace_peerdelta_keycrisis.py",
    "tests/test_rev0030_joined_branch_surfaces.py",
)
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
    "docs/300-bootstrap-join-live-smoke-pressure.md",
    "docs/301-keycrisis-checkpoint-join.md",
    "docs/302-delta-repair-tombstone-first-join.md",
    "docs/303-branchlet-fold-audit-rev0030.md",
)
HEAD_NEEDLES = ("negative_space", "peer_delta", "key_crisis", "keycrisis_fold", "bootstrap_join", "delta_repair_join", "keycrisis_join", "live_smoke")
PUBLIC_NEEDLES = ("rev0030", "docs/289-rev0030-negspace-peerdelta-keycrisisfold.md", "negspace", "peerdelta", "bootstrapjoin", "deltarepairjoin", "keycrisisjoin")
INDEX_NEEDLES = ("rev0030 negspace / peerdelta / keycrisisfold", "bootstrap join / live smoke / key crisis join")


def _contains(path: Path, needle: str) -> bool:
    try:
        return needle in path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return False


def audit_keycrisis_fold(root: str | Path, *, revision: str = "rev0030", artifact_stem: str | None = None) -> KeyCrisisFoldReport:
    if revision != "rev0030":
        raise ValueError("keycrisisfold currently pins the rev0030 active fold")
    root_path = Path(root)
    artifact_stem = artifact_stem or root_path.name
    findings: list[KeyCrisisFoldFinding] = []
    for rel in REV0030_MODULES + REV0030_TESTS + REV0030_DOCS:
        if not (root_path / rel).exists():
            findings.append(KeyCrisisFoldFinding("error", "missing_keycrisisfold_path", rel, "rev0030 fold path is absent"))
    for needle in HEAD_NEEDLES:
        if not _contains(root_path / "HEAD_REGISTRY.json", needle):
            findings.append(KeyCrisisFoldFinding("error", "head_registry_missing_needle", "HEAD_REGISTRY.json", f"missing {needle}"))
    for needle in PUBLIC_NEEDLES:
        if not _contains(root_path / "PUBLIC_SURFACE.json", needle):
            findings.append(KeyCrisisFoldFinding("error", "public_surface_missing_needle", "PUBLIC_SURFACE.json", f"missing {needle}"))
    for needle in INDEX_NEEDLES:
        if not _contains(root_path / "docs/00-index.md", needle):
            findings.append(KeyCrisisFoldFinding("error", "index_missing_needle", "docs/00-index.md", f"missing {needle}"))
    if not _contains(root_path / "README.md", revision):
        findings.append(KeyCrisisFoldFinding("error", "readme_revision_drift", "README.md", "README does not name rev0030"))
    if not _contains(root_path / "START_HERE.md", revision):
        findings.append(KeyCrisisFoldFinding("error", "start_here_revision_drift", "START_HERE.md", "START_HERE does not name rev0030"))
    try:
        predecessor = audit_fold_seal(root_path, revision="rev0029", artifact_stem=artifact_stem)
        predecessor_status = f"rev0029_foldseal:{predecessor.status}"
        if predecessor.status != "pass":
            findings.append(KeyCrisisFoldFinding("error", "predecessor_fold_failed", "src/i2p_dht_lab/foldseal.py", predecessor_status))
    except Exception as exc:  # pragma: no cover - defensive audit surface
        predecessor_status = "rev0029_foldseal:exception"
        findings.append(KeyCrisisFoldFinding("error", "predecessor_fold_exception", "src/i2p_dht_lab/foldseal.py", str(exc)))
    try:
        ledger = audit_surface_ledger(root_path, entries_for_revision(revision))
        if ledger.error_count:
            findings.append(KeyCrisisFoldFinding("error", "surface_ledger_errors", "src/i2p_dht_lab/surfaceledger.py", "surface ledger does not pass for rev0030"))
    except Exception as exc:  # pragma: no cover
        findings.append(KeyCrisisFoldFinding("error", "surface_ledger_exception", "src/i2p_dht_lab/surfaceledger.py", str(exc)))
    status = "pass" if not any(finding.severity == "error" for finding in findings) else "fail"
    digest = sha256(KEYCRISIS_FOLD_DOMAIN + b":report:" + bencode({
        b"revision": revision,
        b"artifact": artifact_stem,
        b"status": status,
        b"predecessor": predecessor_status,
        b"findings": [finding.bvalue() for finding in findings],
    }))
    return KeyCrisisFoldReport(revision, artifact_stem, status, predecessor_status, tuple(findings), digest)
