"""rev0047 policy-portfolio / publication-guard fold audit."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .foldmap import audit_fold_map
from .foldregistry import audit_fold_registry
from .ids import DOMAIN, sha256
from .moderationfold import audit_moderation_fold
from .surfaceledger import audit_surface_ledger, entries_for_revision

PUBLICATION_FOLD_DOMAIN = DOMAIN + b":publication-fold-v1:"


@dataclass(frozen=True)
class PublicationFoldFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class PublicationFoldReport:
    revision: str
    artifact_stem: str
    status: str
    predecessor_status: str
    foldmap_status: str
    registry_status: str
    surface_ledger_status: str
    branchlet_status: str
    findings: tuple[PublicationFoldFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")


REV0047_PATHS = (
    "src/i2p_dht_lab/policyportfolio.py",
    "src/i2p_dht_lab/publicationguard.py",
    "src/i2p_dht_lab/publicationfold.py",
    "tests/test_rev0047_policyportfolio_publicationguard.py",
    "docs/500-rev0047-policyportfolio-publicationguard-branchfold.md",
    "docs/501-policy-portfolio-source-capture.md",
    "docs/502-publication-guard-final-side-effect.md",
    "docs/503-branchlet-fold-rev0046-publication-chaos.md",
    "docs/504-publicationfold-audit-refactor.md",
)
BRANCHLET_PATHS = (
    "artifacts/branchlets/rev0046_publication_chaos/README.md",
    "artifacts/branchlets/rev0046_publication_chaos/bridgeegress.py",
    "artifacts/branchlets/rev0046_publication_chaos/witnessappeal.py",
    "artifacts/branchlets/rev0046_publication_chaos/bridgechaos.py",
    "artifacts/branchlets/rev0046_publication_chaos/bridgepublish.py",
    "artifacts/branchlets/rev0046_publication_chaos/bridgequench.py",
    "artifacts/branchlets/rev0046_publication_chaos/validatorroot.py",
)
NEEDLES = ("rev0047", "policyportfolio", "publicationguard", "publicationfold")


def _contains(path: Path, needle: str) -> bool:
    try:
        return needle in path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return False


def audit_publication_fold(root: str | Path, *, revision: str = "rev0047", artifact_stem: str | None = None) -> PublicationFoldReport:
    if revision != "rev0047":
        raise ValueError("publicationfold currently audits rev0047")
    root_path = Path(root)
    artifact_stem = artifact_stem or root_path.name
    findings: list[PublicationFoldFinding] = []
    for rel in REV0047_PATHS:
        if not (root_path / rel).exists():
            findings.append(PublicationFoldFinding("error", "missing_rev0047_path", rel, "rev0047 policy/publication path is absent"))
    branchlet_missing = False
    for rel in BRANCHLET_PATHS:
        if not (root_path / rel).exists():
            branchlet_missing = True
            findings.append(PublicationFoldFinding("error", "missing_folded_branchlet", rel, "folded rev0046 publication/chaos branchlet artifact is absent"))
    branchlet_status = "pass" if not branchlet_missing else "fail"
    for surface_path in ("PUBLIC_SURFACE.json", "HEAD_REGISTRY.json", "docs/00-index.md"):
        for needle in NEEDLES:
            if not _contains(root_path / surface_path, needle):
                findings.append(PublicationFoldFinding("error", "surface_missing_needle", surface_path, f"missing {needle}"))
    try:
        predecessor = audit_moderation_fold(root_path, revision="rev0046", artifact_stem=artifact_stem)
        predecessor_status = predecessor.status
        if predecessor.error_count:
            findings.append(PublicationFoldFinding("error", "moderationfold_failed", "src/i2p_dht_lab/moderationfold.py", "rev0046 predecessor fold failed"))
    except Exception as exc:  # pragma: no cover
        predecessor_status = "exception"
        findings.append(PublicationFoldFinding("error", "moderationfold_exception", "src/i2p_dht_lab/moderationfold.py", str(exc)))
    try:
        foldmap = audit_fold_map(root_path, revision="rev0047", artifact_stem=artifact_stem)
        foldmap_status = foldmap.status
        if foldmap.error_count:
            findings.append(PublicationFoldFinding("error", "foldmap_failed", "src/i2p_dht_lab/foldmap.py", "rev0047 foldmap failed"))
    except Exception as exc:  # pragma: no cover
        foldmap_status = "exception"
        findings.append(PublicationFoldFinding("error", "foldmap_exception", "src/i2p_dht_lab/foldmap.py", str(exc)))
    try:
        registry = audit_fold_registry(root_path, revision="rev0047")
        registry_status = registry.status
        if registry.error_count:
            findings.append(PublicationFoldFinding("error", "foldregistry_failed", "src/i2p_dht_lab/foldregistry.py", "rev0047 registry failed"))
    except Exception as exc:  # pragma: no cover
        registry_status = "exception"
        findings.append(PublicationFoldFinding("error", "foldregistry_exception", "src/i2p_dht_lab/foldregistry.py", str(exc)))
    try:
        ledger = audit_surface_ledger(root_path, entries_for_revision("rev0047"))
        surface_status = "pass" if ledger.ok else "fail"
        if ledger.error_count:
            findings.append(PublicationFoldFinding("error", "surface_ledger_failed", "src/i2p_dht_lab/surfaceledger.py", "rev0047 surface ledger failed"))
    except Exception as exc:  # pragma: no cover
        surface_status = "exception"
        findings.append(PublicationFoldFinding("error", "surface_ledger_exception", "src/i2p_dht_lab/surfaceledger.py", str(exc)))
    status = "pass" if not any(finding.severity == "error" for finding in findings) else "fail"
    digest = sha256(PUBLICATION_FOLD_DOMAIN + b":report:" + bencode({
        b"revision": revision,
        b"artifact": artifact_stem,
        b"status": status,
        b"predecessor": predecessor_status,
        b"foldmap": foldmap_status,
        b"registry": registry_status,
        b"surface": surface_status,
        b"branchlets": branchlet_status,
        b"findings": [finding.bvalue() for finding in findings],
    }))
    return PublicationFoldReport(revision, artifact_stem, status, predecessor_status, foldmap_status, registry_status, surface_status, branchlet_status, tuple(findings), digest)
