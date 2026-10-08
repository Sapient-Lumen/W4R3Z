"""Cube structure audit helpers.

This module is deliberately mundane.  The cube is accumulating speculative
surfaces quickly, so rev0013 starts checking packaging hygiene and historical
surface drift without pretending every warning should fail the build.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .supersession import SupersessionMap, load_supersession_map

ADR_PREFIX = re.compile(r"^(\d{4})-")
DOC_PREFIX = re.compile(r"^(\d{2,3})-")
TRANSIENT_NAMES = {".pytest_cache", "__pycache__", ".mypy_cache", ".ruff_cache"}


@dataclass(frozen=True)
class CubeAuditFinding:
    severity: str
    code: str
    path: str
    detail: str


@dataclass(frozen=True)
class CubeAuditReport:
    root: str
    findings: tuple[CubeAuditFinding, ...]
    file_count: int

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")

    @property
    def info_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "info")

    @property
    def status(self) -> str:
        return "fail" if self.error_count else "warn" if self.warning_count else "pass"

    def as_dict(self) -> dict[str, object]:
        return {
            "schema": "i2p_dht_lab.cube_audit_report.v1",
            "root": self.root,
            "status": self.status,
            "file_count": self.file_count,
            "warning_count": self.warning_count,
            "info_count": self.info_count,
            "error_count": self.error_count,
            "findings": [finding.__dict__ for finding in self.findings],
        }


def _duplicate_prefix_findings(root: Path, directory: str, pattern: re.Pattern[str], code: str, supersession: SupersessionMap) -> list[CubeAuditFinding]:
    base = root / directory
    if not base.exists():
        return []
    by_prefix: dict[str, list[Path]] = {}
    for path in sorted(base.glob("*.md")):
        match = pattern.match(path.name)
        if match:
            by_prefix.setdefault(match.group(1), []).append(path)
    findings: list[CubeAuditFinding] = []
    for prefix, paths in sorted(by_prefix.items()):
        if len(paths) <= 1:
            continue
        rels = [str(path.relative_to(root)) for path in paths]
        severity = "info" if supersession.covers_any(rels) else "warning"
        suffix = " covered by HISTORICAL_SUPERSESSION.json" if severity == "info" else ""
        findings.append(CubeAuditFinding(severity, code, directory, f"duplicate numeric prefix {prefix}: {', '.join(rels)}{suffix}"))
    return findings


def _transient_findings(root: Path) -> list[CubeAuditFinding]:
    findings: list[CubeAuditFinding] = []
    for path in root.rglob("*"):
        if path.name in TRANSIENT_NAMES:
            findings.append(CubeAuditFinding("warning", "transient_packaging_surface", str(path.relative_to(root)), "transient cache/build path should not ship in cube zip"))
    return findings


def _shadow_module_findings(root: Path, supersession: SupersessionMap) -> list[CubeAuditFinding]:
    src = root / "src" / "i2p_dht_lab"
    if not src.exists():
        return []
    stems = {path.stem: path for path in src.glob("*.py")}
    findings: list[CubeAuditFinding] = []
    for stem, path in sorted(stems.items()):
        squashed = stem.replace("_", "")
        for other_stem, other_path in sorted(stems.items()):
            if other_stem <= stem:
                continue
            if other_stem.replace("_", "") == squashed:
                rels = [str(path.relative_to(root)), str(other_path.relative_to(root))]
                severity = "info" if supersession.covers_any(rels) else "warning"
                suffix = " covered by HISTORICAL_SUPERSESSION.json" if severity == "info" else ""
                findings.append(CubeAuditFinding(severity, "near_duplicate_module_name", "src/i2p_dht_lab", f"{path.name} and {other_path.name} differ only by separators{suffix}"))
    return findings



def _version_surface_findings(root: Path) -> list[CubeAuditFinding]:
    findings: list[CubeAuditFinding] = []
    version_path = root / "VERSION"
    pyproject_path = root / "pyproject.toml"
    readme_path = root / "README.md"
    full_cube_markers = (root / "PUBLIC_SURFACE.json").exists() or pyproject_path.exists() or readme_path.exists()
    version = version_path.read_text(encoding="utf-8").strip() if version_path.exists() else ""
    if not version:
        if full_cube_markers:
            findings.append(CubeAuditFinding("warning", "missing_version_surface", "VERSION", "VERSION is missing or empty"))
        return findings
    if pyproject_path.exists():
        pyproject_text = pyproject_path.read_text(encoding="utf-8")
        if version.startswith("rev") and version[3:].isdigit():
            expected = f"0.0.{int(version[3:])}"
        else:
            expected = version
        if f'version = "{expected}"' not in pyproject_text:
            findings.append(CubeAuditFinding("warning", "version_pyproject_mismatch", "pyproject.toml", f"pyproject version does not match VERSION {version}"))
    else:
        findings.append(CubeAuditFinding("warning", "missing_pyproject_surface", "pyproject.toml", "pyproject.toml is missing"))
    if readme_path.exists():
        lines = readme_path.read_text(encoding="utf-8").splitlines()
        first_line = lines[0] if lines else ""
        if version not in first_line:
            findings.append(CubeAuditFinding("warning", "readme_version_mismatch", "README.md", f"README title does not mention VERSION {version}"))
    return findings

def audit_cube(root: str | Path) -> CubeAuditReport:
    root_path = Path(root).resolve()
    findings: list[CubeAuditFinding] = []
    supersession = load_supersession_map(root_path)
    findings.extend(_transient_findings(root_path))
    findings.extend(_duplicate_prefix_findings(root_path, "adr", ADR_PREFIX, "duplicate_adr_number", supersession))
    findings.extend(_duplicate_prefix_findings(root_path, "docs", DOC_PREFIX, "duplicate_doc_number", supersession))
    findings.extend(_shadow_module_findings(root_path, supersession))
    findings.extend(_version_surface_findings(root_path))
    file_count = sum(1 for path in root_path.rglob("*") if path.is_file())
    return CubeAuditReport(str(root_path), tuple(findings), file_count)


def summarize_findings(findings: Iterable[CubeAuditFinding]) -> dict[str, int]:
    summary: dict[str, int] = {}
    for finding in findings:
        summary[finding.code] = summary.get(finding.code, 0) + 1
    return summary
