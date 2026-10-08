"""rev0100 substrate-century fold audit."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .foldmap import audit_fold_map
from .foldregistry import audit_fold_registry
from .ids import DOMAIN, sha256
from .substratespine import audit_substrate_spine
from .substratereturnfold import audit_substrate_return_fold
from .surfaceledger import audit_surface_ledger, entries_for_revision

SUBSTRATE_CENTURY_FOLD_DOMAIN = DOMAIN + b":substrate-century-fold-v1:"


@dataclass(frozen=True)
class SubstrateCenturyFoldFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class SubstrateCenturyFoldReport:
    revision: str
    artifact_stem: str
    status: str
    predecessor_status: str
    fold_map_status: str
    fold_registry_status: str
    surface_ledger_status: str
    substrate_spine_status: str
    findings: tuple[SubstrateCenturyFoldFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")


def audit_substrate_century_fold(root: str | Path, *, revision: str = "rev0100") -> SubstrateCenturyFoldReport:
    root_path = Path(root)
    artifact = root_path.name
    findings: list[SubstrateCenturyFoldFinding] = []
    predecessor = audit_substrate_return_fold(root_path, revision="rev0099")
    fold_map = audit_fold_map(root_path, revision=revision, artifact_stem=artifact)
    fold_registry = audit_fold_registry(root_path, revision=revision)
    ledger = audit_surface_ledger(root_path, entries_for_revision(revision))
    substrate_spine = audit_substrate_spine(root_path, revision=revision)
    required = (
        "src/i2p_dht_lab/recordingress.py",
        "src/i2p_dht_lab/providersemantics.py",
        "src/i2p_dht_lab/routinganchor.py",
        "src/i2p_dht_lab/substratespine.py",
        "src/i2p_dht_lab/substratecenturyfold.py",
        "tests/test_rev0100_recordingress_providersemantics_routingspine.py",
        "docs/1038-rev0100-recordingress-providersemantics-routingspine.md",
    )
    for rel in required:
        if not (root_path / rel).exists():
            findings.append(SubstrateCenturyFoldFinding("error", "missing_rev0100_path", rel, "rev0100 substrate-century path missing"))
    for label, status in (("predecessor", predecessor.status), ("fold_map", fold_map.status), ("fold_registry", fold_registry.status), ("substrate_spine", substrate_spine.status)):
        if status != "pass":
            findings.append(SubstrateCenturyFoldFinding("error", f"{label}_failed", label, f"{label} audit did not pass"))
    if not ledger.ok:
        findings.append(SubstrateCenturyFoldFinding("error", "surface_ledger_failed", "surfaceledger", "rev0100 surface ledger failed"))
    readme = (root_path / "README.md").read_text(encoding="utf-8", errors="replace") if (root_path / "README.md").exists() else ""
    start = (root_path / "START_HERE.md").read_text(encoding="utf-8", errors="replace") if (root_path / "START_HERE.md").exists() else ""
    for needle in ("recordingress", "providersemantics", "routinganchor", "substratespine", "substratecenturyfold", "substratereturnfold"):
        if needle not in readme or needle not in start:
            findings.append(SubstrateCenturyFoldFinding("error", "missing_wake_anchor", needle, "README.md and START_HERE.md must retain rev0100 wake anchors"))
    status = "pass" if not any(f.severity == "error" for f in findings) else "fail"
    digest = sha256(SUBSTRATE_CENTURY_FOLD_DOMAIN + bencode({
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
    return SubstrateCenturyFoldReport(revision, artifact, status, predecessor.status, fold_map.status, fold_registry.status, "pass" if ledger.ok else "fail", substrate_spine.status, tuple(findings), digest)
