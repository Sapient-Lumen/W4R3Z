"""Audit/refactor surface for formerly under-surfaced branchlet modules.

The cube has deliberately accumulated speculative branchlets.  That is useful
for wake-from-amnesia, but it becomes dangerous when code exists without a clear
current narrative or tests.  This audit does not delete history.  It makes a
small named set of branchlet modules visible and asks whether each has at least
one doc mention, one test mention, and an active-surface-ledger entry.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .ids import DOMAIN, sha256
from .surfaceledger import active_entries

BRANCHLET_FOLD_DOMAIN = DOMAIN + b":branchlet-fold-v1:"


@dataclass(frozen=True)
class BranchletSurface:
    module: str
    symbol: str
    expected_doc_fragment: str


@dataclass(frozen=True)
class BranchletFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class BranchletFoldReport:
    revision: str
    branchlets: tuple[BranchletSurface, ...]
    findings: tuple[BranchletFinding, ...]
    digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for item in self.findings if item.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for item in self.findings if item.severity == "warning")

    @property
    def status(self) -> str:
        if self.error_count:
            return "error"
        if self.warning_count:
            return "warn"
        return "pass"


def rev0024_branchlets() -> tuple[BranchletSurface, ...]:
    return (
        BranchletSurface("src/i2p_dht_lab/interestledger.py", "InterestLedger", "interest ledger"),
        BranchletSurface("src/i2p_dht_lab/pressureledger.py", "PressureRound", "pressure ledger"),
        BranchletSurface("src/i2p_dht_lab/regionreceipt.py", "RegionSweepReceipt", "region receipt"),
        BranchletSurface("src/i2p_dht_lab/relayticket.py", "RelayTicket", "relay ticket"),
        BranchletSurface("src/i2p_dht_lab/gossipsieve.py", "GossipCandidate", "gossip sieve"),
        BranchletSurface("src/i2p_dht_lab/clockguard.py", "TimedObservation", "clock guard"),
    )


def audit_branchlet_fold(root: str | Path, *, revision: str = "rev0024", branchlets: tuple[BranchletSurface, ...] | None = None) -> BranchletFoldReport:
    root_path = Path(root)
    branchlets = branchlets or rev0024_branchlets()
    ledger_modules = {entry.module for entry in active_entries()}
    all_tests_text = ""
    tests_dir = root_path / "tests"
    if tests_dir.exists():
        all_tests_text = "\n".join(path.read_text(encoding="utf-8", errors="replace") for path in tests_dir.glob("test_*.py"))
    docs_text = ""
    docs_dir = root_path / "docs"
    if docs_dir.exists():
        docs_text = "\n".join(path.read_text(encoding="utf-8", errors="replace") for path in docs_dir.glob("*.md"))
    findings: list[BranchletFinding] = []
    for surface in branchlets:
        module_path = root_path / surface.module
        if not module_path.exists():
            findings.append(BranchletFinding("error", "missing_branchlet_module", surface.module, "branchlet module is missing"))
            continue
        module_text = module_path.read_text(encoding="utf-8", errors="replace")
        if surface.symbol not in module_text:
            findings.append(BranchletFinding("error", "missing_branchlet_symbol", surface.module, f"expected symbol {surface.symbol} is absent"))
        if surface.module not in ledger_modules:
            findings.append(BranchletFinding("warning", "branchlet_not_in_surface_ledger", surface.module, "branchlet module is not surfaced in active surface ledger"))
        if surface.symbol not in all_tests_text:
            findings.append(BranchletFinding("warning", "branchlet_symbol_not_tested", surface.module, f"{surface.symbol} is not mentioned in tests"))
        if surface.expected_doc_fragment.lower() not in docs_text.lower():
            findings.append(BranchletFinding("warning", "branchlet_not_documented", surface.module, f"doc fragment '{surface.expected_doc_fragment}' is absent"))
    digest = sha256(BRANCHLET_FOLD_DOMAIN + b":report:" + bencode({
        b"revision": revision,
        b"branchlets": [{b"module": b.module, b"symbol": b.symbol, b"fragment": b.expected_doc_fragment} for b in branchlets],
        b"findings": [finding.bvalue() for finding in findings],
    }))
    return BranchletFoldReport(revision, branchlets, tuple(findings), digest)
