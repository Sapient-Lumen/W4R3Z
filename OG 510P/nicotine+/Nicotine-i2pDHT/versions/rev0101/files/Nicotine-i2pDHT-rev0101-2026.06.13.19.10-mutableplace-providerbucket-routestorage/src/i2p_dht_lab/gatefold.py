"""Gate-fold audit for rev0024 interest/probe/route/dispatch seams.

rev0024 deliberately folds a useful alternate rev0023 branchlet into the main
line.  This audit keeps that refactor explicit: interest mixing, route
attestation, and dispatch-gate auditing must be visible from the public surface,
the active surface ledger, the docs index, and the historical supersession map.

This is not a protocol validator.  It is wake-from-amnesia hygiene for the seam
between metadata-budgeted probes, path-captured entrances, and validated payload
handler dispatch.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .ids import DOMAIN, sha256
from .surfaceledger import active_entries

GATE_FOLD_DOMAIN = DOMAIN + b":gate-fold-v1:"


@dataclass(frozen=True)
class GateFoldFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class GateFoldReport:
    revision: str
    expected_surfaces: tuple[str, ...]
    findings: tuple[GateFoldFinding, ...]
    digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")

    @property
    def status(self) -> str:
        if self.error_count:
            return "fail"
        if self.warning_count:
            return "warn"
        return "pass"

    def as_dict(self) -> dict[str, object]:
        return {
            "schema": "i2p_dht_lab.gate_fold_report.v1",
            "revision": self.revision,
            "status": self.status,
            "warning_count": self.warning_count,
            "error_count": self.error_count,
            "expected_surfaces": list(self.expected_surfaces),
            "findings": [finding.__dict__ for finding in self.findings],
            "digest_hex": self.digest.hex(),
        }


def _load_json(root_path: Path, rel: str) -> object:
    path = root_path / rel
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def audit_gate_fold(root: str | Path, *, revision: str = "rev0024") -> GateFoldReport:
    root_path = Path(root)
    findings: list[GateFoldFinding] = []
    expected = (
        "src/i2p_dht_lab/interestmix.py",
        "src/i2p_dht_lab/routeattest.py",
        "src/i2p_dht_lab/gateaudit.py",
        "src/i2p_dht_lab/gatefold.py",
        "tests/test_rev0024_interestmix_routeattest_gatefold.py",
        "docs/213-rev0024-interestmix-routeattest-gatefold.md",
        "docs/214-interest-mixing-provider-probe-pressure.md",
        "docs/215-route-attestation-capture-pressure.md",
        "docs/216-dispatch-gate-audit-refactor.md",
        "docs/217-gatefold-branchlet-refactor.md",
        "docs/218-python-surface-rev0024.md",
        "docs/219-wake-from-amnesia-rev0024.md",
    )

    for rel in expected:
        if not (root_path / rel).exists():
            findings.append(GateFoldFinding("error", "missing_expected_surface", rel, "rev0024 gatefold surface is absent"))

    ledger_paths = {entry.module for entry in active_entries()} | {entry.test for entry in active_entries()} | {entry.doc for entry in active_entries()}
    ledger_required = set(expected[:5]) | {
        "docs/214-interest-mixing-provider-probe-pressure.md",
        "docs/215-route-attestation-capture-pressure.md",
        "docs/216-dispatch-gate-audit-refactor.md",
        "docs/217-gatefold-branchlet-refactor.md",
    }
    for rel in sorted(ledger_required):
        if rel not in ledger_paths:
            findings.append(GateFoldFinding("warning", "not_in_surface_ledger", rel, "active rev0024 gatefold surface is not listed in active surface ledger"))

    public = _load_json(root_path, "PUBLIC_SURFACE.json")
    public_paths = {str(entry.get("path", "")) for entry in public.get("entry_points", [])} if isinstance(public, dict) else set()
    if isinstance(public, dict) and str(public.get("revision", "")) < revision:
        findings.append(GateFoldFinding("error", "public_revision_drift", "PUBLIC_SURFACE.json", "public surface revision is older than gatefold revision"))
    for rel in ("docs/213-rev0024-interestmix-routeattest-gatefold.md", "docs/217-gatefold-branchlet-refactor.md", "docs/219-wake-from-amnesia-rev0024.md"):
        if rel not in public_paths:
            findings.append(GateFoldFinding("warning", "public_surface_missing_gatefold_path", rel, "public surface does not expose an important rev0024 path"))

    index_text = (root_path / "docs/00-index.md").read_text(encoding="utf-8") if (root_path / "docs/00-index.md").exists() else ""
    if revision not in index_text or "interestmix" not in index_text or "gatefold" not in index_text:
        findings.append(GateFoldFinding("error", "index_missing_current_gatefold", "docs/00-index.md", "docs index does not expose current rev0024 gatefold surface"))

    supersession_text = (root_path / "HISTORICAL_SUPERSESSION.json").read_text(encoding="utf-8") if (root_path / "HISTORICAL_SUPERSESSION.json").exists() else ""
    for needle in ("interestmix-routeattest-gateaudit", "interestmix.py", "routeattest.py", "gateaudit.py"):
        if needle not in supersession_text:
            findings.append(GateFoldFinding("warning", "supersession_missing_branchlet_marker", "HISTORICAL_SUPERSESSION.json", f"historical map does not mention {needle!r}"))

    digest = sha256(GATE_FOLD_DOMAIN + b":report:" + bencode({
        b"revision": revision,
        b"expected": list(expected),
        b"findings": [finding.bvalue() for finding in findings],
    }))
    return GateFoldReport(revision, expected, tuple(findings), digest)
