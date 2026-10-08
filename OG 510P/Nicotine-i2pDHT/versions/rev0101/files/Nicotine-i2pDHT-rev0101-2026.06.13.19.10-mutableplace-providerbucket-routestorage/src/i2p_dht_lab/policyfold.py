"""Audit rev0024 policy/range-Merkle/queue surfaces.

This keeps the active path visible while the cube retains historical branchlets.
The audit is deliberately tiny: the current modules, tests, docs, and surface
ledger entries must be findable from the root.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .ids import DOMAIN, sha256
from .surfaceledger import active_entries

POLICY_FOLD_DOMAIN = DOMAIN + b":policy-fold-v1:"


@dataclass(frozen=True)
class PolicyFoldFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class PolicyFoldReport:
    revision: str
    status: str
    findings: tuple[PolicyFoldFinding, ...]
    digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")


def audit_policy_fold(root: str | Path, *, revision: str = "rev0024") -> PolicyFoldReport:
    root_path = Path(root)
    findings: list[PolicyFoldFinding] = []
    expected = {
        "src/i2p_dht_lab/policyepoch.py",
        "src/i2p_dht_lab/rangemerkle.py",
        "src/i2p_dht_lab/queueforge.py",
        "src/i2p_dht_lab/policyfold.py",
        "tests/test_rev0024_policyepoch_rangemerkle_queueforge.py",
        "docs/213-rev0024-policyepoch-rangemerkle-queueforge.md",
        "docs/214-policy-epoch-heads.md",
        "docs/215-range-merkle-repair-fixtures.md",
        "docs/216-queue-forge-admission-scheduling.md",
        "docs/217-policy-fold-audit-refactor.md",
        "docs/218-python-surface-rev0024.md",
    }
    ledger_paths = {entry.module for entry in active_entries()} | {entry.test for entry in active_entries()} | {entry.doc for entry in active_entries()}
    for path in sorted(expected):
        if not (root_path / path).exists():
            findings.append(PolicyFoldFinding("error", "missing_expected_surface", path, "rev0024 policy/range/queue surface is missing"))
        if (path.startswith("src/") or path.startswith("tests/") or path.startswith("docs/21")) and path not in ledger_paths and path.endswith((".py", ".md")):
            if path not in {"docs/213-rev0024-policyepoch-rangemerkle-queueforge.md", "docs/218-python-surface-rev0024.md", "docs/219-wake-from-amnesia-rev0024.md", "docs/220-research-notes-2026-06-01-rev0024.md"}:
                findings.append(PolicyFoldFinding("warning", "not_in_surface_ledger", path, "rev0024 implementation/design surface is not listed in active surface ledger"))
    index = (root_path / "docs/00-index.md").read_text(encoding="utf-8") if (root_path / "docs/00-index.md").exists() else ""
    if revision not in index or "rangemerkle" not in index or "queueforge" not in index:
        findings.append(PolicyFoldFinding("error", "index_missing_current_revision", "docs/00-index.md", "docs index does not expose current rev0024 policyfold surface"))
    status = "pass" if not any(finding.severity == "error" for finding in findings) else "fail"
    digest = sha256(POLICY_FOLD_DOMAIN + b":report:" + bencode({
        b"revision": revision,
        b"status": status,
        b"findings": [finding.bvalue() for finding in findings],
    }))
    return PolicyFoldReport(revision, status, tuple(findings), digest)
