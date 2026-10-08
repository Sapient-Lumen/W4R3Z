"""rev0095 native shadow-settlement fold audit."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .foldmap import audit_fold_map
from .foldregistry import audit_fold_registry
from .ids import DOMAIN, sha256
from .nativefoldspine import audit_native_fold_spine
from .nativeshadowfold import audit_native_shadow_fold
from .surfaceledger import audit_surface_ledger, entries_for_revision

NATIVE_SETTLEMENT_FOLD_DOMAIN = DOMAIN + b":native-settlement-fold-v1:"


@dataclass(frozen=True)
class NativeSettlementFoldFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class NativeSettlementFoldReport:
    revision: str
    artifact: str
    status: str
    predecessor_status: str
    fold_map_status: str
    fold_registry_status: str
    surface_ledger_status: str
    native_spine_status: str
    findings: tuple[NativeSettlementFoldFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")


def audit_native_settlement_fold(root: str | Path, *, revision: str = "rev0095") -> NativeSettlementFoldReport:
    root_path = Path(root)
    artifact = root_path.name
    findings: list[NativeSettlementFoldFinding] = []
    required = (
        "src/i2p_dht_lab/nativeshadowsettlement.py",
        "src/i2p_dht_lab/nativeadmission.py",
        "src/i2p_dht_lab/nativecallledger.py",
        "src/i2p_dht_lab/nativefoldspine.py",
        "src/i2p_dht_lab/nativesettlementfold.py",
        "tests/test_rev0095_shadowsettlement_admission_callledger.py",
        "docs/988-rev0095-shadowsettlement-admission-callledger.md",
        "docs/989-native-shadow-settlement.md",
        "docs/990-native-admission-held.md",
        "docs/991-native-call-ledger.md",
        "docs/992-nativesettlementfold-audit-refactor.md",
    )
    for rel in required:
        if not (root_path / rel).exists():
            findings.append(NativeSettlementFoldFinding("error", "missing_rev0095_surface", rel, "rev0095 surface is absent"))
    docs_index = (root_path / "docs" / "00-index.md").read_text(encoding="utf-8", errors="replace") if (root_path / "docs" / "00-index.md").exists() else ""
    for needle in ("rev0095", "nativeshadowsettlement", "nativeadmission", "nativecallledger", "nativesettlementfold"):
        if needle not in docs_index:
            findings.append(NativeSettlementFoldFinding("error", "missing_rev0095_index_anchor", "docs/00-index.md", f"missing {needle}"))
    readme = (root_path / "README.md").read_text(encoding="utf-8", errors="replace") if (root_path / "README.md").exists() else ""
    start_here = (root_path / "START_HERE.md").read_text(encoding="utf-8", errors="replace") if (root_path / "START_HERE.md").exists() else ""
    for needle in ("nativeshadowfold", "nativesettlementfold"):
        if needle not in readme or needle not in start_here:
            findings.append(NativeSettlementFoldFinding("error", "missing_native_settlement_anchor", needle, "README.md and START_HERE.md must retain predecessor/current anchors"))
    predecessor = audit_native_shadow_fold(root_path, revision="rev0094")
    fold_map = audit_fold_map(root_path, revision=revision)
    fold_registry = audit_fold_registry(root_path, revision=revision)
    surface = audit_surface_ledger(root_path, entries_for_revision(revision))
    native_spine = audit_native_fold_spine(root_path, revision=revision)
    if predecessor.status != "pass":
        findings.append(NativeSettlementFoldFinding("error", "predecessor_fold_failed", "nativeshadowfold", predecessor.status))
    if fold_map.status != "pass":
        findings.append(NativeSettlementFoldFinding("error", "fold_map_failed", "foldmap", fold_map.status))
    if fold_registry.status != "pass":
        findings.append(NativeSettlementFoldFinding("error", "fold_registry_failed", "foldregistry", fold_registry.status))
    if not surface.ok:
        findings.append(NativeSettlementFoldFinding("error", "surface_ledger_failed", "surfaceledger", "active ledger missing current revision"))
    if native_spine.status != "pass":
        findings.append(NativeSettlementFoldFinding("error", "native_spine_failed", "nativefoldspine", native_spine.status))
    status = "pass" if not any(f.severity == "error" for f in findings) else "fail"
    digest = sha256(NATIVE_SETTLEMENT_FOLD_DOMAIN + bencode({
        b"revision": revision,
        b"artifact": artifact,
        b"status": status,
        b"predecessor": predecessor.status,
        b"foldmap": fold_map.status,
        b"foldregistry": fold_registry.status,
        b"surface": 1 if surface.ok else 0,
        b"native_spine": native_spine.status,
        b"findings": [finding.bvalue() for finding in findings],
    }))
    return NativeSettlementFoldReport(revision, artifact, status, predecessor.status, fold_map.status, fold_registry.status, "pass" if surface.ok else "fail", native_spine.status, tuple(findings), digest)
