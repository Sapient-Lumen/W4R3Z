"""Navigation/audit fold for rev0026 lineage, bundle, and work-meter surfaces."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .ids import DOMAIN, sha256
from .surfaceledger import audit_surface_ledger, entries_for_revision

LINEAGE_FOLD_DOMAIN = DOMAIN + b":lineage-fold-v1:"


@dataclass(frozen=True)
class LineageFoldFinding:
    severity: str
    code: str
    path: str
    detail: str


@dataclass(frozen=True)
class LineageFoldReport:
    revision: str
    status: str
    findings: tuple[LineageFoldFinding, ...]
    checked_paths: tuple[str, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for item in self.findings if item.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for item in self.findings if item.severity == "warning")


def _contains(path: Path, needle: str) -> bool:
    try:
        return needle in path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return False


def audit_lineage_fold(root: str | Path, *, revision: str = "rev0026") -> LineageFoldReport:
    root_path = Path(root)
    required = (
        "src/i2p_dht_lab/lineagewindow.py",
        "src/i2p_dht_lab/claimbundle.py",
        "src/i2p_dht_lab/workmeter.py",
        "src/i2p_dht_lab/lineagefold.py",
        "tests/test_rev0026_lineagebundle_workmeter.py",
    )
    # The lineage branchlet was folded into the spoken rev0026 branch in rev0027,
    # so historical auditors accept either the original doc numbers or the
    # merged doc numbers.  This keeps wake-from-amnesia tests green without
    # overwriting the schedjoin rev0026 docs.
    doc_choices = (
        ("docs/240-rev0026-lineagebundle-workmeter-fold.md", "docs/250-merged-branchlet-rev0026-lineagebundle-workmeter.md"),
        ("docs/241-lineage-window-gap-pressure.md", "docs/251-lineage-window-gap-pressure.md"),
        ("docs/242-claim-bundle-type-pressure.md", "docs/252-claim-bundle-type-pressure.md"),
        ("docs/243-work-meter-garden-contribution-pressure.md", "docs/253-work-meter-garden-contribution-pressure.md"),
        ("docs/244-lineagefold-audit-refactor.md", "docs/254-lineagefold-audit-refactor-merged.md"),
    )
    findings: list[LineageFoldFinding] = []
    for rel in required:
        if not (root_path / rel).exists():
            findings.append(LineageFoldFinding("error", "missing_required_path", rel, "rev0026 lineage fold required path is absent"))
    for choices in doc_choices:
        if not any((root_path / rel).exists() for rel in choices):
            findings.append(LineageFoldFinding("error", "missing_required_path", " | ".join(choices), "rev0026 lineage fold doc path is absent from original and merged numbering"))
    for rel, needles in (
        ("PUBLIC_SURFACE.json", ("docs/240-rev0026-lineagebundle-workmeter-fold.md", "docs/250-merged-branchlet-rev0026-lineagebundle-workmeter.md", "lineage_window")),
        ("HEAD_REGISTRY.json", ("lineage_window",)),
        ("docs/00-index.md", ("rev0026 lineagebundle / workmeter / fold", "merged rev0026 lineagebundle")),
        ("START_HERE.md", ("rev0026",)),
    ):
        if not any(_contains(root_path / rel, needle) for needle in needles):
            findings.append(LineageFoldFinding("error", "missing_pointer_text", rel, f"expected one of pointer texts not found: {needles}"))
    try:
        ledger = audit_surface_ledger(root_path, entries_for_revision(revision))
        if ledger.error_count:
            findings.append(LineageFoldFinding("error", "surface_ledger_errors", "src/i2p_dht_lab/surfaceledger.py", "surface ledger has current revision errors"))
    except Exception as exc:  # pragma: no cover - defensive audit only
        findings.append(LineageFoldFinding("error", "surface_ledger_exception", "src/i2p_dht_lab/surfaceledger.py", str(exc)))
    status = "pass" if not any(item.severity == "error" for item in findings) else "fail"
    digest = sha256(LINEAGE_FOLD_DOMAIN + b":report:" + bencode({
        b"revision": revision,
        b"status": status,
        b"checked": list(required),
        b"findings": [{b"severity": item.severity, b"code": item.code, b"path": item.path, b"detail": item.detail} for item in findings],
    }))
    return LineageFoldReport(revision, status, tuple(findings), required, digest)
