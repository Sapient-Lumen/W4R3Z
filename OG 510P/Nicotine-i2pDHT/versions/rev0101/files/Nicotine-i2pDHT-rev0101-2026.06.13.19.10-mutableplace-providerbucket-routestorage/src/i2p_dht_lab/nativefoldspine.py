"""Compact native/GCC fold-spine audit through rev0099.

Earlier revisions extended this file by appending override functions.  rev0097
compacts the native branch into one table and one audit function so the GCC line
is easy to read after restart/amnesia.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .ids import DOMAIN, sha256

NATIVE_FOLD_SPINE_DOMAIN = DOMAIN + b":native-fold-spine-v2:"

NATIVE_SPINE: tuple[tuple[str, str, str], ...] = (
    ("rev0081", "src/i2p_dht_lab/nativeboundary.py", "nativeboundaryfold"),
    ("rev0082", "src/i2p_dht_lab/nativeparity.py", "nativeparityfold"),
    ("rev0083", "src/i2p_dht_lab/nativeruntime.py", "nativedispatchfold"),
    ("rev0084", "src/i2p_dht_lab/parserhold.py", "nativebudgetfold"),
    ("rev0085", "src/i2p_dht_lab/nativeprovenance.py", "nativeprovenancefold"),
    ("rev0086", "src/i2p_dht_lab/nativeselection.py", "nativeselectionfold"),
    ("rev0087", "src/i2p_dht_lab/nativeload.py", "nativelifecyclefold"),
    ("rev0088", "src/i2p_dht_lab/nativeunload.py", "nativecontrolfold"),
    ("rev0089", "src/i2p_dht_lab/nativecoldstart.py", "nativecoldfold"),
    ("rev0090", "src/i2p_dht_lab/nativehandoff.py", "nativehandofffold"),
    ("rev0091", "src/i2p_dht_lab/nativepreflight.py", "nativereentryfold"),
    ("rev0092", "src/i2p_dht_lab/nativeloadreentry.py", "nativeloadreentryfold"),
    ("rev0093", "src/i2p_dht_lab/nativeloadloop.py", "nativeloadloopfold"),
    ("rev0094", "src/i2p_dht_lab/nativeshadowcall.py", "nativeshadowfold"),
    ("rev0095", "src/i2p_dht_lab/nativeshadowsettlement.py", "nativesettlementfold"),
    ("rev0096", "src/i2p_dht_lab/nativecallarchive.py", "nativearchivefold"),
    ("rev0097", "src/i2p_dht_lab/nativearchivereplay.py", "nativearchivereplayfold"),
    ("rev0098", "src/i2p_dht_lab/nativepromotearchive.py", "nativebranchclosefold"),
    ("rev0099", "src/i2p_dht_lab/recordplaneoracle.py", "substratereturnfold"),
)

REQUIRED_BY_REVISION: dict[str, tuple[str, ...]] = {
    "rev0091": ("nativepreflight", "nativefoldspine"),
    "rev0092": ("nativeloadreentry", "revalidationseal", "nativecallhold", "nativefoldspine"),
    "rev0093": ("nativeloadloop", "nativecallcanary", "dispatchfence", "nativeloadloopfold", "nativefoldspine"),
    "rev0094": ("nativeshadowcall", "resultdiff", "faultseal", "nativeshadowfold", "nativefoldspine"),
    "rev0095": ("nativeshadowsettlement", "nativeadmission", "nativecallledger", "nativesettlementfold", "nativefoldspine"),
    "rev0096": ("nativecallarchive", "nativepromotiondeny", "nativeshadowgc", "nativearchivefold", "nativefoldspine"),
    "rev0097": ("nativearchivereplay", "nativepromotereview", "nativearchivereplayfold", "nativefoldspine"),
    "rev0098": ("nativepromotearchive", "nativepromotionpolicy", "nativebranchclose", "nativebranchclosefold", "nativefoldspine"),
    "rev0099": ("recordplaneoracle", "substratereentry", "substratereturnfold", "nativebranchclosefold", "nativefoldspine"),
}


@dataclass(frozen=True)
class NativeFoldSpineFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class NativeFoldSpineReport:
    revision: str
    status: str
    checked_count: int
    findings: tuple[NativeFoldSpineFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")


def audit_native_fold_spine(root: str | Path, *, revision: str = "rev0099") -> NativeFoldSpineReport:
    root_path = Path(root)
    findings: list[NativeFoldSpineFinding] = []
    readme = (root_path / "README.md").read_text(encoding="utf-8", errors="replace") if (root_path / "README.md").exists() else ""
    start_here = (root_path / "START_HERE.md").read_text(encoding="utf-8", errors="replace") if (root_path / "START_HERE.md").exists() else ""
    docs_index = root_path / "docs" / "00-index.md"
    index_text = docs_index.read_text(encoding="utf-8", errors="replace") if docs_index.exists() else ""

    seen_revs: set[str] = set()
    for rev, rel, needle in NATIVE_SPINE:
        if rev in seen_revs:
            findings.append(NativeFoldSpineFinding("error", "duplicate_native_spine_revision", rev, "native spine revision repeated"))
        seen_revs.add(rev)
        path = root_path / rel
        if not path.exists():
            findings.append(NativeFoldSpineFinding("error", "missing_native_spine_path", rel, f"{rev} expected native spine path"))
        if needle not in readme or needle not in start_here:
            findings.append(NativeFoldSpineFinding("error", "missing_native_spine_anchor", f"{rev}:{needle}", "README.md and START_HERE.md must retain native fold anchors"))
    required_needles = REQUIRED_BY_REVISION.get(revision, ("nativefoldspine",))
    if revision not in index_text or any(needle not in index_text for needle in required_needles):
        findings.append(NativeFoldSpineFinding("error", "current_native_spine_index_missing", "docs/00-index.md", "current native spine path is not indexed"))
    status = "pass" if not any(finding.severity == "error" for finding in findings) else "fail"
    digest = sha256(NATIVE_FOLD_SPINE_DOMAIN + bencode({
        b"revision": revision,
        b"status": status,
        b"checked": len(NATIVE_SPINE),
        b"findings": [finding.bvalue() for finding in findings],
    }))
    return NativeFoldSpineReport(revision, status, len(NATIVE_SPINE), tuple(findings), digest)
