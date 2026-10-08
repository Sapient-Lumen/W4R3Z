"""rev0047 policy portfolio / redress privacy / bridge chaos fold audit."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .foldmap import audit_fold_map
from .foldregistry import audit_fold_registry
from .ids import DOMAIN, sha256
from .moderationfold import audit_moderation_fold
from .surfaceledger import audit_surface_ledger, entries_for_revision

POLICY_PORTFOLIO_FOLD_DOMAIN = DOMAIN + b":policy-portfolio-fold-v1:"


@dataclass(frozen=True)
class PolicyPortfolioFoldFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class PolicyPortfolioFoldReport:
    revision: str
    artifact_stem: str
    status: str
    predecessor_status: str
    foldmap_status: str
    registry_status: str
    surface_ledger_status: str
    findings: tuple[PolicyPortfolioFoldFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")


REV0047_PATHS = (
    "src/i2p_dht_lab/policyportfolio.py",
    "src/i2p_dht_lab/redressprivacy.py",
    "src/i2p_dht_lab/bridgechaos.py",
    "src/i2p_dht_lab/policyportfoliofold.py",
    "tests/test_rev0047_policyportfolio_redressprivacy_bridgechaos.py",
    "docs/490-rev0047-policyportfolio-redressprivacy-bridgechaos.md",
    "docs/491-policy-source-portfolio-capture.md",
    "docs/492-redress-privacy-minimization.md",
    "docs/493-bridge-chaos-restart-pressure.md",
    "docs/494-policyportfoliofold-audit-refactor.md",
)
NEEDLES = ("rev0047", "policyportfolio", "redressprivacy", "bridgechaos", "policyportfoliofold")


def _contains(path: Path, needle: str) -> bool:
    try:
        return needle in path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return False


def audit_policy_portfolio_fold(root: str | Path, *, revision: str = "rev0047", artifact_stem: str | None = None) -> PolicyPortfolioFoldReport:
    if revision != "rev0047":
        raise ValueError("policyportfoliofold currently audits rev0047")
    root_path = Path(root)
    artifact_stem = artifact_stem or root_path.name
    findings: list[PolicyPortfolioFoldFinding] = []
    for rel in REV0047_PATHS:
        if not (root_path / rel).exists():
            findings.append(PolicyPortfolioFoldFinding("error", "missing_rev0047_path", rel, "rev0047 policy portfolio path is absent"))
    for surface_path in ("PUBLIC_SURFACE.json", "HEAD_REGISTRY.json", "docs/00-index.md"):
        for needle in NEEDLES:
            if not _contains(root_path / surface_path, needle):
                findings.append(PolicyPortfolioFoldFinding("error", "surface_missing_needle", surface_path, f"missing {needle}"))
    try:
        predecessor = audit_moderation_fold(root_path, revision="rev0046", artifact_stem=artifact_stem)
        predecessor_status = predecessor.status
        if predecessor.error_count:
            findings.append(PolicyPortfolioFoldFinding("error", "moderationfold_failed", "src/i2p_dht_lab/moderationfold.py", "rev0046 predecessor fold failed"))
    except Exception as exc:  # pragma: no cover
        predecessor_status = "exception"
        findings.append(PolicyPortfolioFoldFinding("error", "moderationfold_exception", "src/i2p_dht_lab/moderationfold.py", str(exc)))
    try:
        foldmap = audit_fold_map(root_path, revision="rev0047", artifact_stem=artifact_stem)
        foldmap_status = foldmap.status
        if foldmap.error_count:
            findings.append(PolicyPortfolioFoldFinding("error", "foldmap_failed", "src/i2p_dht_lab/foldmap.py", "rev0047 foldmap failed"))
    except Exception as exc:  # pragma: no cover
        foldmap_status = "exception"
        findings.append(PolicyPortfolioFoldFinding("error", "foldmap_exception", "src/i2p_dht_lab/foldmap.py", str(exc)))
    try:
        registry = audit_fold_registry(root_path, revision="rev0047")
        registry_status = registry.status
        if registry.error_count:
            findings.append(PolicyPortfolioFoldFinding("error", "foldregistry_failed", "src/i2p_dht_lab/foldregistry.py", "rev0047 fold registry failed"))
    except Exception as exc:  # pragma: no cover
        registry_status = "exception"
        findings.append(PolicyPortfolioFoldFinding("error", "foldregistry_exception", "src/i2p_dht_lab/foldregistry.py", str(exc)))
    try:
        ledger = audit_surface_ledger(root_path, entries_for_revision("rev0047"))
        surface_status = "pass" if ledger.ok else "fail"
        if ledger.error_count:
            findings.append(PolicyPortfolioFoldFinding("error", "surface_ledger_failed", "src/i2p_dht_lab/surfaceledger.py", "rev0047 surface ledger failed"))
    except Exception as exc:  # pragma: no cover
        surface_status = "exception"
        findings.append(PolicyPortfolioFoldFinding("error", "surface_ledger_exception", "src/i2p_dht_lab/surfaceledger.py", str(exc)))
    status = "pass" if not any(finding.severity == "error" for finding in findings) else "fail"
    digest = sha256(POLICY_PORTFOLIO_FOLD_DOMAIN + b":report:" + bencode({
        b"revision": revision,
        b"artifact": artifact_stem,
        b"status": status,
        b"predecessor": predecessor_status,
        b"foldmap": foldmap_status,
        b"registry": registry_status,
        b"surface": surface_status,
        b"findings": [finding.bvalue() for finding in findings],
    }))
    return PolicyPortfolioFoldReport(revision, artifact_stem, status, predecessor_status, foldmap_status, registry_status, surface_status, tuple(findings), digest)
