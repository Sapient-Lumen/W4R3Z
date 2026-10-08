"""Audit current namespace/validator/admission surfaces.

The cube now has several validation boundaries: parseguard, wirecanon,
validatorwall, namespaceregistry, and admissionwall.  This audit is intentionally
small: it checks that active namespace docs and modules are visible and that the
current revision wired these surfaces into the surface ledger.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .ids import DOMAIN, sha256
from .surfaceledger import active_entries

NAMESPACE_FOLD_DOMAIN = DOMAIN + b":namespace-fold-v1:"


@dataclass(frozen=True)
class NamespaceFoldFinding:
    severity: str
    code: str
    path: str
    detail: str


@dataclass(frozen=True)
class NamespaceFoldReport:
    revision: str
    status: str
    findings: tuple[NamespaceFoldFinding, ...]
    digest: bytes

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")


def audit_namespace_fold(root: str | Path, *, revision: str = "rev0023") -> NamespaceFoldReport:
    root_path = Path(root)
    findings: list[NamespaceFoldFinding] = []
    expected = {
        "src/i2p_dht_lab/namespaceregistry.py",
        "src/i2p_dht_lab/admissionwall.py",
        "src/i2p_dht_lab/rangesketch.py",
        "src/i2p_dht_lab/namespacefold.py",
        "tests/test_rev0023_rangesketch_admission_namespace.py",
        "docs/204-rev0023-rangesketch-admissionwall-namespacefold.md",
        "docs/205-range-sketch-anti-entropy.md",
        "docs/206-admission-wall-before-expensive-work.md",
        "docs/207-namespace-registry-validator-policy.md",
        "docs/208-namespace-fold-audit-refactor.md",
        "docs/209-python-surface-rev0023.md",
    }
    ledger_paths = {entry.module for entry in active_entries()} | {entry.test for entry in active_entries()} | {entry.doc for entry in active_entries()}
    for path in sorted(expected):
        if not (root_path / path).exists():
            findings.append(NamespaceFoldFinding("error", "missing_expected_surface", path, "rev0023 namespace/admission/range surface is missing"))
        ledger_required = path.startswith("src/") or path.startswith("tests/") or path in {
            "docs/205-range-sketch-anti-entropy.md",
            "docs/206-admission-wall-before-expensive-work.md",
            "docs/207-namespace-registry-validator-policy.md",
            "docs/208-namespace-fold-audit-refactor.md",
        }
        if ledger_required and path not in ledger_paths:
            findings.append(NamespaceFoldFinding("warning", "not_in_surface_ledger", path, "rev0023 active implementation surface is not listed in active surface ledger"))
    index = (root_path / "docs/00-index.md").read_text(encoding="utf-8") if (root_path / "docs/00-index.md").exists() else ""
    if revision not in index or "rangesketch" not in index:
        findings.append(NamespaceFoldFinding("error", "index_missing_current_revision", "docs/00-index.md", "docs index does not expose current rev0023 namespacefold surface"))
    status = "pass" if not any(finding.severity == "error" for finding in findings) else "fail"
    digest = sha256(NAMESPACE_FOLD_DOMAIN + b":report:" + bencode({
        b"revision": revision,
        b"status": status,
        b"findings": [{b"severity": f.severity, b"code": f.code, b"path": f.path, b"detail": f.detail} for f in findings],
    }))
    return NamespaceFoldReport(revision, status, tuple(findings), digest)
