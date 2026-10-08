"""Substrate-DHT spine after returning from the native branch."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .ids import DOMAIN, sha256

SUBSTRATE_SPINE_DOMAIN = DOMAIN + b":substrate-spine-v1:"

SUBSTRATE_SPINE: tuple[tuple[str, str, str], ...] = (
    ("rev0099", "src/i2p_dht_lab/substratereentry.py", "substratereturnfold"),
    ("rev0100", "src/i2p_dht_lab/recordingress.py", "substratecenturyfold"),
    ("rev0101", "src/i2p_dht_lab/mutableplacement.py", "substrateplacementfold"),
)

REQUIRED_BY_REVISION: dict[str, tuple[str, ...]] = {
    "rev0099": ("recordplaneoracle", "substratereentry", "substratereturnfold"),
    "rev0100": ("recordingress", "providersemantics", "routinganchor", "substratespine", "substratecenturyfold"),
    "rev0101": ("mutableplacement", "providerbucket", "routestorage", "substratespine", "substrateplacementfold"),
}


@dataclass(frozen=True)
class SubstrateSpineFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class SubstrateSpineReport:
    revision: str
    status: str
    checked_count: int
    findings: tuple[SubstrateSpineFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")


def audit_substrate_spine(root: str | Path, *, revision: str = "rev0101") -> SubstrateSpineReport:
    root_path = Path(root)
    findings: list[SubstrateSpineFinding] = []
    readme = (root_path / "README.md").read_text(encoding="utf-8", errors="replace") if (root_path / "README.md").exists() else ""
    start = (root_path / "START_HERE.md").read_text(encoding="utf-8", errors="replace") if (root_path / "START_HERE.md").exists() else ""
    index = (root_path / "docs" / "00-index.md").read_text(encoding="utf-8", errors="replace") if (root_path / "docs" / "00-index.md").exists() else ""
    seen: set[str] = set()
    for rev, rel, needle in SUBSTRATE_SPINE:
        if rev in seen:
            findings.append(SubstrateSpineFinding("error", "duplicate_substrate_spine_revision", rev, "substrate spine revision repeated"))
        seen.add(rev)
        if not (root_path / rel).exists():
            findings.append(SubstrateSpineFinding("error", "missing_substrate_spine_path", rel, f"{rev} expected substrate spine path"))
        if needle not in readme or needle not in start:
            findings.append(SubstrateSpineFinding("error", "missing_substrate_spine_anchor", f"{rev}:{needle}", "README.md and START_HERE.md must retain substrate fold anchors"))
    required = REQUIRED_BY_REVISION.get(revision, ("substratespine",))
    if revision not in index or any(needle not in index for needle in required):
        findings.append(SubstrateSpineFinding("error", "current_substrate_spine_index_missing", "docs/00-index.md", "current substrate spine path is not indexed"))
    status = "pass" if not any(finding.severity == "error" for finding in findings) else "fail"
    digest = sha256(SUBSTRATE_SPINE_DOMAIN + bencode({
        b"revision": revision,
        b"status": status,
        b"checked": len(SUBSTRATE_SPINE),
        b"findings": [finding.bvalue() for finding in findings],
    }))
    return SubstrateSpineReport(revision, status, len(SUBSTRATE_SPINE), tuple(findings), digest)
