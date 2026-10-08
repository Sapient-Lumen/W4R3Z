"""rev0087 fold audit for native load / crash ledger / performance guard."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .foldmap import audit_fold_map
from .foldregistry import audit_fold_registry
from .ids import DOMAIN, sha256
from .nativeselectionfold import audit_native_selection_fold
from .surfaceledger import audit_surface_ledger, entries_for_revision

NATIVE_LIFECYCLE_FOLD_DOMAIN = DOMAIN + b":native-lifecycle-fold-v1:"


@dataclass(frozen=True)
class NativeLifecycleFoldFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class NativeLifecycleFoldReport:
    revision: str
    artifact_stem: str
    status: str
    predecessor_status: str
    foldmap_status: str
    foldregistry_status: str
    surface_ledger_status: str
    findings: tuple[NativeLifecycleFoldFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")


def _exists(root: Path, rel: str, needle: str, findings: list[NativeLifecycleFoldFinding]) -> None:
    path = root / rel
    if not path.exists():
        findings.append(NativeLifecycleFoldFinding("error", "missing_path", rel, "rev0087 expected this path"))
        return
    if needle not in path.read_text(encoding="utf-8", errors="replace"):
        findings.append(NativeLifecycleFoldFinding("error", "missing_needle", rel, f"missing needle {needle!r}"))


def audit_native_lifecycle_fold(root: str | Path, *, revision: str = "rev0087", artifact_stem: str = "") -> NativeLifecycleFoldReport:
    root_path = Path(root)
    artifact = artifact_stem or root_path.name
    findings: list[NativeLifecycleFoldFinding] = []
    checks = {
        "src/i2p_dht_lab/nativeload.py": "NativeLoadDecisionKind",
        "src/i2p_dht_lab/nativecrashledger.py": "NativeCrashDecisionKind",
        "src/i2p_dht_lab/nativeperfguard.py": "NativePerfDecisionKind",
        "src/i2p_dht_lab/nativelifecyclefold.py": "audit_native_lifecycle_fold",
        "tests/test_rev0087_nativeload_crashledger_perfguard.py": "test_native_load_accepts_only_after_selection_and_promotion_bind",
        "docs/908-rev0087-nativeload-crashledger-perfguard.md": "rev0087",
        "docs/909-native-load-lifecycle-boundary.md": "Native load",
        "docs/910-native-crash-ledger.md": "crash ledger",
        "docs/911-native-performance-guard.md": "performance guard",
        "docs/912-nativelifecyclefold-audit-refactor.md": "nativelifecyclefold",
        "README.md": "nativelifecyclefold",
        "START_HERE.md": "nativelifecyclefold",
        "PUBLIC_SURFACE.json": "nativeload",
        "HEAD_REGISTRY.json": "rev0087",
    }
    for rel, needle in checks.items():
        _exists(root_path, rel, needle, findings)
    predecessor = audit_native_selection_fold(root_path, revision="rev0086", artifact_stem=artifact)
    fold_map = audit_fold_map(root_path, revision=revision, artifact_stem=artifact)
    fold_registry = audit_fold_registry(root_path, revision=revision)
    surface = audit_surface_ledger(root_path, entries_for_revision(revision))
    if predecessor.status != "pass":
        findings.append(NativeLifecycleFoldFinding("error", "predecessor_failed", "rev0086", predecessor.status))
    if fold_map.status != "pass":
        findings.append(NativeLifecycleFoldFinding("error", "foldmap_failed", "foldmap", fold_map.status))
    if fold_registry.status != "pass":
        findings.append(NativeLifecycleFoldFinding("error", "foldregistry_failed", "foldregistry", fold_registry.status))
    if not surface.ok:
        findings.append(NativeLifecycleFoldFinding("error", "surface_ledger_failed", "surfaceledger", str(surface.error_count)))
    status = "pass" if not any(f.severity == "error" for f in findings) else "fail"
    digest = sha256(NATIVE_LIFECYCLE_FOLD_DOMAIN + bencode({
        b"revision": revision,
        b"artifact": artifact,
        b"status": status,
        b"predecessor": predecessor.status,
        b"foldmap": fold_map.status,
        b"registry": fold_registry.status,
        b"surface": 1 if surface.ok else 0,
        b"findings": [finding.bvalue() for finding in findings],
    }))
    return NativeLifecycleFoldReport(revision, artifact, status, predecessor.status, fold_map.status, fold_registry.status, "pass" if surface.ok else "fail", tuple(findings), digest)
