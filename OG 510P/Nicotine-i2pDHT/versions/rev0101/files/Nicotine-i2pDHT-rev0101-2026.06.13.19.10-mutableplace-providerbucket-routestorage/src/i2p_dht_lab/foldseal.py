"""rev0029 audit/refactor seal for the current risk path.

``foldspine.py`` pinned rev0028.  rev0029 adds a small seal rather than editing
history away: it checks the new checkpoint, egress, dispatch-join, and fold-seal
surfaces while also proving the predecessor fold still passes.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .foldspine import audit_fold_spine
from .ids import DOMAIN, sha256
from .surfaceledger import audit_surface_ledger, entries_for_revision

FOLD_SEAL_DOMAIN = DOMAIN + b":fold-seal-v1:"


@dataclass(frozen=True)
class FoldSealFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class FoldSealReport:
    revision: str
    artifact_stem: str
    status: str
    predecessor_status: str
    findings: tuple[FoldSealFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for item in self.findings if item.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for item in self.findings if item.severity == "warning")


REV0029_MODULES = (
    "src/i2p_dht_lab/checkpointlane.py",
    "src/i2p_dht_lab/egressmeter.py",
    "src/i2p_dht_lab/dispatchjoin.py",
    "src/i2p_dht_lab/foldseal.py",
)
REV0029_TESTS = ("tests/test_rev0029_checkpoint_egress_dispatch_foldseal.py",)
REV0029_DOCS = (
    "docs/279-rev0029-checkpointlane-egressmeter-foldseal.md",
    "docs/280-checkpoint-lane-restart-pressure.md",
    "docs/281-egress-meter-metadata-budget.md",
    "docs/282-dispatch-join-misbind-egress.md",
    "docs/283-foldseal-audit-refactor.md",
    "docs/284-python-surface-rev0029.md",
    "docs/285-wake-from-amnesia-rev0029.md",
    "docs/286-risk-register-rev0029.md",
    "docs/287-proof-obligation-rev0029.md",
)
HEAD_NEEDLES = ("checkpoint_lane", "egress_meter", "dispatch_join", "fold_seal")
PUBLIC_NEEDLES = ("rev0029", "docs/279-rev0029-checkpointlane-egressmeter-foldseal.md", "checkpointlane")
INDEX_NEEDLES = ("rev0029 checkpointlane / egressmeter / foldseal",)


def _contains(path: Path, needle: str) -> bool:
    try:
        return needle in path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return False


def audit_fold_seal(root: str | Path, *, revision: str = "rev0029", artifact_stem: str | None = None) -> FoldSealReport:
    if revision != "rev0029":
        raise ValueError("foldseal currently pins the rev0029 active seal")
    root_path = Path(root)
    artifact_stem = artifact_stem or root_path.name
    findings: list[FoldSealFinding] = []
    for rel in REV0029_MODULES + REV0029_TESTS + REV0029_DOCS:
        if not (root_path / rel).exists():
            findings.append(FoldSealFinding("error", "missing_foldseal_path", rel, "rev0029 foldseal path is absent"))
    for needle in HEAD_NEEDLES:
        if not _contains(root_path / "HEAD_REGISTRY.json", needle):
            findings.append(FoldSealFinding("error", "head_registry_missing_needle", "HEAD_REGISTRY.json", f"missing {needle}"))
    for needle in PUBLIC_NEEDLES:
        if not _contains(root_path / "PUBLIC_SURFACE.json", needle):
            findings.append(FoldSealFinding("error", "public_surface_missing_needle", "PUBLIC_SURFACE.json", f"missing {needle}"))
    for needle in INDEX_NEEDLES:
        if not _contains(root_path / "docs/00-index.md", needle):
            findings.append(FoldSealFinding("error", "index_missing_needle", "docs/00-index.md", f"missing {needle}"))
    if not _contains(root_path / "README.md", revision):
        findings.append(FoldSealFinding("error", "readme_revision_drift", "README.md", "README does not name rev0029"))
    if not _contains(root_path / "START_HERE.md", revision):
        findings.append(FoldSealFinding("error", "start_here_revision_drift", "START_HERE.md", "START_HERE does not name rev0029"))
    try:
        predecessor = audit_fold_spine(root_path, revision="rev0028", artifact_stem=artifact_stem)
        predecessor_status = f"rev0028_foldspine:{predecessor.status}"
        if predecessor.status != "pass":
            findings.append(FoldSealFinding("error", "predecessor_fold_failed", "src/i2p_dht_lab/foldspine.py", predecessor_status))
    except Exception as exc:  # pragma: no cover - defensive audit surface
        predecessor_status = "rev0028_foldspine:exception"
        findings.append(FoldSealFinding("error", "predecessor_fold_exception", "src/i2p_dht_lab/foldspine.py", str(exc)))
    try:
        ledger = audit_surface_ledger(root_path, entries_for_revision(revision))
        if ledger.error_count:
            findings.append(FoldSealFinding("error", "surface_ledger_errors", "src/i2p_dht_lab/surfaceledger.py", "surface ledger does not pass for rev0029"))
    except Exception as exc:  # pragma: no cover
        findings.append(FoldSealFinding("error", "surface_ledger_exception", "src/i2p_dht_lab/surfaceledger.py", str(exc)))
    status = "pass" if not any(item.severity == "error" for item in findings) else "fail"
    digest = sha256(FOLD_SEAL_DOMAIN + b":report:" + bencode({
        b"revision": revision,
        b"artifact": artifact_stem,
        b"status": status,
        b"predecessor": predecessor_status,
        b"findings": [item.bvalue() for item in findings],
    }))
    return FoldSealReport(revision, artifact_stem, status, predecessor_status, tuple(findings), digest)
