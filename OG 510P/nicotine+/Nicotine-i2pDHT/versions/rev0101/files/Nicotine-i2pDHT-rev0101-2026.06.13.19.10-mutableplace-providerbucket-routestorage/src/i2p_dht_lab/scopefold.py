"""rev0032 fold audit for scopeledger/storedebt/samtrace.

This is a current-revision audit/refactor seam.  It keeps the rev0032 joined
surfaces visible from public pointers, docs, tests, and the surface ledger while
preserving the rev0031 fold-map as predecessor history.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .foldmap import audit_fold_map
from .ids import DOMAIN, sha256
from .surfaceledger import audit_surface_ledger, entries_for_revision

SCOPE_FOLD_DOMAIN = DOMAIN + b":scope-fold-v1:"


@dataclass(frozen=True)
class ScopeFoldFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class ScopeFoldReport:
    revision: str
    artifact_stem: str
    status: str
    predecessor_status: str
    surface_ledger_status: str
    findings: tuple[ScopeFoldFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")


REV0032_PATHS = (
    "src/i2p_dht_lab/scopeledger.py",
    "src/i2p_dht_lab/storedebt.py",
    "src/i2p_dht_lab/samtrace.py",
    "src/i2p_dht_lab/scopefold.py",
    "tests/test_rev0032_scopeledger_storedebt_samtrace.py",
    "docs/319-rev0032-scopeledger-storedebt-samtrace.md",
    "docs/320-scope-ledger-joined-advance.md",
    "docs/321-store-debt-repair-pressure.md",
    "docs/322-sam-trace-scope-boundary.md",
    "docs/323-scopefold-audit-refactor.md",
)
NEEDLES = ("rev0032", "scopeledger", "storedebt", "samtrace", "scopefold")


def _contains(path: Path, needle: str) -> bool:
    try:
        return needle in path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return False


def audit_scope_fold(root: str | Path, *, revision: str = "rev0032", artifact_stem: str | None = None) -> ScopeFoldReport:
    if revision != "rev0032":
        raise ValueError("scopefold currently audits the rev0032 active path")
    root_path = Path(root)
    artifact_stem = artifact_stem or root_path.name
    findings: list[ScopeFoldFinding] = []
    for rel in REV0032_PATHS:
        if not (root_path / rel).exists():
            findings.append(ScopeFoldFinding("error", "missing_rev0032_path", rel, "rev0032 active path is absent"))
    for surface_path in ("PUBLIC_SURFACE.json", "HEAD_REGISTRY.json", "docs/00-index.md"):
        for needle in NEEDLES:
            if not _contains(root_path / surface_path, needle):
                findings.append(ScopeFoldFinding("error", "surface_missing_needle", surface_path, f"missing {needle}"))
    try:
        predecessor = audit_fold_map(root_path, revision="rev0031", artifact_stem=artifact_stem)
        predecessor_status = predecessor.status
        if predecessor.error_count:
            findings.append(ScopeFoldFinding("error", "predecessor_foldmap_failed", "src/i2p_dht_lab/foldmap.py", "rev0031 foldmap predecessor failed"))
    except Exception as exc:  # pragma: no cover - audit defense
        predecessor_status = "exception"
        findings.append(ScopeFoldFinding("error", "predecessor_foldmap_exception", "src/i2p_dht_lab/foldmap.py", str(exc)))
    try:
        ledger = audit_surface_ledger(root_path, entries_for_revision(revision))
        surface_status = "pass" if ledger.ok else "fail"
        if ledger.error_count:
            findings.append(ScopeFoldFinding("error", "surface_ledger_failed", "src/i2p_dht_lab/surfaceledger.py", "rev0032 surface ledger failed"))
    except Exception as exc:  # pragma: no cover - audit defense
        surface_status = "exception"
        findings.append(ScopeFoldFinding("error", "surface_ledger_exception", "src/i2p_dht_lab/surfaceledger.py", str(exc)))
    status = "pass" if not any(item.severity == "error" for item in findings) else "fail"
    digest = sha256(SCOPE_FOLD_DOMAIN + b":report:" + bencode({
        b"revision": revision,
        b"artifact": artifact_stem,
        b"status": status,
        b"predecessor_status": predecessor_status,
        b"surface_status": surface_status,
        b"findings": [finding.bvalue() for finding in findings],
    }))
    return ScopeFoldReport(revision, artifact_stem, status, predecessor_status, surface_status, tuple(findings), digest)
