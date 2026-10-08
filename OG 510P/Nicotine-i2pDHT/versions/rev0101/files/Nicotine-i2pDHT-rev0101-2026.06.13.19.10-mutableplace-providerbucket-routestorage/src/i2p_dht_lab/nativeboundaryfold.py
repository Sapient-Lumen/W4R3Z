"""rev0081 audit/refactor fold for Python/GCC native-boundary decisions."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .foldmap import audit_fold_map
from .foldregistry import audit_fold_registry
from .ids import DOMAIN, sha256
from .importsettlementfold import audit_import_settlement_fold
from .surfaceledger import audit_surface_ledger, entries_for_revision

NATIVE_BOUNDARY_FOLD_DOMAIN = DOMAIN + b":native-boundary-fold-v1:"


@dataclass(frozen=True)
class NativeBoundaryFoldFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class NativeBoundaryFoldReport:
    revision: str
    artifact_stem: str
    status: str
    predecessor_status: str
    foldmap_status: str
    foldregistry_status: str
    surface_ledger_status: str
    findings: tuple[NativeBoundaryFoldFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")


def _exists(root: Path, rel: str, needle: str, findings: list[NativeBoundaryFoldFinding]) -> None:
    path = root / rel
    if not path.exists():
        findings.append(NativeBoundaryFoldFinding("error", "missing_path", rel, "rev0081 expected this path"))
        return
    if needle not in path.read_text(encoding="utf-8", errors="replace"):
        findings.append(NativeBoundaryFoldFinding("error", "missing_needle", rel, f"missing needle {needle!r}"))


def audit_native_boundary_fold(root: str | Path, *, revision: str = "rev0081", artifact_stem: str = "") -> NativeBoundaryFoldReport:
    root_path = Path(root)
    artifact = artifact_stem or root_path.name
    findings: list[NativeBoundaryFoldFinding] = []
    checks = {
        "src/i2p_dht_lab/nativeboundary.py": "NativeBoundaryDecisionKind",
        "src/i2p_dht_lab/gccffi.py": "GccFfiContract",
        "src/i2p_dht_lab/nativehotpaths.py": "xor_compare_reference",
        "src/i2p_dht_lab/nativeboundaryfold.py": "audit_native_boundary_fold",
        "native/gcc/xor_distance.c": "i2pdht_xor_compare",
        "tests/test_rev0081_nativeboundary_gccffi_hotpath.py": "test_gcc_leaf_kernel_matches_python_reference_when_compiled",
        "docs/848-rev0081-nativeboundary-gccffi-hotpath.md": "rev0081",
        "docs/849-python-first-native-leaf-boundary.md": "Python first",
        "docs/850-gcc-ffi-contract.md": "GCC FFI",
        "docs/851-native-hotpath-xor-kernel.md": "XOR",
        "docs/852-nativeboundaryfold-audit-refactor.md": "nativeboundaryfold",
    }
    for rel, needle in checks.items():
        _exists(root_path, rel, needle, findings)

    try:
        predecessor = audit_import_settlement_fold(root_path, revision="rev0080", artifact_stem=artifact)
        predecessor_status = predecessor.status
        if predecessor.error_count:
            findings.append(NativeBoundaryFoldFinding("error", "predecessor_failed", "src/i2p_dht_lab/importsettlementfold.py", "rev0080 predecessor failed"))
    except Exception as exc:  # pragma: no cover
        predecessor_status = "exception"
        findings.append(NativeBoundaryFoldFinding("error", "predecessor_exception", "src/i2p_dht_lab/importsettlementfold.py", str(exc)))

    try:
        fmap = audit_fold_map(root_path, revision=revision, artifact_stem=artifact)
        foldmap_status = fmap.status
        if fmap.error_count:
            findings.append(NativeBoundaryFoldFinding("error", "foldmap_failed", "src/i2p_dht_lab/foldmap.py", "rev0081 fold map failed"))
    except Exception as exc:  # pragma: no cover
        foldmap_status = "exception"
        findings.append(NativeBoundaryFoldFinding("error", "foldmap_exception", "src/i2p_dht_lab/foldmap.py", str(exc)))

    try:
        registry = audit_fold_registry(root_path, revision=revision)
        foldregistry_status = registry.status
        if registry.error_count:
            findings.append(NativeBoundaryFoldFinding("error", "foldregistry_failed", "src/i2p_dht_lab/foldregistry.py", "rev0081 fold registry failed"))
    except Exception as exc:  # pragma: no cover
        foldregistry_status = "exception"
        findings.append(NativeBoundaryFoldFinding("error", "foldregistry_exception", "src/i2p_dht_lab/foldregistry.py", str(exc)))

    try:
        ledger = audit_surface_ledger(root_path, entries_for_revision(revision))
        surface_ledger_status = "pass" if ledger.ok else "fail"
        if ledger.error_count:
            findings.append(NativeBoundaryFoldFinding("error", "surface_ledger_failed", "src/i2p_dht_lab/surfaceledger.py", "rev0081 surface ledger failed"))
    except Exception as exc:  # pragma: no cover
        surface_ledger_status = "exception"
        findings.append(NativeBoundaryFoldFinding("error", "surface_ledger_exception", "src/i2p_dht_lab/surfaceledger.py", str(exc)))

    status = "pass" if not any(f.severity == "error" for f in findings) else "fail"
    report_digest = sha256(NATIVE_BOUNDARY_FOLD_DOMAIN + b":report:" + bencode({
        b"revision": revision,
        b"artifact": artifact,
        b"status": status,
        b"predecessor": predecessor_status,
        b"foldmap": foldmap_status,
        b"registry": foldregistry_status,
        b"surface": surface_ledger_status,
        b"findings": [finding.bvalue() for finding in findings],
    }))
    return NativeBoundaryFoldReport(revision, artifact, status, predecessor_status, foldmap_status, foldregistry_status, surface_ledger_status, tuple(findings), report_digest)
