"""Surface-fold audit for current-revision navigation.

Earlier cube revisions deliberately kept branchlets and duplicate historical
surfaces.  That helps wake-from-amnesia, but it makes the current path harder to
see.  This audit folds current revision pointers into one small report: active
public docs, active surface-ledger entries, stale artifact names, and duplicate
current-doc roles.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .ids import DOMAIN, sha256
from .surfaceledger import audit_surface_ledger

SURFACE_FOLD_DOMAIN = DOMAIN + b":surface-fold-v1:"


@dataclass(frozen=True)
class SurfaceFoldFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class SurfaceFoldReport:
    revision: str
    current_docs: tuple[str, ...]
    findings: tuple[SurfaceFoldFinding, ...]
    digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")

    @property
    def status(self) -> str:
        if self.error_count:
            return "error"
        if self.warning_count:
            return "warn"
        return "pass"


def audit_surface_fold(root: str | Path, *, revision: str, artifact_stem: str) -> SurfaceFoldReport:
    root_path = Path(root)
    findings: list[SurfaceFoldFinding] = []
    public_path = root_path / "PUBLIC_SURFACE.json"
    public_revision = ""
    if not public_path.exists():
        findings.append(SurfaceFoldFinding("error", "missing_public_surface", "PUBLIC_SURFACE.json", "public surface is absent"))
        current_docs: tuple[str, ...] = ()
    else:
        public = json.loads(public_path.read_text(encoding="utf-8"))
        public_revision = str(public.get("revision", ""))
        if public_revision == revision and public.get("artifact_stem") != artifact_stem:
            findings.append(SurfaceFoldFinding("error", "artifact_stem_drift", "PUBLIC_SURFACE.json", "artifact stem does not match packaged directory"))
        entry_points = public.get("entry_points", [])
        if public_revision == revision:
            current_docs = tuple(entry.get("path", "") for entry in entry_points if str(entry.get("role", "")).endswith("current") or revision in str(entry.get("path", "")))
        else:
            current_docs = tuple(sorted(str(path.relative_to(root_path)) for path in (root_path / "docs").glob(f"*{revision}*.md")))
        seen_roles: dict[str, int] = {}
        for entry in entry_points:
            role = str(entry.get("role", ""))
            seen_roles[role] = seen_roles.get(role, 0) + 1
            path = root_path / str(entry.get("path", ""))
            if not path.exists():
                findings.append(SurfaceFoldFinding("error", "missing_public_entry", str(entry.get("path", "")), "public entry points at a missing path"))
        for role, count in sorted(seen_roles.items()):
            if role and count > 1 and role.endswith("current"):
                findings.append(SurfaceFoldFinding("warning", "duplicate_current_role", role, "current public role appears more than once"))
        if not current_docs:
            findings.append(SurfaceFoldFinding("warning", "no_current_docs_detected", "PUBLIC_SURFACE.json", f"no {revision}/current docs were discoverable"))

    ledger = audit_surface_ledger(root_path)
    if ledger.error_count:
        findings.append(SurfaceFoldFinding("error", "surface_ledger_errors", "surfaceledger.py", f"active surface ledger has {ledger.error_count} errors"))

    if public_revision == revision:
        for surface in ("README.md", "START_HERE.md"):
            path = root_path / surface
            if path.exists():
                text = path.read_text(encoding="utf-8")
                if revision not in text:
                    findings.append(SurfaceFoldFinding("warning", "landing_page_missing_revision", surface, f"{surface} does not mention {revision}"))
                if artifact_stem not in text and surface == "README.md":
                    findings.append(SurfaceFoldFinding("warning", "readme_missing_artifact_stem", surface, "README does not mention packaged artifact stem"))

    digest = sha256(SURFACE_FOLD_DOMAIN + b":report:" + bencode({
        b"revision": revision,
        b"artifact_stem": artifact_stem,
        b"current_docs": list(current_docs),
        b"findings": [finding.bvalue() for finding in findings],
    }))
    return SurfaceFoldReport(revision, current_docs, tuple(findings), digest)
