"""rev0090 fold audit for native handoff / relaunch gate / loader seal."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .foldmap import audit_fold_map
from .foldregistry import audit_fold_registry
from .ids import DOMAIN, sha256
from .nativecoldfold import audit_native_cold_fold
from .nativefoldspine import audit_native_fold_spine
from .surfaceledger import audit_surface_ledger, entries_for_revision

NATIVE_HANDOFF_FOLD_DOMAIN = DOMAIN + b":native-handoff-fold-v1:"


@dataclass(frozen=True)
class NativeHandoffFoldFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class NativeHandoffFoldReport:
    revision: str
    artifact_stem: str
    status: str
    predecessor_status: str
    foldmap_status: str
    foldregistry_status: str
    surface_ledger_status: str
    native_spine_status: str
    findings: tuple[NativeHandoffFoldFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")


def _exists(root: Path, rel: str, needle: str, findings: list[NativeHandoffFoldFinding]) -> None:
    path = root / rel
    if not path.exists():
        findings.append(NativeHandoffFoldFinding("error", "missing_path", rel, "rev0090 expected this path"))
        return
    if needle not in path.read_text(encoding="utf-8", errors="replace"):
        findings.append(NativeHandoffFoldFinding("error", "missing_needle", rel, f"missing needle {needle!r}"))


def audit_native_handoff_fold(root: str | Path, *, revision: str = "rev0090", artifact_stem: str = "") -> NativeHandoffFoldReport:
    root_path = Path(root)
    artifact = artifact_stem or root_path.name
    findings: list[NativeHandoffFoldFinding] = []
    checks = {
        "src/i2p_dht_lab/nativehandoff.py": "NativeHandoffDecisionKind",
        "src/i2p_dht_lab/relaunchgate.py": "NativeRelaunchGateDecisionKind",
        "src/i2p_dht_lab/loaderseal.py": "NativeLoaderSealDecisionKind",
        "src/i2p_dht_lab/nativefoldspine.py": "audit_native_fold_spine",
        "src/i2p_dht_lab/nativehandofffold.py": "audit_native_handoff_fold",
        "tests/test_rev0090_nativehandoff_relaunchgate_loaderseal.py": "test_native_handoff_accepts_candidate_but_forbids_load_and_dispatch",
        "docs/938-rev0090-nativehandoff-relaunchgate-loaderseal.md": "rev0090",
        "docs/939-native-handoff-relaunch-candidate.md": "Native handoff",
        "docs/940-relaunch-gate-prior-lanes.md": "Relaunch gate",
        "docs/941-loader-seal-restart-memory.md": "Loader seal",
        "docs/942-native-fold-spine-audit-refactor.md": "nativefoldspine",
        "README.md": "nativehandofffold",
        "START_HERE.md": "nativehandofffold",
        "PUBLIC_SURFACE.json": "nativehandoff",
        "HEAD_REGISTRY.json": "rev0090",
    }
    for rel, needle in checks.items():
        _exists(root_path, rel, needle, findings)
    predecessor = audit_native_cold_fold(root_path, revision="rev0089", artifact_stem=artifact)
    fold_map = audit_fold_map(root_path, revision=revision, artifact_stem=artifact)
    fold_registry = audit_fold_registry(root_path, revision=revision)
    surface = audit_surface_ledger(root_path, entries_for_revision(revision))
    spine = audit_native_fold_spine(root_path, revision=revision)
    if predecessor.status != "pass":
        findings.append(NativeHandoffFoldFinding("error", "predecessor_failed", "rev0089", predecessor.status))
    if fold_map.status != "pass":
        findings.append(NativeHandoffFoldFinding("error", "foldmap_failed", "foldmap", fold_map.status))
    if fold_registry.status != "pass":
        findings.append(NativeHandoffFoldFinding("error", "foldregistry_failed", "foldregistry", fold_registry.status))
    if not surface.ok:
        findings.append(NativeHandoffFoldFinding("error", "surface_ledger_failed", "surfaceledger", str(surface.error_count)))
    if spine.status != "pass":
        findings.append(NativeHandoffFoldFinding("error", "native_spine_failed", "nativefoldspine", spine.status))
    status = "pass" if not any(f.severity == "error" for f in findings) else "fail"
    digest = sha256(NATIVE_HANDOFF_FOLD_DOMAIN + bencode({
        b"revision": revision,
        b"artifact": artifact,
        b"status": status,
        b"predecessor": predecessor.status,
        b"foldmap": fold_map.status,
        b"registry": fold_registry.status,
        b"surface": 1 if surface.ok else 0,
        b"spine": spine.status,
        b"findings": [finding.bvalue() for finding in findings],
    }))
    return NativeHandoffFoldReport(revision, artifact, status, predecessor.status, fold_map.status, fold_registry.status, "pass" if surface.ok else "fail", spine.status, tuple(findings), digest)
