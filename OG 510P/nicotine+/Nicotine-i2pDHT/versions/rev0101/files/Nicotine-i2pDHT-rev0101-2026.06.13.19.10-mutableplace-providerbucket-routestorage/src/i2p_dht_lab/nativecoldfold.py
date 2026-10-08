"""rev0089 fold audit for native cold-start / probe corpus / loader-GC."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .foldmap import audit_fold_map
from .foldregistry import audit_fold_registry
from .ids import DOMAIN, sha256
from .nativecontrolfold import audit_native_control_fold
from .surfaceledger import audit_surface_ledger, entries_for_revision

NATIVE_COLD_FOLD_DOMAIN = DOMAIN + b":native-cold-fold-v1:"


@dataclass(frozen=True)
class NativeColdFoldFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class NativeColdFoldReport:
    revision: str
    artifact_stem: str
    status: str
    predecessor_status: str
    foldmap_status: str
    foldregistry_status: str
    surface_ledger_status: str
    findings: tuple[NativeColdFoldFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")


def _exists(root: Path, rel: str, needle: str, findings: list[NativeColdFoldFinding]) -> None:
    path = root / rel
    if not path.exists():
        findings.append(NativeColdFoldFinding("error", "missing_path", rel, "rev0089 expected this path"))
        return
    if needle not in path.read_text(encoding="utf-8", errors="replace"):
        findings.append(NativeColdFoldFinding("error", "missing_needle", rel, f"missing needle {needle!r}"))


def audit_native_cold_fold(root: str | Path, *, revision: str = "rev0089", artifact_stem: str = "") -> NativeColdFoldReport:
    root_path = Path(root)
    artifact = artifact_stem or root_path.name
    findings: list[NativeColdFoldFinding] = []
    checks = {
        "src/i2p_dht_lab/nativecoldstart.py": "NativeColdStartDecisionKind",
        "src/i2p_dht_lab/probecorpus.py": "NativeProbeCorpusDecisionKind",
        "src/i2p_dht_lab/loadergc.py": "NativeLoaderGcDecisionKind",
        "src/i2p_dht_lab/nativecoldfold.py": "audit_native_cold_fold",
        "tests/test_rev0089_nativecoldstart_probecorpus_loadergc.py": "test_native_cold_start_holds_probe_without_loading",
        "docs/928-rev0089-nativecoldstart-probecorpus-loadergc.md": "rev0089",
        "docs/929-native-cold-start-after-unload.md": "Native cold-start",
        "docs/930-probe-corpus-refresh.md": "Probe corpus",
        "docs/931-loader-gc-after-cold-start.md": "Loader-GC",
        "docs/932-nativecoldfold-audit-refactor.md": "nativecoldfold",
        "README.md": "nativecoldfold",
        "START_HERE.md": "nativecoldfold",
        "PUBLIC_SURFACE.json": "nativecoldstart",
        "HEAD_REGISTRY.json": "rev0089",
    }
    for rel, needle in checks.items():
        _exists(root_path, rel, needle, findings)
    predecessor = audit_native_control_fold(root_path, revision="rev0088", artifact_stem=artifact)
    fold_map = audit_fold_map(root_path, revision=revision, artifact_stem=artifact)
    fold_registry = audit_fold_registry(root_path, revision=revision)
    surface = audit_surface_ledger(root_path, entries_for_revision(revision))
    if predecessor.status != "pass":
        findings.append(NativeColdFoldFinding("error", "predecessor_failed", "rev0088", predecessor.status))
    if fold_map.status != "pass":
        findings.append(NativeColdFoldFinding("error", "foldmap_failed", "foldmap", fold_map.status))
    if fold_registry.status != "pass":
        findings.append(NativeColdFoldFinding("error", "foldregistry_failed", "foldregistry", fold_registry.status))
    if not surface.ok:
        findings.append(NativeColdFoldFinding("error", "surface_ledger_failed", "surfaceledger", str(surface.error_count)))
    status = "pass" if not any(f.severity == "error" for f in findings) else "fail"
    digest = sha256(NATIVE_COLD_FOLD_DOMAIN + bencode({
        b"revision": revision,
        b"artifact": artifact,
        b"status": status,
        b"predecessor": predecessor.status,
        b"foldmap": fold_map.status,
        b"registry": fold_registry.status,
        b"surface": 1 if surface.ok else 0,
        b"findings": [finding.bvalue() for finding in findings],
    }))
    return NativeColdFoldReport(revision, artifact, status, predecessor.status, fold_map.status, fold_registry.status, "pass" if surface.ok else "fail", tuple(findings), digest)
