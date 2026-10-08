"""rev0098 native branch-close fold audit."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .foldmap import audit_fold_map
from .foldregistry import audit_fold_registry
from .ids import DOMAIN, sha256
from .nativearchivereplayfold import audit_native_archive_replay_fold
from .nativefoldspine import audit_native_fold_spine
from .surfaceledger import audit_surface_ledger, entries_for_revision

NATIVE_BRANCH_CLOSE_FOLD_DOMAIN = DOMAIN + b":native-branch-close-fold-v1:"


@dataclass(frozen=True)
class NativeBranchCloseFoldFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class NativeBranchCloseFoldReport:
    revision: str
    artifact_stem: str
    status: str
    predecessor_status: str
    fold_map_status: str
    fold_registry_status: str
    surface_ledger_status: str
    native_spine_status: str
    findings: tuple[NativeBranchCloseFoldFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")


def audit_native_branch_close_fold(root: str | Path, *, revision: str = "rev0098") -> NativeBranchCloseFoldReport:
    root_path = Path(root)
    artifact = root_path.name
    findings: list[NativeBranchCloseFoldFinding] = []
    predecessor = audit_native_archive_replay_fold(root_path, revision="rev0097")
    fold_map = audit_fold_map(root_path, revision=revision, artifact_stem=artifact)
    fold_registry = audit_fold_registry(root_path, revision=revision)
    ledger = audit_surface_ledger(root_path, entries_for_revision(revision))
    native_spine = audit_native_fold_spine(root_path, revision=revision)
    required = (
        "src/i2p_dht_lab/nativepromotearchive.py",
        "src/i2p_dht_lab/nativepromotionpolicy.py",
        "src/i2p_dht_lab/nativebranchclose.py",
        "src/i2p_dht_lab/nativebranchclosefold.py",
        "tests/test_rev0098_nativebranchclose_promotearchive_policy.py",
        "docs/1018-rev0098-nativebranchclose-promotearchive-policyseal.md",
    )
    for rel in required:
        if not (root_path / rel).exists():
            findings.append(NativeBranchCloseFoldFinding("error", "missing_rev0098_path", rel, "rev0098 native branch-close path missing"))
    for label, status in (("predecessor", predecessor.status), ("fold_map", fold_map.status), ("fold_registry", fold_registry.status), ("native_spine", native_spine.status)):
        if status != "pass":
            findings.append(NativeBranchCloseFoldFinding("error", f"{label}_failed", label, f"{label} audit did not pass"))
    if not ledger.ok:
        findings.append(NativeBranchCloseFoldFinding("error", "surface_ledger_failed", "surfaceledger", "rev0098 surface ledger failed"))
    status = "pass" if not any(f.severity == "error" for f in findings) else "fail"
    digest = sha256(NATIVE_BRANCH_CLOSE_FOLD_DOMAIN + bencode({
        b"revision": revision,
        b"artifact": artifact,
        b"status": status,
        b"predecessor": predecessor.status,
        b"fold_map": fold_map.status,
        b"fold_registry": fold_registry.status,
        b"surface_ledger": 1 if ledger.ok else 0,
        b"native_spine": native_spine.status,
        b"findings": [finding.bvalue() for finding in findings],
    }))
    return NativeBranchCloseFoldReport(revision, artifact, status, predecessor.status, fold_map.status, fold_registry.status, "pass" if ledger.ok else "fail", native_spine.status, tuple(findings), digest)
