"""rev0043 compartment fold audit.

The audit/refactor lane for rev0043 pins key-compartment and authority-split
surfaces as the current path while preserving rev0042 controlplanefold as
predecessor history.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .controlplanefold import audit_controlplane_fold
from .foldmap import audit_fold_map
from .foldregistry import audit_fold_registry
from .ids import DOMAIN, sha256
from .surfaceledger import audit_surface_ledger, entries_for_revision

COMPARTMENT_FOLD_DOMAIN = DOMAIN + b":compartment-fold-v1:"


@dataclass(frozen=True)
class CompartmentFoldFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class CompartmentFoldReport:
    revision: str
    artifact_stem: str
    status: str
    predecessor_status: str
    foldmap_status: str
    registry_status: str
    surface_ledger_status: str
    findings: tuple[CompartmentFoldFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for item in self.findings if item.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for item in self.findings if item.severity == "warning")


REV0043_PATHS = (
    "src/i2p_dht_lab/keycompartment.py",
    "src/i2p_dht_lab/authoritysplit.py",
    "src/i2p_dht_lab/compartmentfold.py",
    "tests/test_rev0043_keycompartment_authoritysplit.py",
    "docs/445-rev0043-keycompartment-authoritysplit-fold.md",
    "docs/446-key-compartment-boundaries.md",
    "docs/447-authority-split-joined-gate.md",
    "docs/448-compartmentfold-audit-refactor.md",
)
NEEDLES = ("rev0043", "keycompartment", "authoritysplit", "compartmentfold")


def _contains(path: Path, needle: str) -> bool:
    try:
        return needle in path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return False


def audit_compartment_fold(root: str | Path, *, revision: str = "rev0043", artifact_stem: str | None = None) -> CompartmentFoldReport:
    if revision != "rev0043":
        raise ValueError("compartmentfold currently audits rev0043")
    root_path = Path(root)
    artifact_stem = artifact_stem or root_path.name
    findings: list[CompartmentFoldFinding] = []
    for rel in REV0043_PATHS:
        if not (root_path / rel).exists():
            findings.append(CompartmentFoldFinding("error", "missing_rev0043_path", rel, "rev0043 compartment path is absent"))
    for surface_path in ("PUBLIC_SURFACE.json", "HEAD_REGISTRY.json", "docs/00-index.md"):
        for needle in NEEDLES:
            if not _contains(root_path / surface_path, needle):
                findings.append(CompartmentFoldFinding("error", "surface_missing_needle", surface_path, f"missing {needle}"))
    try:
        predecessor = audit_controlplane_fold(root_path, revision="rev0042", artifact_stem=artifact_stem)
        predecessor_status = predecessor.status
        if predecessor.error_count:
            findings.append(CompartmentFoldFinding("error", "controlplanefold_failed", "src/i2p_dht_lab/controlplanefold.py", "rev0042 predecessor failed"))
    except Exception as exc:  # pragma: no cover
        predecessor_status = "exception"
        findings.append(CompartmentFoldFinding("error", "controlplanefold_exception", "src/i2p_dht_lab/controlplanefold.py", str(exc)))
    try:
        foldmap = audit_fold_map(root_path, revision="rev0043", artifact_stem=artifact_stem)
        foldmap_status = foldmap.status
        if foldmap.error_count:
            findings.append(CompartmentFoldFinding("error", "foldmap_failed", "src/i2p_dht_lab/foldmap.py", "rev0043 foldmap failed"))
    except Exception as exc:  # pragma: no cover
        foldmap_status = "exception"
        findings.append(CompartmentFoldFinding("error", "foldmap_exception", "src/i2p_dht_lab/foldmap.py", str(exc)))
    try:
        registry = audit_fold_registry(root_path, revision="rev0043")
        registry_status = registry.status
        if registry.error_count:
            findings.append(CompartmentFoldFinding("error", "foldregistry_failed", "src/i2p_dht_lab/foldregistry.py", "rev0043 registry failed"))
    except Exception as exc:  # pragma: no cover
        registry_status = "exception"
        findings.append(CompartmentFoldFinding("error", "foldregistry_exception", "src/i2p_dht_lab/foldregistry.py", str(exc)))
    try:
        ledger = audit_surface_ledger(root_path, entries_for_revision(revision))
        surface_status = "pass" if ledger.ok else "fail"
        if ledger.error_count:
            findings.append(CompartmentFoldFinding("error", "surface_ledger_failed", "src/i2p_dht_lab/surfaceledger.py", "rev0043 surface ledger failed"))
    except Exception as exc:  # pragma: no cover
        surface_status = "exception"
        findings.append(CompartmentFoldFinding("error", "surface_ledger_exception", "src/i2p_dht_lab/surfaceledger.py", str(exc)))
    status = "pass" if not any(f.severity == "error" for f in findings) else "fail"
    digest = sha256(COMPARTMENT_FOLD_DOMAIN + b":report:" + bencode({
        b"revision": revision,
        b"artifact": artifact_stem,
        b"status": status,
        b"predecessor": predecessor_status,
        b"foldmap": foldmap_status,
        b"registry": registry_status,
        b"surface": surface_status,
        b"findings": [f.bvalue() for f in findings],
    }))
    return CompartmentFoldReport(revision, artifact_stem, status, predecessor_status, foldmap_status, registry_status, surface_status, tuple(findings), digest)
