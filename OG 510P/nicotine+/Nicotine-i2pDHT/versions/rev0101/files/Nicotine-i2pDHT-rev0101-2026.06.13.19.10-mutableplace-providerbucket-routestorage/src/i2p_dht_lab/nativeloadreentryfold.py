"""rev0092 fold audit for native load re-entry / revalidation / call hold."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .foldmap import audit_fold_map
from .foldregistry import audit_fold_registry
from .ids import DOMAIN, sha256
from .nativefoldspine import audit_native_fold_spine
from .nativereentryfold import audit_native_reentry_fold
from .surfaceledger import audit_surface_ledger, entries_for_revision

NATIVE_LOAD_REENTRY_FOLD_DOMAIN = DOMAIN + b":native-load-reentry-fold-v1:"


@dataclass(frozen=True)
class NativeLoadReentryFoldFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class NativeLoadReentryFoldReport:
    revision: str
    artifact_stem: str
    status: str
    predecessor_status: str
    foldmap_status: str
    foldregistry_status: str
    surface_ledger_status: str
    native_spine_status: str
    findings: tuple[NativeLoadReentryFoldFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")


def _exists(root: Path, rel: str, needle: str, findings: list[NativeLoadReentryFoldFinding]) -> None:
    path = root / rel
    if not path.exists():
        findings.append(NativeLoadReentryFoldFinding("error", "missing_path", rel, "rev0092 expected this path"))
        return
    if needle not in path.read_text(encoding="utf-8", errors="replace"):
        findings.append(NativeLoadReentryFoldFinding("error", "missing_needle", rel, f"missing needle {needle!r}"))


def audit_native_load_reentry_fold(root: str | Path, *, revision: str = "rev0092", artifact_stem: str = "") -> NativeLoadReentryFoldReport:
    root_path = Path(root)
    artifact = artifact_stem or root_path.name
    findings: list[NativeLoadReentryFoldFinding] = []
    checks = {
        "src/i2p_dht_lab/nativeloadreentry.py": "NativeLoadReentryDecisionKind",
        "src/i2p_dht_lab/revalidationseal.py": "RevalidationSealDecisionKind",
        "src/i2p_dht_lab/nativecallhold.py": "NativeCallHoldDecisionKind",
        "src/i2p_dht_lab/nativefoldspine.py": "rev0092",
        "src/i2p_dht_lab/nativeloadreentryfold.py": "audit_native_load_reentry_fold",
        "tests/test_rev0092_nativeloadreentry_revalidationseal_callhold.py": "test_load_reentry_prepares_request_but_does_not_load",
        "docs/958-rev0092-nativeloadreentry-revalidationseal-callhold.md": "rev0092",
        "docs/959-native-load-reentry-request.md": "Native load re-entry",
        "docs/960-revalidation-seal-prior-lanes.md": "Revalidation seal",
        "docs/961-native-call-hold.md": "Native call hold",
        "docs/962-nativeloadreentryfold-audit-refactor.md": "nativeloadreentryfold",
        "README.md": "nativeloadreentryfold",
        "START_HERE.md": "nativeloadreentryfold",
        "PUBLIC_SURFACE.json": "nativeloadreentry",
        "HEAD_REGISTRY.json": "rev0092",
    }
    for rel, needle in checks.items():
        _exists(root_path, rel, needle, findings)
    predecessor = audit_native_reentry_fold(root_path, revision="rev0091", artifact_stem=artifact)
    fold_map = audit_fold_map(root_path, revision=revision, artifact_stem=artifact)
    fold_registry = audit_fold_registry(root_path, revision=revision)
    surface = audit_surface_ledger(root_path, entries_for_revision(revision))
    native_spine = audit_native_fold_spine(root_path, revision=revision)
    if predecessor.status != "pass":
        findings.append(NativeLoadReentryFoldFinding("error", "predecessor_failed", "rev0091", predecessor.status))
    if fold_map.status != "pass":
        findings.append(NativeLoadReentryFoldFinding("error", "foldmap_failed", "foldmap", fold_map.status))
    if fold_registry.status != "pass":
        findings.append(NativeLoadReentryFoldFinding("error", "foldregistry_failed", "foldregistry", fold_registry.status))
    if not surface.ok:
        findings.append(NativeLoadReentryFoldFinding("error", "surface_ledger_failed", "surfaceledger", str(surface.error_count)))
    if native_spine.status != "pass":
        findings.append(NativeLoadReentryFoldFinding("error", "native_spine_failed", "nativefoldspine", native_spine.status))
    status = "pass" if not any(f.severity == "error" for f in findings) else "fail"
    digest = sha256(NATIVE_LOAD_REENTRY_FOLD_DOMAIN + bencode({
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
    return NativeLoadReentryFoldReport(revision, artifact, status, predecessor.status, fold_map.status, fold_registry.status, "pass" if surface.ok else "fail", native_spine.status, tuple(findings), digest)
