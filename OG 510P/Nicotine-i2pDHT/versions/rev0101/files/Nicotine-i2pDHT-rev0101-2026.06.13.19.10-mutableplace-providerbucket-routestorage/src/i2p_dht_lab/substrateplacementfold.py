"""rev0101 substrate-placement fold audit."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .foldmap import audit_fold_map
from .foldregistry import audit_fold_registry
from .ids import DOMAIN, sha256
from .substratecenturyfold import audit_substrate_century_fold
from .substratespine import audit_substrate_spine
from .surfaceledger import audit_surface_ledger, entries_for_revision

SUBSTRATE_PLACEMENT_FOLD_DOMAIN = DOMAIN + b":substrate-placement-fold-v1:"


@dataclass(frozen=True)
class SubstratePlacementFoldFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class SubstratePlacementFoldReport:
    revision: str
    artifact_stem: str
    status: str
    predecessor_status: str
    fold_map_status: str
    fold_registry_status: str
    surface_ledger_status: str
    substrate_spine_status: str
    findings: tuple[SubstratePlacementFoldFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")


def audit_substrate_placement_fold(root: str | Path, *, revision: str = "rev0101") -> SubstratePlacementFoldReport:
    root_path = Path(root)
    artifact = root_path.name
    findings: list[SubstratePlacementFoldFinding] = []
    predecessor = audit_substrate_century_fold(root_path, revision="rev0100")
    fold_map = audit_fold_map(root_path, revision=revision, artifact_stem=artifact)
    fold_registry = audit_fold_registry(root_path, revision=revision)
    ledger = audit_surface_ledger(root_path, entries_for_revision(revision))
    substrate_spine = audit_substrate_spine(root_path, revision=revision)
    required = (
        "src/i2p_dht_lab/mutableplacement.py",
        "src/i2p_dht_lab/providerbucket.py",
        "src/i2p_dht_lab/routestorage.py",
        "src/i2p_dht_lab/substratespine.py",
        "src/i2p_dht_lab/substrateplacementfold.py",
        "tests/test_rev0101_mutableplace_providerbucket_routestorage.py",
        "docs/1048-rev0101-mutableplace-providerbucket-routestorage.md",
    )
    for rel in required:
        if not (root_path / rel).exists():
            findings.append(SubstratePlacementFoldFinding("error", "missing_rev0101_path", rel, "rev0101 substrate-placement path missing"))
    for label, status in (("predecessor", predecessor.status), ("fold_map", fold_map.status), ("fold_registry", fold_registry.status), ("substrate_spine", substrate_spine.status)):
        if status != "pass":
            findings.append(SubstratePlacementFoldFinding("error", f"{label}_failed", label, f"{label} audit did not pass"))
    if not ledger.ok:
        findings.append(SubstratePlacementFoldFinding("error", "surface_ledger_failed", "surfaceledger", "rev0101 surface ledger failed"))
    readme = (root_path / "README.md").read_text(encoding="utf-8", errors="replace") if (root_path / "README.md").exists() else ""
    start = (root_path / "START_HERE.md").read_text(encoding="utf-8", errors="replace") if (root_path / "START_HERE.md").exists() else ""
    for needle in ("mutableplacement", "providerbucket", "routestorage", "substrateplacementfold", "substratecenturyfold", "substratespine"):
        if needle not in readme or needle not in start:
            findings.append(SubstratePlacementFoldFinding("error", "missing_wake_anchor", needle, "README.md and START_HERE.md must retain rev0101 wake anchors"))
    status = "pass" if not any(f.severity == "error" for f in findings) else "fail"
    digest = sha256(SUBSTRATE_PLACEMENT_FOLD_DOMAIN + bencode({
        b"revision": revision,
        b"artifact": artifact,
        b"status": status,
        b"predecessor": predecessor.status,
        b"fold_map": fold_map.status,
        b"fold_registry": fold_registry.status,
        b"surface_ledger": 1 if ledger.ok else 0,
        b"substrate_spine": substrate_spine.status,
        b"findings": [finding.bvalue() for finding in findings],
    }))
    return SubstratePlacementFoldReport(revision, artifact, status, predecessor.status, fold_map.status, fold_registry.status, "pass" if ledger.ok else "fail", substrate_spine.status, tuple(findings), digest)
