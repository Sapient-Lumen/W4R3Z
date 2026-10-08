"""Audit/refactor helpers for keeping the cube navigable.

The cube intentionally keeps historical surfaces for wake-from-amnesia, but
active code should not silently import deprecated names or let revision metadata
fall apart.  This module is small, local, and intentionally boring: it scans the
repository tree for active import drift, duplicate public module names, and
revision-pointer inconsistencies.
"""
from __future__ import annotations

import ast
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .bencode import bencode
from .ids import DOMAIN, sha256

SURFACE_CLEAN_DOMAIN = DOMAIN + b":surface-clean-v1:"
LEGACY_MODULE_NAMES = frozenset({"providerpoison"})
CANONICAL_REPLACEMENTS = {"providerpoison": "provider_poison"}


@dataclass(frozen=True)
class SurfaceCleanFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class SurfaceCleanReport:
    revision: str
    findings: tuple[SurfaceCleanFinding, ...]
    digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for item in self.findings if item.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for item in self.findings if item.severity == "warning")

    @property
    def status(self) -> str:
        if self.error_count:
            return "error"
        if self.warning_count:
            return "warn"
        return "pass"


def _module_files(root: Path) -> Iterable[Path]:
    src = root / "src" / "i2p_dht_lab"
    if not src.exists():
        return ()
    return tuple(sorted(path for path in src.glob("*.py") if path.name != "__init__.py"))


def _imported_i2p_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module and node.module.startswith("i2p_dht_lab."):
                found.add(node.module.rsplit(".", 1)[-1])
            elif node.level == 1 and node.module:
                found.add(node.module.split(".", 1)[0])
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("i2p_dht_lab."):
                    found.add(alias.name.rsplit(".", 1)[-1])
    return found


def audit_surface_clean(root: str | Path, *, revision: str, allow_historical_tests: bool = True) -> SurfaceCleanReport:
    root_path = Path(root)
    findings: list[SurfaceCleanFinding] = []

    if (root_path / "VERSION").exists():
        version = (root_path / "VERSION").read_text(encoding="utf-8").strip()
        if version != revision:
            findings.append(SurfaceCleanFinding("error", "version_revision_mismatch", "VERSION", f"VERSION={version!r} expected {revision!r}"))
    for surface in ("PUBLIC_SURFACE.json", "CLAIM_SURFACE.json", "NEXT_REVISION.json", "REVISION_RECEIPT.json"):
        path = root_path / surface
        if path.exists():
            payload = json.loads(path.read_text(encoding="utf-8"))
            if surface == "NEXT_REVISION.json":
                current = payload.get("current_revision")
            else:
                current = payload.get("revision")
            if current != revision:
                findings.append(SurfaceCleanFinding("error", "surface_revision_mismatch", surface, f"surface revision is {current!r}, expected {revision!r}"))

    public_modules = [path.stem for path in _module_files(root_path)]
    duplicates = sorted({name for name in public_modules if public_modules.count(name) > 1})
    for duplicate in duplicates:
        findings.append(SurfaceCleanFinding("error", "duplicate_module_name", f"src/i2p_dht_lab/{duplicate}.py", "module appears more than once"))

    for path in _module_files(root_path):
        imported = _imported_i2p_modules(path)
        for legacy in sorted(imported & LEGACY_MODULE_NAMES):
            findings.append(SurfaceCleanFinding("warning", "legacy_import", str(path.relative_to(root_path)), f"imports legacy {legacy}; prefer {CANONICAL_REPLACEMENTS.get(legacy, 'canonical module')}"))

    if not allow_historical_tests:
        for test in sorted((root_path / "tests").glob("test_*.py")):
            imported = _imported_i2p_modules(test)
            for legacy in sorted(imported & LEGACY_MODULE_NAMES):
                findings.append(SurfaceCleanFinding("warning", "legacy_test_import", str(test.relative_to(root_path)), f"test imports legacy {legacy}"))

    supersession = root_path / "HISTORICAL_SUPERSESSION.json"
    if supersession.exists():
        text = supersession.read_text(encoding="utf-8")
        for legacy, canonical in CANONICAL_REPLACEMENTS.items():
            if legacy not in text or canonical not in text:
                findings.append(SurfaceCleanFinding("warning", "supersession_missing_legacy_mapping", "HISTORICAL_SUPERSESSION.json", f"expected mapping evidence for {legacy}->{canonical}"))
    else:
        findings.append(SurfaceCleanFinding("warning", "missing_supersession_map", "HISTORICAL_SUPERSESSION.json", "historical supersession map is absent"))

    digest = sha256(SURFACE_CLEAN_DOMAIN + b":report:" + bencode({
        b"revision": revision,
        b"findings": [item.bvalue() for item in findings],
    }))
    return SurfaceCleanReport(revision, tuple(findings), digest)
