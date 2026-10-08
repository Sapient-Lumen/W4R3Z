"""Audit/refactor fold for rev0024 clock/relay/gossip surfaces."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .ids import DOMAIN, sha256
from .surfaceledger import active_entries

CLOCK_FOLD_DOMAIN = DOMAIN + b":clock-fold-v1:"


@dataclass(frozen=True)
class ClockFoldFinding:
    severity: str
    code: str
    path: str
    detail: str


@dataclass(frozen=True)
class ClockFoldReport:
    revision: str
    status: str
    checked_paths: tuple[str, ...]
    findings: tuple[ClockFoldFinding, ...]
    digest: bytes

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")


def audit_clock_fold(root: str | Path, *, revision: str) -> ClockFoldReport:
    root_path = Path(root)
    expected = (
        "src/i2p_dht_lab/clockguard.py",
        "src/i2p_dht_lab/relayticket.py",
        "src/i2p_dht_lab/gossipsieve.py",
        "src/i2p_dht_lab/clockfold.py",
        "tests/test_rev0024_relayticket_gossipsieve_clockguard.py",
        "docs/222-clock-guard-and-time-window-pressure.md",
        "docs/223-relay-ticket-garden-capacity-boundaries.md",
        "docs/224-gossip-sieve-before-expensive-work.md",
        "docs/225-branchlet-fold-audit-refactor.md",
    )
    findings: list[ClockFoldFinding] = []
    for rel in expected:
        if not (root_path / rel).exists():
            findings.append(ClockFoldFinding("error", "missing_clock_fold_path", rel, "rev0024 clock/relay/gossip surface path is missing"))
    ledger_modules = {entry.module for entry in active_entries()}
    for rel in expected[:4]:
        if rel not in ledger_modules:
            findings.append(ClockFoldFinding("error", "missing_surface_ledger_entry", rel, "rev0024 module is not in the active surface ledger"))
    docs_index = (root_path / "docs/00-index.md").read_text(encoding="utf-8") if (root_path / "docs/00-index.md").exists() else ""
    for rel in expected[5:9]:
        if rel not in docs_index:
            findings.append(ClockFoldFinding("error", "missing_docs_index_pointer", rel, "rev0024 doc is not linked from docs/00-index.md"))
    version_text = (root_path / "VERSION").read_text(encoding="utf-8").strip() if (root_path / "VERSION").exists() else ""
    if version_text and version_text < revision:
        findings.append(ClockFoldFinding("error", "version_drift", "VERSION", f"expected at least {revision}, found {version_text!r}"))
    status = "pass" if not any(finding.severity == "error" for finding in findings) else "fail"
    digest = sha256(CLOCK_FOLD_DOMAIN + b":report:" + bencode({
        b"revision": revision,
        b"status": status,
        b"checked": list(expected),
        b"findings": [{b"severity": item.severity, b"code": item.code, b"path": item.path, b"detail": item.detail} for item in findings],
    }))
    return ClockFoldReport(revision, status, expected, tuple(findings), digest)
