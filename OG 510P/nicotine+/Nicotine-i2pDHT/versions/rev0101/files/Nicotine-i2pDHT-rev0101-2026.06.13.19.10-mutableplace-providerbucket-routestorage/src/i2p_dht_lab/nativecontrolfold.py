"""rev0088 fold audit for native unload / sandbox stubs / crash-ledger GC."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .foldmap import audit_fold_map
from .foldregistry import audit_fold_registry
from .ids import DOMAIN, sha256
from .nativelifecyclefold import audit_native_lifecycle_fold
from .surfaceledger import audit_surface_ledger, entries_for_revision

NATIVE_CONTROL_FOLD_DOMAIN = DOMAIN + b":native-control-fold-v1:"


@dataclass(frozen=True)
class NativeControlFoldFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class NativeControlFoldReport:
    revision: str
    artifact_stem: str
    status: str
    predecessor_status: str
    foldmap_status: str
    foldregistry_status: str
    surface_ledger_status: str
    findings: tuple[NativeControlFoldFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")


def _exists(root: Path, rel: str, needle: str, findings: list[NativeControlFoldFinding]) -> None:
    path = root / rel
    if not path.exists():
        findings.append(NativeControlFoldFinding("error", "missing_path", rel, "rev0088 expected this path"))
        return
    if needle not in path.read_text(encoding="utf-8", errors="replace"):
        findings.append(NativeControlFoldFinding("error", "missing_needle", rel, f"missing needle {needle!r}"))


def audit_native_control_fold(root: str | Path, *, revision: str = "rev0088", artifact_stem: str = "") -> NativeControlFoldReport:
    root_path = Path(root)
    artifact = artifact_stem or root_path.name
    findings: list[NativeControlFoldFinding] = []
    checks = {
        "src/i2p_dht_lab/nativeunload.py": "NativeUnloadDecisionKind",
        "src/i2p_dht_lab/nativesandboxstub.py": "NativeSandboxDecisionKind",
        "src/i2p_dht_lab/nativecrashgc.py": "NativeCrashGcDecisionKind",
        "src/i2p_dht_lab/nativecontrolfold.py": "audit_native_control_fold",
        "tests/test_rev0088_nativeunload_sandboxstub_crashgc.py": "test_native_unload_forces_faults_to_fallback_and_quarantine",
        "docs/918-rev0088-nativeunload-sandboxstub-crashgc.md": "rev0088",
        "docs/919-native-unload-quarantine-boundary.md": "Native unload",
        "docs/920-native-sandbox-stub.md": "sandbox-stub",
        "docs/921-native-crash-gc.md": "crash-ledger GC",
        "docs/922-nativecontrolfold-audit-refactor.md": "nativecontrolfold",
        "README.md": "nativecontrolfold",
        "START_HERE.md": "nativecontrolfold",
        "PUBLIC_SURFACE.json": "nativeunload",
        "HEAD_REGISTRY.json": "rev0088",
    }
    for rel, needle in checks.items():
        _exists(root_path, rel, needle, findings)
    predecessor = audit_native_lifecycle_fold(root_path, revision="rev0087", artifact_stem=artifact)
    fold_map = audit_fold_map(root_path, revision=revision, artifact_stem=artifact)
    fold_registry = audit_fold_registry(root_path, revision=revision)
    surface = audit_surface_ledger(root_path, entries_for_revision(revision))
    if predecessor.status != "pass":
        findings.append(NativeControlFoldFinding("error", "predecessor_failed", "rev0087", predecessor.status))
    if fold_map.status != "pass":
        findings.append(NativeControlFoldFinding("error", "foldmap_failed", "foldmap", fold_map.status))
    if fold_registry.status != "pass":
        findings.append(NativeControlFoldFinding("error", "foldregistry_failed", "foldregistry", fold_registry.status))
    if not surface.ok:
        findings.append(NativeControlFoldFinding("error", "surface_ledger_failed", "surfaceledger", str(surface.error_count)))
    status = "pass" if not any(f.severity == "error" for f in findings) else "fail"
    digest = sha256(NATIVE_CONTROL_FOLD_DOMAIN + bencode({
        b"revision": revision,
        b"artifact": artifact,
        b"status": status,
        b"predecessor": predecessor.status,
        b"foldmap": fold_map.status,
        b"registry": fold_registry.status,
        b"surface": 1 if surface.ok else 0,
        b"findings": [finding.bvalue() for finding in findings],
    }))
    return NativeControlFoldReport(revision, artifact, status, predecessor.status, fold_map.status, fold_registry.status, "pass" if surface.ok else "fail", tuple(findings), digest)
