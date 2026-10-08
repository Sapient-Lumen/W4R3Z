"""Revision surface cast audit.

``foldspine.py`` proved useful but pinned one revision.  This module keeps the
same small audit vocabulary while making the current revision spec declarative,
so future cubes can add one cast instead of another bespoke fold module.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .ids import DOMAIN, sha256
from .surfaceledger import audit_surface_ledger, entries_for_revision

SPINE_CAST_DOMAIN = DOMAIN + b":spine-cast-v1:"


@dataclass(frozen=True)
class SpineCastFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class RevisionCastSpec:
    revision: str
    artifact_stem: str
    modules: tuple[str, ...]
    tests: tuple[str, ...]
    docs: tuple[str, ...]
    public_needles: tuple[str, ...]
    head_needles: tuple[str, ...]
    index_needles: tuple[str, ...]
    script_needles: tuple[str, ...] = ()


@dataclass(frozen=True)
class SpineCastReport:
    spec: RevisionCastSpec
    status: str
    findings: tuple[SpineCastFinding, ...]
    report_digest: bytes

    @property
    def revision(self) -> str:
        return self.spec.revision

    @property
    def error_count(self) -> int:
        return sum(1 for item in self.findings if item.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for item in self.findings if item.severity == "warning")


def rev0029_cast_spec(artifact_stem: str) -> RevisionCastSpec:
    return RevisionCastSpec(
        revision="rev0029",
        artifact_stem=artifact_stem,
        modules=(
            "src/i2p_dht_lab/absencegate.py",
            "src/i2p_dht_lab/keycrisis.py",
            "src/i2p_dht_lab/checkpointlane.py",
            "src/i2p_dht_lab/spinecast.py",
        ),
        tests=("tests/test_rev0029_negspace_keycrisis_checkpointfold.py",),
        docs=(
            "docs/279-rev0029-negspace-keycrisis-checkpointfold.md",
            "docs/280-absence-gate-negative-space-pressure.md",
            "docs/281-key-crisis-recovery-rotation.md",
            "docs/282-checkpoint-lane-restart-boundary.md",
            "docs/283-spinecast-audit-refactor.md",
            "docs/284-python-surface-rev0029.md",
            "docs/285-wake-from-amnesia-rev0029.md",
            "docs/286-risk-register-rev0029.md",
            "docs/287-research-notes-2026-06-03-rev0029.md",
            "docs/288-proof-obligation-rev0029.md",
        ),
        public_needles=(
            "docs/279-rev0029-negspace-keycrisis-checkpointfold.md",
            "docs/283-spinecast-audit-refactor.md",
            "rev0029",
        ),
        head_needles=("absence_gate", "key_crisis", "checkpoint_lane", "spine_cast"),
        index_needles=("rev0029 negspace / keycrisis / checkpointfold",),
        script_needles=("rev0029", "audit_spine_cast"),
    )


def _contains(path: Path, needle: str) -> bool:
    try:
        return needle in path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return False


def audit_spine_cast(root: str | Path, spec: RevisionCastSpec | None = None, *, revision: str = "rev0029", artifact_stem: str | None = None) -> SpineCastReport:
    root_path = Path(root)
    if spec is None:
        artifact_stem = artifact_stem or root_path.name
        if revision != "rev0029":
            raise ValueError("spinecast currently declares the rev0029 current cast")
        spec = rev0029_cast_spec(artifact_stem)
    findings: list[SpineCastFinding] = []
    for rel in spec.modules + spec.tests + spec.docs:
        if not (root_path / rel).exists():
            findings.append(SpineCastFinding("error", "missing_cast_path", rel, "revision cast path is absent"))
    for needle in spec.public_needles:
        if not _contains(root_path / "PUBLIC_SURFACE.json", needle):
            findings.append(SpineCastFinding("error", "public_surface_missing_needle", "PUBLIC_SURFACE.json", f"missing {needle}"))
    for needle in spec.head_needles:
        if not _contains(root_path / "HEAD_REGISTRY.json", needle):
            findings.append(SpineCastFinding("error", "head_registry_missing_needle", "HEAD_REGISTRY.json", f"missing {needle}"))
    for needle in spec.index_needles:
        if not _contains(root_path / "docs/00-index.md", needle):
            findings.append(SpineCastFinding("error", "index_missing_needle", "docs/00-index.md", f"missing {needle}"))
    for needle in spec.script_needles:
        if not _contains(root_path / "scripts/evidence/run_cube_audit.py", needle):
            findings.append(SpineCastFinding("error", "cube_audit_missing_needle", "scripts/evidence/run_cube_audit.py", f"missing {needle}"))
    for file_name in ("README.md", "START_HERE.md", "VERSION"):
        if not _contains(root_path / file_name, spec.revision):
            findings.append(SpineCastFinding("error", "revision_drift", file_name, f"missing {spec.revision}"))
    try:
        ledger = audit_surface_ledger(root_path, entries_for_revision(spec.revision))
        if ledger.error_count:
            findings.append(SpineCastFinding("error", "surface_ledger_errors", "src/i2p_dht_lab/surfaceledger.py", "surface ledger does not pass for cast revision"))
    except Exception as exc:  # pragma: no cover - defensive audit surface
        findings.append(SpineCastFinding("error", "surface_ledger_exception", "src/i2p_dht_lab/surfaceledger.py", str(exc)))
    status = "pass" if not any(item.severity == "error" for item in findings) else "fail"
    digest = sha256(SPINE_CAST_DOMAIN + b":report:" + bencode({
        b"revision": spec.revision,
        b"artifact": spec.artifact_stem,
        b"status": status,
        b"findings": [item.bvalue() for item in findings],
    }))
    return SpineCastReport(spec, status, tuple(findings), digest)
