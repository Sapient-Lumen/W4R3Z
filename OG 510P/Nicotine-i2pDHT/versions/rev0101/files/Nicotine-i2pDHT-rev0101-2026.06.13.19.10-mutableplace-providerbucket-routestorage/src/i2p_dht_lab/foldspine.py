"""Declarative current-revision audit spine.

The cube accumulated many one-off ``*fold.py`` audit modules. That history is
useful, but current work needs one small declarative spine that can check the
active revision without adding another bespoke audit pattern every time.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .ids import DOMAIN, sha256
from .surfaceledger import audit_surface_ledger, entries_for_revision

FOLD_SPINE_DOMAIN = DOMAIN + b":fold-spine-v1:"


@dataclass(frozen=True)
class FoldSpineFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class RevisionSpineSpec:
    revision: str
    artifact_stem: str
    modules: tuple[str, ...]
    tests: tuple[str, ...]
    docs: tuple[str, ...]
    public_needles: tuple[str, ...]
    head_needles: tuple[str, ...]
    index_needles: tuple[str, ...]


@dataclass(frozen=True)
class FoldSpineReport:
    spec: RevisionSpineSpec
    status: str
    findings: tuple[FoldSpineFinding, ...]
    report_digest: bytes

    @property
    def revision(self) -> str:
        return self.spec.revision

    @property
    def checked_paths(self) -> tuple[str, ...]:
        return self.spec.modules + self.spec.tests + self.spec.docs

    @property
    def error_count(self) -> int:
        return sum(1 for item in self.findings if item.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for item in self.findings if item.severity == "warning")


def rev0028_spine_spec(artifact_stem: str) -> RevisionSpineSpec:
    return RevisionSpineSpec(
        revision="rev0028",
        artifact_stem=artifact_stem,
        modules=(
            "src/i2p_dht_lab/journallane.py",
            "src/i2p_dht_lab/generatorfuzz.py",
            "src/i2p_dht_lab/refusaljoin.py",
            "src/i2p_dht_lab/samwire.py",
            "src/i2p_dht_lab/foldspine.py",
        ),
        tests=("tests/test_rev0028_journal_generator_refusal_sam_fold.py",),
        docs=(
            "docs/268-rev0028-journallane-generatorfuzz-foldspine.md",
            "docs/269-journal-lane-crash-cut-replay.md",
            "docs/270-generator-fuzz-corpus.md",
            "docs/271-refusal-join-scheduler-pressure.md",
            "docs/272-sam-wire-shadow-script.md",
            "docs/273-foldspine-audit-refactor.md",
            "docs/274-python-surface-rev0028.md",
            "docs/275-wake-from-amnesia-rev0028.md",
            "docs/276-risk-register-rev0028.md",
            "docs/277-research-notes-2026-06-03-rev0028.md",
            "docs/278-proof-obligation-rev0028.md",
        ),
        public_needles=(
            "docs/268-rev0028-journallane-generatorfuzz-foldspine.md",
            "docs/273-foldspine-audit-refactor.md",
            "rev0028",
        ),
        head_needles=("journal_lane", "generator_fuzz", "refusal_join", "sam_wire", "fold_spine"),
        index_needles=("rev0028 journallane / generatorfuzz / foldspine",),
    )


def _contains(path: Path, needle: str) -> bool:
    try:
        return needle in path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return False


def audit_revision_spine(root: str | Path, spec: RevisionSpineSpec) -> FoldSpineReport:
    root_path = Path(root)
    findings: list[FoldSpineFinding] = []
    for rel in spec.modules + spec.tests + spec.docs:
        if not (root_path / rel).exists():
            findings.append(FoldSpineFinding("error", "missing_spine_path", rel, "revision spine path is absent"))
    for needle in spec.public_needles:
        if not _contains(root_path / "PUBLIC_SURFACE.json", needle):
            findings.append(FoldSpineFinding("error", "public_surface_missing_needle", "PUBLIC_SURFACE.json", f"missing {needle}"))
    for needle in spec.head_needles:
        if not _contains(root_path / "HEAD_REGISTRY.json", needle):
            findings.append(FoldSpineFinding("error", "head_registry_missing_needle", "HEAD_REGISTRY.json", f"missing {needle}"))
    for needle in spec.index_needles:
        if not _contains(root_path / "docs/00-index.md", needle):
            findings.append(FoldSpineFinding("error", "index_missing_needle", "docs/00-index.md", f"missing {needle}"))
    if not _contains(root_path / "README.md", spec.revision):
        findings.append(FoldSpineFinding("error", "readme_revision_drift", "README.md", f"missing {spec.revision}"))
    if not _contains(root_path / "START_HERE.md", spec.revision):
        findings.append(FoldSpineFinding("error", "start_here_revision_drift", "START_HERE.md", f"missing {spec.revision}"))
    try:
        ledger = audit_surface_ledger(root_path, entries_for_revision(spec.revision))
        if ledger.error_count:
            findings.append(FoldSpineFinding("error", "surface_ledger_errors", "src/i2p_dht_lab/surfaceledger.py", "surface ledger does not pass for current revision"))
    except Exception as exc:  # pragma: no cover - defensive audit surface
        findings.append(FoldSpineFinding("error", "surface_ledger_exception", "src/i2p_dht_lab/surfaceledger.py", str(exc)))
    status = "pass" if not any(item.severity == "error" for item in findings) else "fail"
    digest = sha256(FOLD_SPINE_DOMAIN + b":report:" + bencode({
        b"revision": spec.revision,
        b"artifact": spec.artifact_stem,
        b"status": status,
        b"findings": [item.bvalue() for item in findings],
    }))
    return FoldSpineReport(spec, status, tuple(findings), digest)


def audit_fold_spine(root: str | Path, *, revision: str = "rev0028", artifact_stem: str | None = None) -> FoldSpineReport:
    root_path = Path(root)
    artifact_stem = artifact_stem or root_path.name
    if revision != "rev0028":
        raise ValueError("foldspine currently pins the rev0028 active spine")
    return audit_revision_spine(root_path, rev0028_spine_spec(artifact_stem))
