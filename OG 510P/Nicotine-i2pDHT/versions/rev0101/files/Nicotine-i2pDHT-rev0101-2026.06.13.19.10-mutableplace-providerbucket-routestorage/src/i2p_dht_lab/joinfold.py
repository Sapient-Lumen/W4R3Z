"""Current-revision joined-boundary audit for rev0026.

The cube now has enough historical fold modules that navigation drift is itself
a risk.  This audit checks only the rev0026 current path: joined scheduling,
custody/evidence GC, partition/witness merge, transport shadowing, and the docs
that describe them.  It does not delete old branchlets; it verifies the live
path is visible.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .ids import DOMAIN, sha256
from .surfaceledger import audit_surface_ledger, entries_for_revision

JOIN_FOLD_DOMAIN = DOMAIN + b":join-fold-v1:"


@dataclass(frozen=True)
class JoinFoldFinding:
    severity: str
    code: str
    path: str
    detail: str


@dataclass(frozen=True)
class JoinFoldReport:
    revision: str
    status: str
    findings: tuple[JoinFoldFinding, ...]
    checked_paths: tuple[str, ...]
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


def audit_join_fold(root: str | Path, *, revision: str = "rev0026") -> JoinFoldReport:
    root_path = Path(root)
    required = (
        "src/i2p_dht_lab/schedjoin.py",
        "src/i2p_dht_lab/custodygc.py",
        "src/i2p_dht_lab/partitionwitness.py",
        "src/i2p_dht_lab/transportshadow.py",
        "src/i2p_dht_lab/joinfold.py",
        "tests/test_rev0026_schedjoin_custodygc_transportshadow.py",
        "docs/240-rev0026-schedjoin-custodygc-transportshadow.md",
        "docs/241-joined-scheduling-after-capability.md",
        "docs/242-custody-evidence-gc-join.md",
        "docs/243-partition-witness-route-merge.md",
        "docs/244-transport-shadow-canonical-report-carrying.md",
        "docs/245-joinfold-audit-refactor.md",
    )
    findings: list[JoinFoldFinding] = []
    for rel in required:
        if not (root_path / rel).exists():
            findings.append(JoinFoldFinding("error", "missing_required_path", rel, "rev0026 joined-boundary path is absent"))
    for rel, needle in (
        ("PUBLIC_SURFACE.json", "docs/240-rev0026-schedjoin-custodygc-transportshadow.md"),
        ("HEAD_REGISTRY.json", "joined_scheduling"),
        ("docs/00-index.md", "rev0026 schedjoin / custodygc / transportshadow"),
        ("START_HERE.md", "rev0026"),
        ("README.md", "rev0026"),
    ):
        if not _contains(root_path / rel, needle):
            findings.append(JoinFoldFinding("error", "missing_pointer_text", rel, f"expected pointer text not found: {needle}"))
    try:
        ledger = audit_surface_ledger(root_path, entries_for_revision(revision))
        if ledger.error_count:
            findings.append(JoinFoldFinding("error", "surface_ledger_errors", "src/i2p_dht_lab/surfaceledger.py", "surface ledger has current revision errors"))
    except Exception as exc:  # pragma: no cover - defensive audit surface only
        findings.append(JoinFoldFinding("error", "surface_ledger_exception", "src/i2p_dht_lab/surfaceledger.py", str(exc)))
    status = "pass" if not any(item.severity == "error" for item in findings) else "fail"
    digest = sha256(JOIN_FOLD_DOMAIN + b":report:" + bencode({
        b"revision": revision,
        b"status": status,
        b"checked": list(required),
        b"findings": [{b"severity": item.severity, b"code": item.code, b"path": item.path, b"detail": item.detail} for item in findings],
    }))
    return JoinFoldReport(revision, status, tuple(findings), required, digest)
