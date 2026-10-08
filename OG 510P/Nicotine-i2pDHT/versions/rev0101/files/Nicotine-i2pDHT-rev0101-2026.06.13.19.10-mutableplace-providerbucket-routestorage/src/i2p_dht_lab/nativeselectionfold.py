"""rev0086 fold audit for native selection / fallback journal / promotion hold."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .foldmap import audit_fold_map
from .foldregistry import audit_fold_registry
from .ids import DOMAIN, sha256
from .nativeprovenancefold import audit_native_provenance_fold
from .surfaceledger import audit_surface_ledger, entries_for_revision

NATIVE_SELECTION_FOLD_DOMAIN = DOMAIN + b":native-selection-fold-v1:"


@dataclass(frozen=True)
class NativeSelectionFoldFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class NativeSelectionFoldReport:
    revision: str
    artifact_stem: str
    status: str
    predecessor_status: str
    foldmap_status: str
    foldregistry_status: str
    surface_ledger_status: str
    findings: tuple[NativeSelectionFoldFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")


def _exists(root: Path, rel: str, needle: str, findings: list[NativeSelectionFoldFinding]) -> None:
    path = root / rel
    if not path.exists():
        findings.append(NativeSelectionFoldFinding("error", "missing_path", rel, "rev0086 expected this path"))
        return
    if needle not in path.read_text(encoding="utf-8", errors="replace"):
        findings.append(NativeSelectionFoldFinding("error", "missing_needle", rel, f"missing needle {needle!r}"))


def audit_native_selection_fold(root: str | Path, *, revision: str = "rev0086", artifact_stem: str = "") -> NativeSelectionFoldReport:
    root_path = Path(root)
    artifact = artifact_stem or root_path.name
    findings: list[NativeSelectionFoldFinding] = []
    checks = {
        "src/i2p_dht_lab/nativeselection.py": "NativeSelectionDecisionKind",
        "src/i2p_dht_lab/fallbackjournal.py": "FallbackJournalDecisionKind",
        "src/i2p_dht_lab/nativepromotion.py": "NativePromotionDecisionKind",
        "src/i2p_dht_lab/nativeselectionfold.py": "audit_native_selection_fold",
        "tests/test_rev0086_nativeselection_fallbackjournal_promotehold.py": "test_native_selection_accepts_only_after_reports_bind",
        "docs/898-rev0086-nativeselection-fallbackjournal-promotehold.md": "rev0086",
        "docs/899-native-selection-exact-boundary.md": "Native selection",
        "docs/900-fallback-journal-restart-memory.md": "Fallback journal",
        "docs/901-native-promotion-hold.md": "Native promotion",
        "docs/902-nativeselectionfold-audit-refactor.md": "nativeselectionfold",
        "README.md": "nativeselectionfold",
        "START_HERE.md": "nativeselectionfold",
        "PUBLIC_SURFACE.json": "nativeselection",
        "HEAD_REGISTRY.json": "rev0086",
    }
    for rel, needle in checks.items():
        _exists(root_path, rel, needle, findings)
    predecessor = audit_native_provenance_fold(root_path, revision="rev0085", artifact_stem=artifact)
    fold_map = audit_fold_map(root_path, revision=revision, artifact_stem=artifact)
    fold_registry = audit_fold_registry(root_path, revision=revision)
    surface = audit_surface_ledger(root_path, entries_for_revision(revision))
    if predecessor.status != "pass":
        findings.append(NativeSelectionFoldFinding("error", "predecessor_failed", "rev0085", predecessor.status))
    if fold_map.status != "pass":
        findings.append(NativeSelectionFoldFinding("error", "foldmap_failed", "foldmap", fold_map.status))
    if fold_registry.status != "pass":
        findings.append(NativeSelectionFoldFinding("error", "foldregistry_failed", "foldregistry", fold_registry.status))
    if not surface.ok:
        findings.append(NativeSelectionFoldFinding("error", "surface_ledger_failed", "surfaceledger", str(surface.error_count)))
    status = "pass" if not any(f.severity == "error" for f in findings) else "fail"
    digest = sha256(NATIVE_SELECTION_FOLD_DOMAIN + bencode({
        b"revision": revision,
        b"artifact": artifact,
        b"status": status,
        b"predecessor": predecessor.status,
        b"foldmap": fold_map.status,
        b"registry": fold_registry.status,
        b"surface": 1 if surface.ok else 0,
        b"findings": [finding.bvalue() for finding in findings],
    }))
    return NativeSelectionFoldReport(revision, artifact, status, predecessor.status, fold_map.status, fold_registry.status, "pass" if surface.ok else "fail", tuple(findings), digest)
