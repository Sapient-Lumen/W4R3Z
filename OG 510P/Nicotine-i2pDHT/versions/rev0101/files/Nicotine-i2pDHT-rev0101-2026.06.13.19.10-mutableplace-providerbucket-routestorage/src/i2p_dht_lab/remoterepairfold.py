"""rev0065 audit/refactor fold for remote witness repair pressure."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .foldmap import audit_fold_map
from .foldregistry import audit_fold_registry
from .ids import DOMAIN, sha256
from .remotewitnessledger import REMOTE_WITNESS_LEDGER_DOMAIN
from .retrypublishfold import audit_retry_publish_fold
from .surfaceledger import audit_surface_ledger, entries_for_revision

REMOTE_REPAIR_FOLD_DOMAIN = DOMAIN + b":remote-repair-fold-v1:"


@dataclass(frozen=True)
class RemoteRepairFoldFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class RemoteRepairFoldReport:
    revision: str
    artifact_stem: str
    status: str
    predecessor_status: str
    foldmap_status: str
    foldregistry_status: str
    surface_ledger_status: str
    findings: tuple[RemoteRepairFoldFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")


def _exists(root: Path, rel: str, needle: str, findings: list[RemoteRepairFoldFinding]) -> None:
    path = root / rel
    if not path.exists():
        findings.append(RemoteRepairFoldFinding("error", "missing_path", rel, "rev0065 remoterepairfold expected this path"))
        return
    text = path.read_text(encoding="utf-8", errors="replace")
    if needle not in text:
        findings.append(RemoteRepairFoldFinding("error", "missing_needle", rel, f"missing needle {needle!r}"))


def audit_remote_repair_fold(root: str | Path, *, revision: str = "rev0065", artifact_stem: str = "") -> RemoteRepairFoldReport:
    root_path = Path(root)
    artifact = artifact_stem or root_path.name
    findings: list[RemoteRepairFoldFinding] = []
    checks = {
        "src/i2p_dht_lab/remotewitnessledger.py": "RemoteWitnessLedgerDecisionKind",
        "src/i2p_dht_lab/repairoutbox.py": "RepairOutboxDecisionKind",
        "src/i2p_dht_lab/conflictcooldown.py": "ConflictCooldownDecisionKind",
        "src/i2p_dht_lab/remoterepairfold.py": "audit_remote_repair_fold",
        "tests/test_rev0065_remotewitness_repairoutbox_conflictcooldown.py": "test_remote_conflict_rounds_stage_repair_outbox_and_start_cooldown",
        "docs/688-rev0065-remotewitness-repairoutbox-conflictcooldown.md": "rev0065",
        "docs/689-remote-witness-ledger-rounds.md": "remote witness ledger",
        "docs/690-repair-outbox-after-duplicate-conflict.md": "repair outbox",
        "docs/691-conflict-cooldown-duplicate-pressure.md": "conflict cooldown",
        "docs/692-remoterepairfold-audit-refactor.md": "remoterepairfold",
    }
    for rel, needle in checks.items():
        _exists(root_path, rel, needle, findings)
    try:
        predecessor = audit_retry_publish_fold(root_path, revision="rev0064", artifact_stem="x")
        predecessor_status = predecessor.status
        if predecessor.error_count:
            findings.append(RemoteRepairFoldFinding("error", "predecessor_failed", "src/i2p_dht_lab/retrypublishfold.py", "rev0064 predecessor failed"))
    except Exception as exc:  # pragma: no cover
        predecessor_status = "exception"
        findings.append(RemoteRepairFoldFinding("error", "predecessor_exception", "src/i2p_dht_lab/retrypublishfold.py", str(exc)))
    try:
        fmap = audit_fold_map(root_path, revision=revision, artifact_stem=artifact)
        foldmap_status = fmap.status
        if fmap.error_count:
            findings.append(RemoteRepairFoldFinding("error", "foldmap_failed", "src/i2p_dht_lab/foldmap.py", "rev0065 fold map failed"))
    except Exception as exc:  # pragma: no cover
        foldmap_status = "exception"
        findings.append(RemoteRepairFoldFinding("error", "foldmap_exception", "src/i2p_dht_lab/foldmap.py", str(exc)))
    try:
        registry = audit_fold_registry(root_path, revision=revision)
        foldregistry_status = registry.status
        if registry.error_count:
            findings.append(RemoteRepairFoldFinding("error", "foldregistry_failed", "src/i2p_dht_lab/foldregistry.py", "rev0065 fold registry failed"))
    except Exception as exc:  # pragma: no cover
        foldregistry_status = "exception"
        findings.append(RemoteRepairFoldFinding("error", "foldregistry_exception", "src/i2p_dht_lab/foldregistry.py", str(exc)))
    try:
        ledger = audit_surface_ledger(root_path, entries_for_revision(revision))
        surface_ledger_status = "pass" if ledger.ok else "fail"
        if ledger.error_count:
            findings.append(RemoteRepairFoldFinding("error", "surface_ledger_failed", "src/i2p_dht_lab/surfaceledger.py", "rev0065 surface ledger failed"))
    except Exception as exc:  # pragma: no cover
        surface_ledger_status = "exception"
        findings.append(RemoteRepairFoldFinding("error", "surface_ledger_exception", "src/i2p_dht_lab/surfaceledger.py", str(exc)))
    status = "pass" if not any(f.severity == "error" for f in findings) else "fail"
    digest = sha256(REMOTE_REPAIR_FOLD_DOMAIN + b":report:" + bencode({
        b"revision": revision,
        b"artifact": artifact,
        b"status": status,
        b"predecessor": predecessor_status,
        b"foldmap": foldmap_status,
        b"foldregistry": foldregistry_status,
        b"surface": surface_ledger_status,
        b"findings": [finding.bvalue() for finding in findings],
        b"remote_domain": REMOTE_WITNESS_LEDGER_DOMAIN,
    }))
    return RemoteRepairFoldReport(revision, artifact, status, predecessor_status, foldmap_status, foldregistry_status, surface_ledger_status, tuple(findings), digest)
