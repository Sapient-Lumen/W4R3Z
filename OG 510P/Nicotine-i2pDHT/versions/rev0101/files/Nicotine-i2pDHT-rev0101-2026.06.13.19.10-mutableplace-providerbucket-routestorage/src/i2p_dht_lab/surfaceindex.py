"""Current-revision surface index audit.

The cube is intentionally historical: many branchlets, duplicate numeric docs,
and superseded surfaces remain in place.  That is good for wake-from-amnesia but
bad for navigation.  This small audit checks only the current revision's public
index, head registry, and active surface ledger so a reader can find the live
path without deleting old paths.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .ids import DOMAIN, sha256
from .surfaceledger import audit_surface_ledger

SURFACE_INDEX_DOMAIN = DOMAIN + b":surface-index-v1:"


@dataclass(frozen=True)
class SurfaceIndexFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class SurfaceIndexReport:
    revision: str
    indexed_paths: tuple[str, ...]
    findings: tuple[SurfaceIndexFinding, ...]
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


def audit_surface_index(root: str | Path, *, revision: str) -> SurfaceIndexReport:
    root_path = Path(root)
    findings: list[SurfaceIndexFinding] = []
    public_path = root_path / "PUBLIC_SURFACE.json"
    head_path = root_path / "HEAD_REGISTRY.json"
    index_path = root_path / "docs" / "00-index.md"
    indexed_paths: list[str] = []

    if not public_path.exists():
        findings.append(SurfaceIndexFinding("error", "missing_public_surface", "PUBLIC_SURFACE.json", "public surface is missing"))
    else:
        public = json.loads(public_path.read_text(encoding="utf-8"))
        if public.get("revision") != revision:
            findings.append(SurfaceIndexFinding("error", "public_revision_drift", "PUBLIC_SURFACE.json", "public surface revision does not match requested revision"))
        for entry in public.get("entry_points", []):
            path = str(entry.get("path", ""))
            if not path:
                continue
            indexed_paths.append(path)
            if not (root_path / path).exists():
                findings.append(SurfaceIndexFinding("error", "missing_public_entry", path, "public entry path is missing"))

    if not head_path.exists():
        findings.append(SurfaceIndexFinding("error", "missing_head_registry", "HEAD_REGISTRY.json", "head registry is missing"))
    else:
        registry = json.loads(head_path.read_text(encoding="utf-8"))
        if registry.get("revision") != revision:
            findings.append(SurfaceIndexFinding("error", "head_registry_revision_drift", "HEAD_REGISTRY.json", "head registry revision mismatch"))
        for name, path in sorted(registry.get("heads", {}).items()):
            if not (root_path / str(path)).exists():
                findings.append(SurfaceIndexFinding("error", "missing_head_registry_entry", str(path), f"head registry entry {name} points at missing path"))
            # Keep previous-head paths visible too. Historical heads are part of
            # wake-from-amnesia navigation and some regression tests expect the
            # rev0023 range/namespace path to remain indexed after rev0024.
            indexed_paths.append(str(path))

    if not index_path.exists():
        findings.append(SurfaceIndexFinding("error", "missing_doc_index", "docs/00-index.md", "doc index is missing"))
    else:
        index_text = index_path.read_text(encoding="utf-8")
        for path in sorted(set(p for p in indexed_paths if p.startswith("docs/") and revision in p)):
            if path not in index_text:
                findings.append(SurfaceIndexFinding("warning", "doc_index_missing_current_path", path, "current revision path is not mentioned in docs/00-index.md"))

    ledger = audit_surface_ledger(root_path)
    if ledger.error_count:
        findings.append(SurfaceIndexFinding("error", "surface_ledger_error", "src/i2p_dht_lab/surfaceledger.py", f"surface ledger has {ledger.error_count} error(s)"))

    digest = sha256(SURFACE_INDEX_DOMAIN + b":report:" + bencode({
        b"revision": revision,
        b"indexed_paths": sorted(set(indexed_paths)),
        b"findings": [finding.bvalue() for finding in findings],
    }))
    return SurfaceIndexReport(revision=revision, indexed_paths=tuple(sorted(set(indexed_paths))), findings=tuple(findings), digest=digest)
