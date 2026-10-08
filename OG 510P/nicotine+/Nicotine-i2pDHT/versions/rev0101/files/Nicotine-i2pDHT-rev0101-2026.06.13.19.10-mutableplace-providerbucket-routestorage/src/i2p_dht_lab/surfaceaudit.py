"""Surface-pointer audit for wake-from-amnesia cube hygiene.

The ordinary surface checker is fail-closed for the current public surface.  This
module is gentler and broader: it audits JSON surfaces for missing file pointers
and stale revision strings so a refactor can see drift without immediately
turning every historical wart into a build failure.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class SurfacePointerFinding:
    severity: str
    code: str
    surface: str
    pointer: str
    detail: str


@dataclass(frozen=True)
class SurfacePointerAudit:
    revision: str
    findings: tuple[SurfacePointerFinding, ...]

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")

    @property
    def info_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "info")

    @property
    def status(self) -> str:
        return "warn" if self.warning_count else "pass"

    def as_dict(self) -> dict[str, object]:
        return {
            "schema": "i2p_dht_lab.surface_pointer_audit.v1",
            "revision": self.revision,
            "status": self.status,
            "warning_count": self.warning_count,
            "info_count": self.info_count,
            "findings": [finding.__dict__ for finding in self.findings],
        }


def _load(root: Path, name: str) -> dict[str, object]:
    path = root / name
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _check_path(root: Path, surface: str, pointer: str, findings: list[SurfacePointerFinding]) -> None:
    if not pointer or not isinstance(pointer, str):
        findings.append(SurfacePointerFinding("warning", "empty_pointer", surface, str(pointer), "surface pointer is empty or non-string"))
    elif not (root / pointer).exists():
        findings.append(SurfacePointerFinding("warning", "missing_pointer", surface, pointer, "surface pointer does not exist in cube"))


def _revision_mentions(surface: str, payload: object, revision: str) -> Iterable[SurfacePointerFinding]:
    text = json.dumps(payload, sort_keys=True)
    if revision not in text:
        yield SurfacePointerFinding("info", "revision_not_mentioned", surface, revision, "surface does not mention current revision string")


def audit_surface_pointers(root: str | Path, *, revision: str) -> SurfacePointerAudit:
    root_path = Path(root)
    findings: list[SurfacePointerFinding] = []

    public = _load(root_path, "PUBLIC_SURFACE.json")
    for entry in public.get("entry_points", []):
        if isinstance(entry, dict):
            _check_path(root_path, "PUBLIC_SURFACE.json", str(entry.get("path", "")), findings)

    registry = _load(root_path, "HEAD_REGISTRY.json")
    heads = registry.get("heads", {})
    if isinstance(heads, dict):
        for name, pointer in heads.items():
            _check_path(root_path, "HEAD_REGISTRY.json", str(pointer), findings)
            if isinstance(pointer, str) and pointer.startswith("docs/") and revision in name:
                findings.append(SurfacePointerFinding("info", "revision_name_in_head_key", "HEAD_REGISTRY.json", name, "head key usually names a concept, not a revision"))

    for surface in ("PUBLIC_SURFACE.json", "CLAIM_SURFACE.json", "HEAD_REGISTRY.json", "NEXT_REVISION.json", "REVISION_RECEIPT.json", "PROOF_OBLIGATION_SURFACE.json"):
        payload = _load(root_path, surface)
        findings.extend(_revision_mentions(surface, payload, revision))

    return SurfacePointerAudit(revision, tuple(findings))
