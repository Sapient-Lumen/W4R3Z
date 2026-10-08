"""rev0042 control-plane fold audit.

rev0042 reduces some one-off fold drift by making the current control-plane path
small and explicit: multi-service shared-router pressure, profile cooldowns,
operator key succession, bridge announcement repair, and this audit surface.  It
also preserves rev0041 controlfold as predecessor history.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .controlfold import audit_control_fold
from .foldmap import audit_fold_map
from .foldregistry import audit_fold_registry
from .ids import DOMAIN, sha256
from .surfaceledger import audit_surface_ledger, entries_for_revision

CONTROLPLANE_FOLD_DOMAIN = DOMAIN + b":controlplane-fold-v1:"


@dataclass(frozen=True)
class ControlPlaneFoldFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class ControlPlaneFoldReport:
    revision: str
    artifact_stem: str
    status: str
    predecessor_status: str
    foldmap_status: str
    registry_status: str
    surface_ledger_status: str
    findings: tuple[ControlPlaneFoldFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for item in self.findings if item.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for item in self.findings if item.severity == "warning")


REV0042_PATHS = (
    "src/i2p_dht_lab/multiservice.py",
    "src/i2p_dht_lab/profilecooldown.py",
    "src/i2p_dht_lab/operatorkey.py",
    "src/i2p_dht_lab/announcementrepair.py",
    "src/i2p_dht_lab/controlplanefold.py",
    "tests/test_rev0042_multiservice_cooldown_keyoperator.py",
    "docs/434-rev0042-multiservice-cooldown-keyoperator.md",
    "docs/435-multi-service-router-session-pressure.md",
    "docs/436-profile-cooldown-emergency-freeze.md",
    "docs/437-operator-key-rotation-recovery.md",
    "docs/438-announcement-repair-after-bridge-disable.md",
    "docs/439-controlplanefold-audit-refactor.md",
)
NEEDLES = ("rev0042", "multiservice", "profilecooldown", "operatorkey", "announcementrepair", "controlplanefold")


def _contains(path: Path, needle: str) -> bool:
    try:
        return needle in path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return False


def audit_controlplane_fold(root: str | Path, *, revision: str = "rev0042", artifact_stem: str | None = None) -> ControlPlaneFoldReport:
    if revision != "rev0042":
        raise ValueError("controlplanefold currently audits rev0042")
    root_path = Path(root)
    artifact_stem = artifact_stem or root_path.name
    findings: list[ControlPlaneFoldFinding] = []
    for rel in REV0042_PATHS:
        if not (root_path / rel).exists():
            findings.append(ControlPlaneFoldFinding("error", "missing_rev0042_path", rel, "rev0042 control-plane path is absent"))
    for surface_path in ("PUBLIC_SURFACE.json", "HEAD_REGISTRY.json", "docs/00-index.md"):
        for needle in NEEDLES:
            if not _contains(root_path / surface_path, needle):
                findings.append(ControlPlaneFoldFinding("error", "surface_missing_needle", surface_path, f"missing {needle}"))
    try:
        predecessor = audit_control_fold(root_path, revision="rev0041", artifact_stem=artifact_stem)
        predecessor_status = predecessor.status
        if predecessor.error_count:
            findings.append(ControlPlaneFoldFinding("error", "controlfold_failed", "src/i2p_dht_lab/controlfold.py", "rev0041 predecessor failed"))
    except Exception as exc:  # pragma: no cover
        predecessor_status = "exception"
        findings.append(ControlPlaneFoldFinding("error", "controlfold_exception", "src/i2p_dht_lab/controlfold.py", str(exc)))
    try:
        foldmap = audit_fold_map(root_path, revision="rev0042", artifact_stem=artifact_stem)
        foldmap_status = foldmap.status
        if foldmap.error_count:
            findings.append(ControlPlaneFoldFinding("error", "foldmap_failed", "src/i2p_dht_lab/foldmap.py", "rev0042 foldmap failed"))
    except Exception as exc:  # pragma: no cover
        foldmap_status = "exception"
        findings.append(ControlPlaneFoldFinding("error", "foldmap_exception", "src/i2p_dht_lab/foldmap.py", str(exc)))
    try:
        registry = audit_fold_registry(root_path, revision="rev0042")
        registry_status = registry.status
        if registry.error_count:
            findings.append(ControlPlaneFoldFinding("error", "foldregistry_failed", "src/i2p_dht_lab/foldregistry.py", "rev0042 registry failed"))
    except Exception as exc:  # pragma: no cover
        registry_status = "exception"
        findings.append(ControlPlaneFoldFinding("error", "foldregistry_exception", "src/i2p_dht_lab/foldregistry.py", str(exc)))
    try:
        ledger = audit_surface_ledger(root_path, entries_for_revision(revision))
        surface_status = "pass" if ledger.ok else "fail"
        if ledger.error_count:
            findings.append(ControlPlaneFoldFinding("error", "surface_ledger_failed", "src/i2p_dht_lab/surfaceledger.py", "rev0042 surface ledger failed"))
    except Exception as exc:  # pragma: no cover
        surface_status = "exception"
        findings.append(ControlPlaneFoldFinding("error", "surface_ledger_exception", "src/i2p_dht_lab/surfaceledger.py", str(exc)))
    status = "pass" if not any(f.severity == "error" for f in findings) else "fail"
    digest = sha256(CONTROLPLANE_FOLD_DOMAIN + b":report:" + bencode({
        b"revision": revision,
        b"artifact": artifact_stem,
        b"status": status,
        b"predecessor": predecessor_status,
        b"foldmap": foldmap_status,
        b"registry": registry_status,
        b"surface": surface_status,
        b"findings": [f.bvalue() for f in findings],
    }))
    return ControlPlaneFoldReport(revision, artifact_stem, status, predecessor_status, foldmap_status, registry_status, surface_status, tuple(findings), digest)
