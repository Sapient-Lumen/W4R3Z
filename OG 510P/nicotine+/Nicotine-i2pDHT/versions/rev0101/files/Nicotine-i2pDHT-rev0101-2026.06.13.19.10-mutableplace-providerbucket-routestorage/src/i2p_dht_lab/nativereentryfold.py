"""rev0091 fold audit for native preflight / oracle seal / re-entry journal."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .foldmap import audit_fold_map
from .foldregistry import audit_fold_registry
from .ids import DOMAIN, sha256
from .nativefoldspine import audit_native_fold_spine
from .nativehandofffold import audit_native_handoff_fold
from .surfaceledger import audit_surface_ledger, entries_for_revision

NATIVE_REENTRY_FOLD_DOMAIN = DOMAIN + b":native-reentry-fold-v1:"


@dataclass(frozen=True)
class NativeReentryFoldFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class NativeReentryFoldReport:
    revision: str
    artifact_stem: str
    status: str
    predecessor_status: str
    foldmap_status: str
    foldregistry_status: str
    surface_ledger_status: str
    native_spine_status: str
    findings: tuple[NativeReentryFoldFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")


def _exists(root: Path, rel: str, needle: str, findings: list[NativeReentryFoldFinding]) -> None:
    path = root / rel
    if not path.exists():
        findings.append(NativeReentryFoldFinding("error", "missing_path", rel, "rev0091 expected this path"))
        return
    if needle not in path.read_text(encoding="utf-8", errors="replace"):
        findings.append(NativeReentryFoldFinding("error", "missing_needle", rel, f"missing needle {needle!r}"))


def audit_native_reentry_fold(root: str | Path, *, revision: str = "rev0091", artifact_stem: str = "") -> NativeReentryFoldReport:
    root_path = Path(root)
    artifact = artifact_stem or root_path.name
    findings: list[NativeReentryFoldFinding] = []
    checks = {
        "src/i2p_dht_lab/nativeoracleseal.py": "NativeOracleSealDecisionKind",
        "src/i2p_dht_lab/nativepreflight.py": "NativePreflightDecisionKind",
        "src/i2p_dht_lab/nativereentryjournal.py": "NativeReentryJournalDecisionKind",
        "src/i2p_dht_lab/nativefoldspine.py": "rev0091",
        "src/i2p_dht_lab/nativereentryfold.py": "audit_native_reentry_fold",
        "tests/test_rev0091_nativereentry_oracleseal_preflight.py": "test_native_preflight_routes_to_load_gate_only",
        "docs/948-rev0091-nativereentry-oracleseal-preflight.md": "rev0091",
        "docs/949-native-oracle-seal.md": "Python oracle seal",
        "docs/950-native-preflight-route-to-load-gate.md": "Native preflight",
        "docs/951-native-reentry-journal.md": "Native re-entry journal",
        "docs/952-nativereentryfold-audit-refactor.md": "nativereentryfold",
        "README.md": "nativereentryfold",
        "START_HERE.md": "nativereentryfold",
        "PUBLIC_SURFACE.json": "nativepreflight",
        "HEAD_REGISTRY.json": "rev0091",
    }
    for rel, needle in checks.items():
        _exists(root_path, rel, needle, findings)
    predecessor = audit_native_handoff_fold(root_path, revision="rev0090", artifact_stem=artifact)
    fold_map = audit_fold_map(root_path, revision=revision, artifact_stem=artifact)
    fold_registry = audit_fold_registry(root_path, revision=revision)
    surface = audit_surface_ledger(root_path, entries_for_revision(revision))
    native_spine = audit_native_fold_spine(root_path, revision=revision)
    if predecessor.status != "pass":
        findings.append(NativeReentryFoldFinding("error", "predecessor_failed", "rev0090", predecessor.status))
    if fold_map.status != "pass":
        findings.append(NativeReentryFoldFinding("error", "foldmap_failed", "foldmap", fold_map.status))
    if fold_registry.status != "pass":
        findings.append(NativeReentryFoldFinding("error", "foldregistry_failed", "foldregistry", fold_registry.status))
    if not surface.ok:
        findings.append(NativeReentryFoldFinding("error", "surface_ledger_failed", "surfaceledger", str(surface.error_count)))
    if native_spine.status != "pass":
        findings.append(NativeReentryFoldFinding("error", "native_spine_failed", "nativefoldspine", native_spine.status))
    status = "pass" if not any(f.severity == "error" for f in findings) else "fail"
    digest = sha256(NATIVE_REENTRY_FOLD_DOMAIN + bencode({
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
    return NativeReentryFoldReport(revision, artifact, status, predecessor.status, fold_map.status, fold_registry.status, "pass" if surface.ok else "fail", native_spine.status, tuple(findings), digest)
