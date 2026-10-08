"""rev0094 native shadow/fault fold audit."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .foldmap import audit_fold_map
from .foldregistry import audit_fold_registry
from .ids import DOMAIN, sha256
from .nativefoldspine import audit_native_fold_spine
from .nativeloadloopfold import audit_native_load_loop_fold
from .surfaceledger import audit_surface_ledger, entries_for_revision

NATIVE_SHADOW_FOLD_DOMAIN = DOMAIN + b":native-shadow-fold-v1:"


@dataclass(frozen=True)
class NativeShadowFoldFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class NativeShadowFoldReport:
    revision: str
    artifact: str
    status: str
    predecessor_status: str
    fold_map_status: str
    fold_registry_status: str
    surface_ledger_status: str
    native_spine_status: str
    findings: tuple[NativeShadowFoldFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")


def audit_native_shadow_fold(root: str | Path, *, revision: str = "rev0094") -> NativeShadowFoldReport:
    root_path = Path(root)
    artifact = root_path.name
    findings: list[NativeShadowFoldFinding] = []
    required = (
        "src/i2p_dht_lab/nativeshadowcall.py",
        "src/i2p_dht_lab/resultdiff.py",
        "src/i2p_dht_lab/faultseal.py",
        "src/i2p_dht_lab/nativeshadowfold.py",
        "tests/test_rev0094_nativeshadowcall_resultdiff_faultseal.py",
        "docs/978-rev0094-nativeshadowcall-resultdiff-faultseal.md",
        "docs/979-native-shadow-call.md",
        "docs/980-native-result-diff.md",
        "docs/981-native-fault-seal.md",
        "docs/982-nativeshadowfold-audit-refactor.md",
    )
    for rel in required:
        if not (root_path / rel).exists():
            findings.append(NativeShadowFoldFinding("error", "missing_rev0094_surface", rel, "rev0094 surface is absent"))
    docs_index = (root_path / "docs" / "00-index.md").read_text(encoding="utf-8", errors="replace") if (root_path / "docs" / "00-index.md").exists() else ""
    for needle in ("rev0094", "nativeshadowcall", "resultdiff", "faultseal", "nativeshadowfold"):
        if needle not in docs_index:
            findings.append(NativeShadowFoldFinding("error", "missing_rev0094_index_anchor", "docs/00-index.md", f"missing {needle}"))
    readme = (root_path / "README.md").read_text(encoding="utf-8", errors="replace") if (root_path / "README.md").exists() else ""
    start_here = (root_path / "START_HERE.md").read_text(encoding="utf-8", errors="replace") if (root_path / "START_HERE.md").exists() else ""
    for needle in ("nativeloadloopfold", "nativeshadowfold"):
        if needle not in readme or needle not in start_here:
            findings.append(NativeShadowFoldFinding("error", "missing_native_shadow_anchor", needle, "README.md and START_HERE.md must retain predecessor/current anchors"))
    predecessor = audit_native_load_loop_fold(root_path, revision="rev0093")
    fold_map = audit_fold_map(root_path, revision=revision)
    fold_registry = audit_fold_registry(root_path, revision=revision)
    surface = audit_surface_ledger(root_path, entries_for_revision(revision))
    native_spine = audit_native_fold_spine(root_path, revision=revision)
    if predecessor.status != "pass":
        findings.append(NativeShadowFoldFinding("error", "predecessor_fold_failed", "nativeloadloopfold", predecessor.status))
    if fold_map.status != "pass":
        findings.append(NativeShadowFoldFinding("error", "fold_map_failed", "foldmap", fold_map.status))
    if fold_registry.status != "pass":
        findings.append(NativeShadowFoldFinding("error", "fold_registry_failed", "foldregistry", fold_registry.status))
    if not surface.ok:
        findings.append(NativeShadowFoldFinding("error", "surface_ledger_failed", "surfaceledger", "active ledger missing current revision"))
    if native_spine.status != "pass":
        findings.append(NativeShadowFoldFinding("error", "native_spine_failed", "nativefoldspine", native_spine.status))
    status = "pass" if not any(f.severity == "error" for f in findings) else "fail"
    digest = sha256(NATIVE_SHADOW_FOLD_DOMAIN + bencode({
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
    return NativeShadowFoldReport(revision, artifact, status, predecessor.status, fold_map.status, fold_registry.status, "pass" if surface.ok else "fail", native_spine.status, tuple(findings), digest)
