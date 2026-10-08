"""rev0093 fold audit for native load loop / call canary / dispatch fence."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .foldmap import audit_fold_map
from .foldregistry import audit_fold_registry
from .ids import DOMAIN, sha256
from .nativefoldspine import audit_native_fold_spine
from .nativeloadreentryfold import audit_native_load_reentry_fold
from .surfaceledger import audit_surface_ledger, entries_for_revision

NATIVE_LOAD_LOOP_FOLD_DOMAIN = DOMAIN + b":native-load-loop-fold-v1:"


@dataclass(frozen=True)
class NativeLoadLoopFoldFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class NativeLoadLoopFoldReport:
    revision: str
    artifact_stem: str
    status: str
    predecessor_status: str
    foldmap_status: str
    foldregistry_status: str
    surface_ledger_status: str
    native_spine_status: str
    findings: tuple[NativeLoadLoopFoldFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")


def _exists(root: Path, rel: str, needle: str, findings: list[NativeLoadLoopFoldFinding]) -> None:
    path = root / rel
    if not path.exists():
        findings.append(NativeLoadLoopFoldFinding("error", "missing_path", rel, "rev0093 expected this path"))
        return
    if needle not in path.read_text(encoding="utf-8", errors="replace"):
        findings.append(NativeLoadLoopFoldFinding("error", "missing_needle", rel, f"missing needle {needle!r}"))


def audit_native_load_loop_fold(root: str | Path, *, revision: str = "rev0093", artifact_stem: str = "") -> NativeLoadLoopFoldReport:
    root_path = Path(root)
    artifact = artifact_stem or root_path.name
    findings: list[NativeLoadLoopFoldFinding] = []
    checks = {
        "src/i2p_dht_lab/nativeloadloop.py": "NativeLoadLoopDecisionKind",
        "src/i2p_dht_lab/nativecallcanary.py": "NativeCallCanaryDecisionKind",
        "src/i2p_dht_lab/dispatchfence.py": "NativeDispatchFenceDecisionKind",
        "src/i2p_dht_lab/nativefoldspine.py": "rev0093",
        "src/i2p_dht_lab/nativeloadloopfold.py": "audit_native_load_loop_fold",
        "tests/test_rev0093_nativeloadloop_callcanary_dispatchfence.py": "test_load_loop_call_canary_and_dispatch_fence_happy_path",
        "docs/968-rev0093-nativeloadloop-callcanary-dispatchfence.md": "rev0093",
        "docs/969-native-load-loopback.md": "Native load loopback",
        "docs/970-native-call-canary.md": "Native call canary",
        "docs/971-dispatch-fence.md": "Dispatch fence",
        "docs/972-nativeloadloopfold-audit-refactor.md": "nativeloadloopfold",
        "README.md": "nativeloadloopfold",
        "START_HERE.md": "nativeloadloopfold",
        "PUBLIC_SURFACE.json": "nativeloadloop",
        "HEAD_REGISTRY.json": "rev0093",
    }
    for rel, needle in checks.items():
        _exists(root_path, rel, needle, findings)
    predecessor = audit_native_load_reentry_fold(root_path, revision="rev0092", artifact_stem=artifact)
    fold_map = audit_fold_map(root_path, revision=revision, artifact_stem=artifact)
    fold_registry = audit_fold_registry(root_path, revision=revision)
    surface = audit_surface_ledger(root_path, entries_for_revision(revision))
    native_spine = audit_native_fold_spine(root_path, revision=revision)
    if predecessor.status != "pass":
        findings.append(NativeLoadLoopFoldFinding("error", "predecessor_failed", "rev0092", predecessor.status))
    if fold_map.status != "pass":
        findings.append(NativeLoadLoopFoldFinding("error", "foldmap_failed", "foldmap", fold_map.status))
    if fold_registry.status != "pass":
        findings.append(NativeLoadLoopFoldFinding("error", "foldregistry_failed", "foldregistry", fold_registry.status))
    if not surface.ok:
        findings.append(NativeLoadLoopFoldFinding("error", "surface_ledger_failed", "surfaceledger", str(surface.error_count)))
    if native_spine.status != "pass":
        findings.append(NativeLoadLoopFoldFinding("error", "native_spine_failed", "nativefoldspine", native_spine.status))
    status = "pass" if not any(f.severity == "error" for f in findings) else "fail"
    digest = sha256(NATIVE_LOAD_LOOP_FOLD_DOMAIN + bencode({
        b"revision": revision,
        b"artifact": artifact,
        b"status": status,
        b"predecessor": predecessor.status,
        b"foldmap": fold_map.status,
        b"registry": fold_registry.status,
        b"surface": 1 if surface.ok else 0,
        b"native_spine": native_spine.status,
        b"findings": [finding.bvalue() for finding in findings],
    }))
    return NativeLoadLoopFoldReport(revision, artifact, status, predecessor.status, fold_map.status, fold_registry.status, "pass" if surface.ok else "fail", native_spine.status, tuple(findings), digest)
