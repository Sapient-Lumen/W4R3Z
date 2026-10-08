"""rev0069 audit/refactor fold for closure seal / retention proof / audit export."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .archivejournalfold import audit_archive_journal_fold
from .bencode import bencode
from .foldmap import audit_fold_map
from .foldregistry import audit_fold_registry
from .ids import DOMAIN, sha256
from .surfaceledger import audit_surface_ledger, entries_for_revision

CLOSURE_SEAL_FOLD_DOMAIN = DOMAIN + b":closure-seal-fold-v1:"


@dataclass(frozen=True)
class ClosureSealFoldFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class ClosureSealFoldReport:
    revision: str
    artifact_stem: str
    status: str
    predecessor_status: str
    foldmap_status: str
    foldregistry_status: str
    surface_ledger_status: str
    findings: tuple[ClosureSealFoldFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")


def _exists(root: Path, rel: str, needle: str, findings: list[ClosureSealFoldFinding]) -> None:
    path = root / rel
    if not path.exists():
        findings.append(ClosureSealFoldFinding("error", "missing_path", rel, "rev0069 closuresealfold expected this path"))
        return
    text = path.read_text(encoding="utf-8", errors="replace")
    if needle not in text:
        findings.append(ClosureSealFoldFinding("error", "missing_needle", rel, f"missing needle {needle!r}"))


def audit_closure_seal_fold(root: str | Path, *, revision: str = "rev0069", artifact_stem: str = "") -> ClosureSealFoldReport:
    root_path = Path(root)
    artifact = artifact_stem or root_path.name
    findings: list[ClosureSealFoldFinding] = []
    checks = {
        "src/i2p_dht_lab/closureseal.py": "ClosureSealDecisionKind",
        "src/i2p_dht_lab/retentionproof.py": "RetentionProofDecisionKind",
        "src/i2p_dht_lab/auditexport.py": "AuditExportDecisionKind",
        "src/i2p_dht_lab/closuresealfold.py": "audit_closure_seal_fold",
        "tests/test_rev0069_closureseal_retention_export.py": "test_closure_seal_retention_and_export_happy_path",
        "docs/728-rev0069-closureseal-retentionproof-exportaudit.md": "rev0069",
        "docs/729-closure-seal-after-audit.md": "closure seal",
        "docs/730-retention-proof-hard-negative-carry.md": "retention proof",
        "docs/731-audit-export-redacted-boundary.md": "audit export",
        "docs/732-closuresealfold-audit-refactor.md": "closuresealfold",
    }
    for rel, needle in checks.items():
        _exists(root_path, rel, needle, findings)
    try:
        predecessor = audit_archive_journal_fold(root_path, revision="rev0068", artifact_stem="x")
        predecessor_status = predecessor.status
        if predecessor.error_count:
            findings.append(ClosureSealFoldFinding("error", "predecessor_failed", "src/i2p_dht_lab/archivejournalfold.py", "rev0068 predecessor failed"))
    except Exception as exc:  # pragma: no cover
        predecessor_status = "exception"
        findings.append(ClosureSealFoldFinding("error", "predecessor_exception", "src/i2p_dht_lab/archivejournalfold.py", str(exc)))
    try:
        fmap = audit_fold_map(root_path, revision=revision, artifact_stem=artifact)
        foldmap_status = fmap.status
        if fmap.error_count:
            findings.append(ClosureSealFoldFinding("error", "foldmap_failed", "src/i2p_dht_lab/foldmap.py", "rev0069 fold map failed"))
    except Exception as exc:  # pragma: no cover
        foldmap_status = "exception"
        findings.append(ClosureSealFoldFinding("error", "foldmap_exception", "src/i2p_dht_lab/foldmap.py", str(exc)))
    try:
        registry = audit_fold_registry(root_path, revision=revision)
        foldregistry_status = registry.status
        if registry.error_count:
            findings.append(ClosureSealFoldFinding("error", "foldregistry_failed", "src/i2p_dht_lab/foldregistry.py", "rev0069 fold registry failed"))
    except Exception as exc:  # pragma: no cover
        foldregistry_status = "exception"
        findings.append(ClosureSealFoldFinding("error", "foldregistry_exception", "src/i2p_dht_lab/foldregistry.py", str(exc)))
    try:
        ledger = audit_surface_ledger(root_path, entries_for_revision(revision))
        surface_ledger_status = "pass" if ledger.ok else "fail"
        if ledger.error_count:
            findings.append(ClosureSealFoldFinding("error", "surface_ledger_failed", "src/i2p_dht_lab/surfaceledger.py", "rev0069 surface ledger failed"))
    except Exception as exc:  # pragma: no cover
        surface_ledger_status = "exception"
        findings.append(ClosureSealFoldFinding("error", "surface_ledger_exception", "src/i2p_dht_lab/surfaceledger.py", str(exc)))
    status = "pass" if not any(f.severity == "error" for f in findings) else "fail"
    digest = sha256(CLOSURE_SEAL_FOLD_DOMAIN + b":report:" + bencode({
        b"revision": revision,
        b"artifact": artifact,
        b"status": status,
        b"predecessor": predecessor_status,
        b"foldmap": foldmap_status,
        b"foldregistry": foldregistry_status,
        b"surface": surface_ledger_status,
        b"findings": [finding.bvalue() for finding in findings],
    }))
    return ClosureSealFoldReport(revision, artifact, status, predecessor_status, foldmap_status, foldregistry_status, surface_ledger_status, tuple(findings), digest)
