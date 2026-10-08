"""rev0082 audit/refactor fold for native parity, ABI guard, and fallback seal."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .foldmap import audit_fold_map
from .foldregistry import audit_fold_registry
from .ids import DOMAIN, sha256
from .nativeboundaryfold import audit_native_boundary_fold
from .surfaceledger import audit_surface_ledger, entries_for_revision

NATIVE_PARITY_FOLD_DOMAIN = DOMAIN + b":native-parity-fold-v1:"


@dataclass(frozen=True)
class NativeParityFoldFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class NativeParityFoldReport:
    revision: str
    artifact_stem: str
    status: str
    predecessor_status: str
    foldmap_status: str
    foldregistry_status: str
    surface_ledger_status: str
    findings: tuple[NativeParityFoldFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")


def _exists(root: Path, rel: str, needle: str, findings: list[NativeParityFoldFinding]) -> None:
    path = root / rel
    if not path.exists():
        findings.append(NativeParityFoldFinding("error", "missing_path", rel, "rev0082 expected this path"))
        return
    if needle not in path.read_text(encoding="utf-8", errors="replace"):
        findings.append(NativeParityFoldFinding("error", "missing_needle", rel, f"missing needle {needle!r}"))


def audit_native_parity_fold(root: str | Path, *, revision: str = "rev0082", artifact_stem: str = "") -> NativeParityFoldReport:
    root_path = Path(root)
    artifact = artifact_stem or root_path.name
    findings: list[NativeParityFoldFinding] = []
    checks = {
        "src/i2p_dht_lab/nativeparity.py": "NativeParityDecisionKind",
        "src/i2p_dht_lab/abiguard.py": "AbiGuardDecisionKind",
        "src/i2p_dht_lab/fallbackseal.py": "FallbackSealDecisionKind",
        "src/i2p_dht_lab/nativeparityfold.py": "audit_native_parity_fold",
        "tests/test_rev0082_nativeparity_abiguard_fallbackseal.py": "test_native_parity_accepts_real_compiled_leaf",
        "docs/858-rev0082-nativeparity-abiguard-fallbackseal.md": "rev0082",
        "docs/859-native-parity-before-selection.md": "Native parity",
        "docs/860-abi-guard-load-boundary.md": "ABI guard",
        "docs/861-fallback-seal-native-quarantine.md": "fallback seal",
        "docs/862-nativeparityfold-audit-refactor.md": "nativeparityfold",
    }
    for rel, needle in checks.items():
        _exists(root_path, rel, needle, findings)

    try:
        predecessor = audit_native_boundary_fold(root_path, revision="rev0081", artifact_stem=artifact)
        predecessor_status = predecessor.status
        if predecessor.error_count:
            findings.append(NativeParityFoldFinding("error", "predecessor_failed", "src/i2p_dht_lab/nativeboundaryfold.py", "rev0081 predecessor failed"))
    except Exception as exc:  # pragma: no cover
        predecessor_status = "exception"
        findings.append(NativeParityFoldFinding("error", "predecessor_exception", "src/i2p_dht_lab/nativeboundaryfold.py", str(exc)))

    try:
        fmap = audit_fold_map(root_path, revision=revision, artifact_stem=artifact)
        foldmap_status = fmap.status
        if fmap.error_count:
            findings.append(NativeParityFoldFinding("error", "foldmap_failed", "src/i2p_dht_lab/foldmap.py", "rev0082 fold map failed"))
    except Exception as exc:  # pragma: no cover
        foldmap_status = "exception"
        findings.append(NativeParityFoldFinding("error", "foldmap_exception", "src/i2p_dht_lab/foldmap.py", str(exc)))

    try:
        registry = audit_fold_registry(root_path, revision=revision)
        foldregistry_status = registry.status
        if registry.error_count:
            findings.append(NativeParityFoldFinding("error", "foldregistry_failed", "src/i2p_dht_lab/foldregistry.py", "rev0082 fold registry failed"))
    except Exception as exc:  # pragma: no cover
        foldregistry_status = "exception"
        findings.append(NativeParityFoldFinding("error", "foldregistry_exception", "src/i2p_dht_lab/foldregistry.py", str(exc)))

    try:
        ledger = audit_surface_ledger(root_path, entries_for_revision(revision))
        surface_ledger_status = "pass" if ledger.ok else "fail"
        if ledger.error_count:
            findings.append(NativeParityFoldFinding("error", "surface_ledger_failed", "src/i2p_dht_lab/surfaceledger.py", "rev0082 surface ledger failed"))
    except Exception as exc:  # pragma: no cover
        surface_ledger_status = "exception"
        findings.append(NativeParityFoldFinding("error", "surface_ledger_exception", "src/i2p_dht_lab/surfaceledger.py", str(exc)))

    status = "pass" if not any(f.severity == "error" for f in findings) else "fail"
    report_digest = sha256(NATIVE_PARITY_FOLD_DOMAIN + b":report:" + bencode({
        b"revision": revision,
        b"artifact": artifact,
        b"status": status,
        b"predecessor": predecessor_status,
        b"foldmap": foldmap_status,
        b"registry": foldregistry_status,
        b"surface": surface_ledger_status,
        b"findings": [finding.bvalue() for finding in findings],
    }))
    return NativeParityFoldReport(revision, artifact, status, predecessor_status, foldmap_status, foldregistry_status, surface_ledger_status, tuple(findings), report_digest)
