"""rev0083 audit/refactor fold for runtime drift, dispatch seal, and source audit."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .foldmap import audit_fold_map
from .foldregistry import audit_fold_registry
from .ids import DOMAIN, sha256
from .nativeparityfold import audit_native_parity_fold
from .surfaceledger import audit_surface_ledger, entries_for_revision

NATIVE_DISPATCH_FOLD_DOMAIN = DOMAIN + b":native-dispatch-fold-v1:"


@dataclass(frozen=True)
class NativeDispatchFoldFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class NativeDispatchFoldReport:
    revision: str
    artifact_stem: str
    status: str
    predecessor_status: str
    foldmap_status: str
    foldregistry_status: str
    surface_ledger_status: str
    findings: tuple[NativeDispatchFoldFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")


def _exists(root: Path, rel: str, needle: str, findings: list[NativeDispatchFoldFinding]) -> None:
    path = root / rel
    if not path.exists():
        findings.append(NativeDispatchFoldFinding("error", "missing_path", rel, "rev0083 expected this path"))
        return
    if needle not in path.read_text(encoding="utf-8", errors="replace"):
        findings.append(NativeDispatchFoldFinding("error", "missing_needle", rel, f"missing needle {needle!r}"))


def audit_native_dispatch_fold(root: str | Path, *, revision: str = "rev0083", artifact_stem: str = "") -> NativeDispatchFoldReport:
    root_path = Path(root)
    artifact = artifact_stem or root_path.name
    findings: list[NativeDispatchFoldFinding] = []
    checks = {
        "src/i2p_dht_lab/nativeruntime.py": "NativeRuntimeDecisionKind",
        "src/i2p_dht_lab/nativedispatch.py": "NativeDispatchDecisionKind",
        "src/i2p_dht_lab/nativeaudit.py": "NativeSourceAuditDecisionKind",
        "src/i2p_dht_lab/nativedispatchfold.py": "audit_native_dispatch_fold",
        "tests/test_rev0083_nativeruntime_dispatchaudit_fallbackbudget.py": "test_runtime_accepts_native_only_when_stamp_matches",
        "docs/868-rev0083-nativeruntime-dispatchaudit-fallbackbudget.md": "rev0083",
        "docs/869-native-runtime-drift-guard.md": "runtime drift",
        "docs/870-native-dispatch-seal.md": "dispatch seal",
        "docs/871-native-source-audit.md": "source audit",
        "docs/872-nativedispatchfold-audit-refactor.md": "nativedispatchfold",
    }
    for rel, needle in checks.items():
        _exists(root_path, rel, needle, findings)

    try:
        predecessor = audit_native_parity_fold(root_path, revision="rev0082", artifact_stem=artifact)
        predecessor_status = predecessor.status
        if predecessor.error_count:
            findings.append(NativeDispatchFoldFinding("error", "predecessor_failed", "src/i2p_dht_lab/nativeparityfold.py", "rev0082 predecessor failed"))
    except Exception as exc:  # pragma: no cover
        predecessor_status = "exception"
        findings.append(NativeDispatchFoldFinding("error", "predecessor_exception", "src/i2p_dht_lab/nativeparityfold.py", str(exc)))

    try:
        fmap = audit_fold_map(root_path, revision=revision, artifact_stem=artifact)
        foldmap_status = fmap.status
        if fmap.error_count:
            findings.append(NativeDispatchFoldFinding("error", "foldmap_failed", "src/i2p_dht_lab/foldmap.py", "rev0083 fold map failed"))
    except Exception as exc:  # pragma: no cover
        foldmap_status = "exception"
        findings.append(NativeDispatchFoldFinding("error", "foldmap_exception", "src/i2p_dht_lab/foldmap.py", str(exc)))

    try:
        registry = audit_fold_registry(root_path, revision=revision)
        foldregistry_status = registry.status
        if registry.error_count:
            findings.append(NativeDispatchFoldFinding("error", "foldregistry_failed", "src/i2p_dht_lab/foldregistry.py", "rev0083 fold registry failed"))
    except Exception as exc:  # pragma: no cover
        foldregistry_status = "exception"
        findings.append(NativeDispatchFoldFinding("error", "foldregistry_exception", "src/i2p_dht_lab/foldregistry.py", str(exc)))

    try:
        ledger = audit_surface_ledger(root_path, entries_for_revision(revision))
        surface_ledger_status = "pass" if ledger.ok else "fail"
        if ledger.error_count:
            findings.append(NativeDispatchFoldFinding("error", "surface_ledger_failed", "src/i2p_dht_lab/surfaceledger.py", "rev0083 surface ledger failed"))
    except Exception as exc:  # pragma: no cover
        surface_ledger_status = "exception"
        findings.append(NativeDispatchFoldFinding("error", "surface_ledger_exception", "src/i2p_dht_lab/surfaceledger.py", str(exc)))

    status = "pass" if not any(f.severity == "error" for f in findings) else "fail"
    digest = sha256(NATIVE_DISPATCH_FOLD_DOMAIN + b":report:" + bencode({
        b"revision": revision,
        b"artifact": artifact,
        b"status": status,
        b"predecessor": predecessor_status,
        b"foldmap": foldmap_status,
        b"registry": foldregistry_status,
        b"surface": surface_ledger_status,
        b"findings": [finding.bvalue() for finding in findings],
    }))
    return NativeDispatchFoldReport(revision, artifact, status, predecessor_status, foldmap_status, foldregistry_status, surface_ledger_status, tuple(findings), digest)
