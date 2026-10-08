"""rev0044 fold bridge audit.

The canonical rev0043 line introduced key compartments and authority split. A
parallel rev0043 branchlet introduced control intent and bridge firewall. This
fold audit keeps both histories visible and pins the rev0044 bridge that joins
them.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .foldmap import audit_fold_map
from .foldregistry import audit_fold_registry
from .ids import DOMAIN, sha256
from .surfaceledger import audit_surface_ledger, entries_for_revision

FOLD_BRIDGE_DOMAIN = DOMAIN + b":fold-bridge-v1:"

CURRENT_PATHS = (
    "src/i2p_dht_lab/compartmentfirewall.py",
    "src/i2p_dht_lab/controlreceipt.py",
    "src/i2p_dht_lab/foldbridge.py",
    "src/i2p_dht_lab/controlintent.py",
    "src/i2p_dht_lab/bridgefirewall.py",
    "tests/test_rev0044_compartmentfirewall_controlreceipt_foldbridge.py",
    "docs/455-rev0044-compartmentfirewall-controlreceipt-foldbridge.md",
    "docs/456-compartment-firewall-joined-boundary.md",
    "docs/457-control-receipt-restart-memory.md",
    "docs/458-foldbridge-audit-refactor.md",
)
BRANCHLET_PATHS = (
    "artifacts/branchlets/rev0043_controlintent_bridgefirewall/controlintent.py",
    "artifacts/branchlets/rev0043_controlintent_bridgefirewall/bridgefirewall.py",
    "artifacts/branchlets/rev0043_controlintent_bridgefirewall/test_rev0043_controlintent_bridgefirewall_foldtrim.py",
    "artifacts/branchlets/rev0043_controlintent_bridgefirewall/docs/445-rev0043-controlintent-bridgefirewall-foldtrim.md",
)
PREDECESSOR_PATHS = (
    "src/i2p_dht_lab/keycompartment.py",
    "src/i2p_dht_lab/authoritysplit.py",
    "src/i2p_dht_lab/compartmentfold.py",
    "tests/test_rev0043_keycompartment_authoritysplit.py",
    "docs/445-rev0043-keycompartment-authoritysplit-fold.md",
)
NEEDLES = ("rev0044", "compartmentfirewall", "controlreceipt", "foldbridge", "controlintent", "bridgefirewall")


@dataclass(frozen=True)
class FoldBridgeFinding:
    severity: str
    code: str
    path: str
    detail: str


@dataclass(frozen=True)
class FoldBridgeReport:
    revision: str
    status: str
    predecessor_status: str
    branchlet_status: str
    foldmap_status: str
    registry_status: str
    ledger_status: str
    findings: tuple[FoldBridgeFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")


def audit_fold_bridge(root: str | Path, *, revision: str = "rev0044") -> FoldBridgeReport:
    if revision != "rev0044":
        raise ValueError("foldbridge currently audits rev0044")
    root_path = Path(root)
    findings: list[FoldBridgeFinding] = []
    for rel in CURRENT_PATHS:
        if not (root_path / rel).exists():
            findings.append(FoldBridgeFinding("error", "missing_current_path", rel, "rev0044 path missing"))
    for rel in BRANCHLET_PATHS:
        if not (root_path / rel).exists():
            findings.append(FoldBridgeFinding("error", "missing_branchlet_path", rel, "folded rev0043 branchlet path missing"))
    for rel in PREDECESSOR_PATHS:
        if not (root_path / rel).exists():
            findings.append(FoldBridgeFinding("error", "missing_predecessor_path", rel, "canonical rev0043 predecessor path missing"))
    public_text = (root_path / "PUBLIC_SURFACE.json").read_text(encoding="utf-8") if (root_path / "PUBLIC_SURFACE.json").exists() else ""
    head_text = (root_path / "HEAD_REGISTRY.json").read_text(encoding="utf-8") if (root_path / "HEAD_REGISTRY.json").exists() else ""
    index_text = (root_path / "docs/00-index.md").read_text(encoding="utf-8") if (root_path / "docs/00-index.md").exists() else ""
    for needle in NEEDLES:
        if needle not in public_text:
            findings.append(FoldBridgeFinding("error", "public_surface_missing_needle", "PUBLIC_SURFACE.json", f"missing {needle}"))
        if needle not in head_text:
            findings.append(FoldBridgeFinding("error", "head_registry_missing_needle", "HEAD_REGISTRY.json", f"missing {needle}"))
        if needle not in index_text:
            findings.append(FoldBridgeFinding("error", "index_missing_needle", "docs/00-index.md", f"missing {needle}"))
    predecessor_report = audit_fold_map(root_path, revision="rev0043")
    foldmap_report = audit_fold_map(root_path, revision="rev0044")
    registry_report = audit_fold_registry(root_path, revision="rev0044")
    ledger_report = audit_surface_ledger(root_path, entries_for_revision("rev0044"))
    if predecessor_report.status != "pass":
        findings.append(FoldBridgeFinding("error", "predecessor_foldmap_failed", "src/i2p_dht_lab/foldmap.py", "rev0043 foldmap did not pass"))
    if foldmap_report.status != "pass":
        findings.append(FoldBridgeFinding("error", "current_foldmap_failed", "src/i2p_dht_lab/foldmap.py", "rev0044 foldmap did not pass"))
    if registry_report.status != "pass":
        findings.append(FoldBridgeFinding("error", "registry_failed", "src/i2p_dht_lab/foldregistry.py", "rev0044 fold registry did not pass"))
    if ledger_report.error_count:
        findings.append(FoldBridgeFinding("error", "ledger_failed", "src/i2p_dht_lab/surfaceledger.py", "rev0044 surface ledger did not pass"))
    branchlet_status = "pass" if not any(f.code == "missing_branchlet_path" for f in findings) else "fail"
    status = "pass" if not any(f.severity == "error" for f in findings) else "fail"
    digest = sha256(FOLD_BRIDGE_DOMAIN + b":report:" + bencode({
        b"revision": revision,
        b"status": status,
        b"predecessor_status": predecessor_report.status,
        b"branchlet_status": branchlet_status,
        b"foldmap_status": foldmap_report.status,
        b"registry_status": registry_report.status,
        b"ledger_status": "pass" if not ledger_report.error_count else "fail",
        b"findings": [{b"severity": f.severity, b"code": f.code, b"path": f.path, b"detail": f.detail} for f in findings],
    }))
    return FoldBridgeReport(revision, status, predecessor_report.status, branchlet_status, foldmap_report.status, registry_report.status, "pass" if not ledger_report.error_count else "fail", tuple(findings), digest)
