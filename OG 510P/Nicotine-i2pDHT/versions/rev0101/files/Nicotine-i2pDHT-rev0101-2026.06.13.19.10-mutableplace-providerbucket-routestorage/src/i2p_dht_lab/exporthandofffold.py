"""rev0070 audit/refactor fold for export receipt / retention GC / closure handoff."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .closuresealfold import audit_closure_seal_fold
from .foldmap import audit_fold_map
from .foldregistry import audit_fold_registry
from .ids import DOMAIN, sha256
from .surfaceledger import audit_surface_ledger, entries_for_revision

EXPORT_HANDOFF_FOLD_DOMAIN = DOMAIN + b":export-handoff-fold-v1:"


@dataclass(frozen=True)
class ExportHandoffFoldFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class ExportHandoffFoldReport:
    revision: str
    artifact_stem: str
    status: str
    predecessor_status: str
    foldmap_status: str
    foldregistry_status: str
    surface_ledger_status: str
    findings: tuple[ExportHandoffFoldFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")


def _exists(root: Path, rel: str, needle: str, findings: list[ExportHandoffFoldFinding]) -> None:
    path = root / rel
    if not path.exists():
        findings.append(ExportHandoffFoldFinding("error", "missing_path", rel, "rev0070 exporthandofffold expected this path"))
        return
    text = path.read_text(encoding="utf-8", errors="replace")
    if needle not in text:
        findings.append(ExportHandoffFoldFinding("error", "missing_needle", rel, f"missing needle {needle!r}"))


def audit_export_handoff_fold(root: str | Path, *, revision: str = "rev0070", artifact_stem: str = "") -> ExportHandoffFoldReport:
    root_path = Path(root)
    artifact = artifact_stem or root_path.name
    findings: list[ExportHandoffFoldFinding] = []
    checks = {
        "src/i2p_dht_lab/exportreceipt.py": "ExportReceiptDecisionKind",
        "src/i2p_dht_lab/retentiongc.py": "RetentionGcDecisionKind",
        "src/i2p_dht_lab/closurehandoff.py": "ClosureHandoffDecisionKind",
        "src/i2p_dht_lab/exporthandofffold.py": "audit_export_handoff_fold",
        "tests/test_rev0070_exportreceipt_retentiongc_handoff.py": "test_export_receipt_retention_gc_and_handoff_happy_path",
        "docs/738-rev0070-exportreceipt-retentiongc-closurehandoff.md": "rev0070",
        "docs/739-export-receipt-restart-memory.md": "export receipt",
        "docs/740-retention-gc-after-export.md": "retention GC",
        "docs/741-closure-handoff-redacted-boundary.md": "closure handoff",
        "docs/742-exporthandofffold-audit-refactor.md": "exporthandofffold",
    }
    for rel, needle in checks.items():
        _exists(root_path, rel, needle, findings)
    try:
        predecessor = audit_closure_seal_fold(root_path, revision="rev0069", artifact_stem="x")
        predecessor_status = predecessor.status
        if predecessor.error_count:
            findings.append(ExportHandoffFoldFinding("error", "predecessor_failed", "src/i2p_dht_lab/closuresealfold.py", "rev0069 predecessor failed"))
    except Exception as exc:  # pragma: no cover
        predecessor_status = "exception"
        findings.append(ExportHandoffFoldFinding("error", "predecessor_exception", "src/i2p_dht_lab/closuresealfold.py", str(exc)))
    try:
        fmap = audit_fold_map(root_path, revision=revision, artifact_stem=artifact)
        foldmap_status = fmap.status
        if fmap.error_count:
            findings.append(ExportHandoffFoldFinding("error", "foldmap_failed", "src/i2p_dht_lab/foldmap.py", "rev0070 fold map failed"))
    except Exception as exc:  # pragma: no cover
        foldmap_status = "exception"
        findings.append(ExportHandoffFoldFinding("error", "foldmap_exception", "src/i2p_dht_lab/foldmap.py", str(exc)))
    try:
        registry = audit_fold_registry(root_path, revision=revision)
        foldregistry_status = registry.status
        if registry.error_count:
            findings.append(ExportHandoffFoldFinding("error", "foldregistry_failed", "src/i2p_dht_lab/foldregistry.py", "rev0070 fold registry failed"))
    except Exception as exc:  # pragma: no cover
        foldregistry_status = "exception"
        findings.append(ExportHandoffFoldFinding("error", "foldregistry_exception", "src/i2p_dht_lab/foldregistry.py", str(exc)))
    try:
        ledger = audit_surface_ledger(root_path, entries_for_revision(revision))
        surface_ledger_status = "pass" if ledger.ok else "fail"
        if ledger.error_count:
            findings.append(ExportHandoffFoldFinding("error", "surface_ledger_failed", "src/i2p_dht_lab/surfaceledger.py", "rev0070 surface ledger failed"))
    except Exception as exc:  # pragma: no cover
        surface_ledger_status = "exception"
        findings.append(ExportHandoffFoldFinding("error", "surface_ledger_exception", "src/i2p_dht_lab/surfaceledger.py", str(exc)))
    status = "pass" if not any(finding.severity == "error" for finding in findings) else "fail"
    digest = sha256(EXPORT_HANDOFF_FOLD_DOMAIN + b":report:" + bencode({
        b"revision": revision,
        b"artifact": artifact,
        b"status": status,
        b"predecessor": predecessor_status,
        b"foldmap": foldmap_status,
        b"foldregistry": foldregistry_status,
        b"surface": surface_ledger_status,
        b"findings": [finding.bvalue() for finding in findings],
    }))
    return ExportHandoffFoldReport(revision, artifact, status, predecessor_status, foldmap_status, foldregistry_status, surface_ledger_status, tuple(findings), digest)
