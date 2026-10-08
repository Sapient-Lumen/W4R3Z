"""rev0096 native call-archive / promotion-denial / shadow-GC fold audit."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .foldmap import audit_fold_map
from .foldregistry import audit_fold_registry
from .ids import DOMAIN, sha256
from .nativefoldspine import audit_native_fold_spine
from .nativesettlementfold import audit_native_settlement_fold
from .surfaceledger import audit_surface_ledger, entries_for_revision

NATIVE_ARCHIVE_FOLD_DOMAIN = DOMAIN + b":native-archive-fold-v1:"


@dataclass(frozen=True)
class NativeArchiveFoldFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class NativeArchiveFoldReport:
    revision: str
    artifact: str
    status: str
    predecessor_status: str
    fold_map_status: str
    fold_registry_status: str
    surface_ledger_status: str
    native_spine_status: str
    findings: tuple[NativeArchiveFoldFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")


def audit_native_archive_fold(root: str | Path, *, revision: str = "rev0096") -> NativeArchiveFoldReport:
    root_path = Path(root)
    artifact = root_path.name
    findings: list[NativeArchiveFoldFinding] = []
    required = (
        "src/i2p_dht_lab/nativecallarchive.py",
        "src/i2p_dht_lab/nativepromotiondeny.py",
        "src/i2p_dht_lab/nativeshadowgc.py",
        "src/i2p_dht_lab/nativearchivefold.py",
        "src/i2p_dht_lab/nativefoldspine.py",
        "tests/test_rev0096_callarchive_promotedeny_shadowgc.py",
        "docs/998-rev0096-callarchive-promotedeny-shadowgc.md",
        "docs/999-native-call-archive.md",
        "docs/1000-native-promotion-denial.md",
        "docs/1001-native-shadow-gc.md",
        "docs/1002-nativearchivefold-audit-refactor.md",
    )
    for rel in required:
        if not (root_path / rel).exists():
            findings.append(NativeArchiveFoldFinding("error", "missing_rev0096_surface", rel, "rev0096 surface is absent"))
    docs_index = (root_path / "docs" / "00-index.md").read_text(encoding="utf-8", errors="replace") if (root_path / "docs" / "00-index.md").exists() else ""
    for needle in ("rev0096", "nativecallarchive", "nativepromotiondeny", "nativeshadowgc", "nativearchivefold"):
        if needle not in docs_index:
            findings.append(NativeArchiveFoldFinding("error", "missing_rev0096_index_anchor", "docs/00-index.md", f"missing {needle}"))
    readme = (root_path / "README.md").read_text(encoding="utf-8", errors="replace") if (root_path / "README.md").exists() else ""
    start_here = (root_path / "START_HERE.md").read_text(encoding="utf-8", errors="replace") if (root_path / "START_HERE.md").exists() else ""
    for needle in ("nativesettlementfold", "nativearchivefold"):
        if needle not in readme or needle not in start_here:
            findings.append(NativeArchiveFoldFinding("error", "missing_native_archive_anchor", needle, "README.md and START_HERE.md must retain predecessor/current anchors"))
    predecessor = audit_native_settlement_fold(root_path, revision="rev0095")
    fold_map = audit_fold_map(root_path, revision=revision)
    fold_registry = audit_fold_registry(root_path, revision=revision)
    surface = audit_surface_ledger(root_path, entries_for_revision(revision))
    native_spine = audit_native_fold_spine(root_path, revision=revision)
    if predecessor.status != "pass":
        findings.append(NativeArchiveFoldFinding("error", "predecessor_fold_failed", "nativesettlementfold", predecessor.status))
    if fold_map.status != "pass":
        findings.append(NativeArchiveFoldFinding("error", "fold_map_failed", "foldmap", fold_map.status))
    if fold_registry.status != "pass":
        findings.append(NativeArchiveFoldFinding("error", "fold_registry_failed", "foldregistry", fold_registry.status))
    if not surface.ok:
        findings.append(NativeArchiveFoldFinding("error", "surface_ledger_failed", "surfaceledger", "active ledger missing current revision"))
    if native_spine.status != "pass":
        findings.append(NativeArchiveFoldFinding("error", "native_spine_failed", "nativefoldspine", native_spine.status))
    status = "pass" if not any(f.severity == "error" for f in findings) else "fail"
    digest = sha256(NATIVE_ARCHIVE_FOLD_DOMAIN + bencode({
        b"revision": revision,
        b"artifact": artifact,
        b"status": status,
        b"predecessor": predecessor.status,
        b"foldmap": fold_map.status,
        b"foldregistry": fold_registry.status,
        b"surface": 1 if surface.ok else 0,
        b"native_spine": native_spine.status,
        b"findings": [finding.bvalue() for finding in findings],
    }))
    return NativeArchiveFoldReport(revision, artifact, status, predecessor.status, fold_map.status, fold_registry.status, "pass" if surface.ok else "fail", native_spine.status, tuple(findings), digest)
