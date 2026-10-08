"""rev0047 appeal/publication/quench fold audit."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .foldmap import audit_fold_map
from .foldregistry import audit_fold_registry
from .ids import DOMAIN, sha256
from .moderationfold import audit_moderation_fold
from .surfaceledger import audit_surface_ledger, entries_for_revision

APPEAL_PUBLICATION_FOLD_DOMAIN = DOMAIN + b":appeal-publication-fold-v1:"

REV0047_PATHS = (
    "src/i2p_dht_lab/witnessappealmesh.py",
    "src/i2p_dht_lab/publicationledger.py",
    "src/i2p_dht_lab/bridgequenchlane.py",
    "src/i2p_dht_lab/appealpublicationfold.py",
    "tests/test_rev0047_appeal_publication_quench.py",
    "docs/490-rev0047-appealmesh-publicationquench-branchfold.md",
    "docs/491-witness-appeal-mesh.md",
    "docs/492-publication-ledger-boundary.md",
    "docs/493-bridge-quench-lane.md",
    "docs/494-appealpublicationfold-audit-refactor.md",
)
BRANCHLET_PATHS = (
    "artifacts/branchlets/rev0046_public_bridge_branchlets/README.md",
    "artifacts/branchlets/rev0046_public_bridge_branchlets/witnessappeal.py",
    "artifacts/branchlets/rev0046_public_bridge_branchlets/bridgechaos.py",
    "artifacts/branchlets/rev0046_public_bridge_branchlets/bridgepublish.py",
    "artifacts/branchlets/rev0046_public_bridge_branchlets/bridgequench.py",
    "artifacts/branchlets/rev0046_public_bridge_branchlets/validatorroot.py",
)
NEEDLES = ("rev0047", "witnessappealmesh", "publicationledger", "bridgequenchlane", "appealpublicationfold")


@dataclass(frozen=True)
class AppealPublicationFoldFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class AppealPublicationFoldReport:
    revision: str
    artifact_stem: str
    status: str
    predecessor_status: str
    foldmap_status: str
    registry_status: str
    surface_ledger_status: str
    branchlet_count: int
    findings: tuple[AppealPublicationFoldFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")


def _contains(path: Path, needle: str) -> bool:
    try:
        return needle in path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return False


def audit_appeal_publication_fold(root: str | Path, *, revision: str = "rev0047", artifact_stem: str | None = None) -> AppealPublicationFoldReport:
    if revision != "rev0047":
        raise ValueError("appealpublicationfold currently audits rev0047")
    root_path = Path(root)
    artifact_stem = artifact_stem or root_path.name
    findings: list[AppealPublicationFoldFinding] = []
    for rel in REV0047_PATHS:
        if not (root_path / rel).exists():
            findings.append(AppealPublicationFoldFinding("error", "missing_rev0047_path", rel, "rev0047 appeal/publication/quench path is absent"))
    branchlet_count = 0
    for rel in BRANCHLET_PATHS:
        if (root_path / rel).exists():
            branchlet_count += 1
        else:
            findings.append(AppealPublicationFoldFinding("warning", "missing_folded_branchlet", rel, "alternate rev0046 branchlet evidence is absent"))
    for surface_path in ("PUBLIC_SURFACE.json", "HEAD_REGISTRY.json", "docs/00-index.md"):
        for needle in NEEDLES:
            if not _contains(root_path / surface_path, needle):
                findings.append(AppealPublicationFoldFinding("error", "surface_missing_needle", surface_path, f"missing {needle}"))
    try:
        predecessor = audit_moderation_fold(root_path, revision="rev0046", artifact_stem=artifact_stem)
        predecessor_status = predecessor.status
        if predecessor.error_count:
            findings.append(AppealPublicationFoldFinding("error", "moderationfold_failed", "src/i2p_dht_lab/moderationfold.py", "rev0046 predecessor fold failed"))
    except Exception as exc:  # pragma: no cover
        predecessor_status = "exception"
        findings.append(AppealPublicationFoldFinding("error", "moderationfold_exception", "src/i2p_dht_lab/moderationfold.py", str(exc)))
    try:
        foldmap = audit_fold_map(root_path, revision="rev0047", artifact_stem=artifact_stem)
        foldmap_status = foldmap.status
        if foldmap.error_count:
            findings.append(AppealPublicationFoldFinding("error", "foldmap_failed", "src/i2p_dht_lab/foldmap.py", "rev0047 foldmap failed"))
    except Exception as exc:  # pragma: no cover
        foldmap_status = "exception"
        findings.append(AppealPublicationFoldFinding("error", "foldmap_exception", "src/i2p_dht_lab/foldmap.py", str(exc)))
    try:
        registry = audit_fold_registry(root_path, revision="rev0047")
        registry_status = registry.status
        if registry.error_count:
            findings.append(AppealPublicationFoldFinding("error", "foldregistry_failed", "src/i2p_dht_lab/foldregistry.py", "rev0047 registry failed"))
    except Exception as exc:  # pragma: no cover
        registry_status = "exception"
        findings.append(AppealPublicationFoldFinding("error", "foldregistry_exception", "src/i2p_dht_lab/foldregistry.py", str(exc)))
    try:
        ledger = audit_surface_ledger(root_path, entries_for_revision("rev0047"))
        surface_status = "pass" if ledger.ok else "fail"
        if ledger.error_count:
            findings.append(AppealPublicationFoldFinding("error", "surface_ledger_failed", "src/i2p_dht_lab/surfaceledger.py", "rev0047 surface ledger failed"))
    except Exception as exc:  # pragma: no cover
        surface_status = "exception"
        findings.append(AppealPublicationFoldFinding("error", "surface_ledger_exception", "src/i2p_dht_lab/surfaceledger.py", str(exc)))
    status = "pass" if not any(f.severity == "error" for f in findings) else "fail"
    digest = sha256(APPEAL_PUBLICATION_FOLD_DOMAIN + b":report:" + bencode({
        b"revision": revision,
        b"artifact": artifact_stem,
        b"status": status,
        b"predecessor": predecessor_status,
        b"foldmap": foldmap_status,
        b"registry": registry_status,
        b"surface": surface_status,
        b"branchlets": branchlet_count,
        b"findings": [finding.bvalue() for finding in findings],
    }))
    return AppealPublicationFoldReport(revision, artifact_stem, status, predecessor_status, foldmap_status, registry_status, surface_status, branchlet_count, tuple(findings), digest)
