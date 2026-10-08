from __future__ import annotations

import fnmatch
import hashlib
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping

CUBE_NAME_RE = re.compile(
    r"^(?P<project>[A-Za-z0-9][A-Za-z0-9_-]*)-"
    r"(?P<revision>rev\d{4})-"
    r"(?P<timestamp>\d{4}\.\d{2}\.\d{2}\.\d{2}\.\d{2})-"
    r"(?P<codename>[a-z0-9]+(?:-[a-z0-9]+)*)$"
)

DEFAULT_FORBIDDEN_GLOBS: tuple[str, ...] = (
    "build/**",
    ".pytest_cache/**",
    "**/.pytest_cache/**",
    "__pycache__/**",
    "**/__pycache__/**",
    "*.pyc",
    "**/*.pyc",
    "*.pyo",
    "**/*.pyo",
)

REQUIRED_TOP_LEVEL: tuple[str, ...] = (
    "README.md",
    "manifest.json",
    "CHECKSUMS.json",
    "environment.json",
    "requirements.txt",
    ".mucignore",
    "data/revision_log.json",
)


@dataclass(frozen=True)
class CubeIdentity:
    project: str
    revision: str
    timestamp: str
    codename: str
    cube_name: str
    filename: str


@dataclass
class PackageContractReport:
    root: str
    identity: dict[str, str] | None = None
    checks: list[dict[str, Any]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    checksum_file_count: int = 0
    actual_file_count_excluding_checksum_manifest: int = 0

    @property
    def passed(self) -> bool:
        return not self.errors

    def add_check(self, name: str, passed: bool, detail: str = "") -> None:
        self.checks.append({"name": name, "passed": bool(passed), "detail": detail})
        if not passed:
            self.errors.append(f"{name}: {detail}" if detail else name)

    def as_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "root": self.root,
            "identity": self.identity,
            "checks": self.checks,
            "errors": self.errors,
            "warnings": self.warnings,
            "checksum_file_count": self.checksum_file_count,
            "actual_file_count_excluding_checksum_manifest": self.actual_file_count_excluding_checksum_manifest,
        }


def parse_cube_name(name: str) -> CubeIdentity:
    match = CUBE_NAME_RE.fullmatch(name)
    if match is None:
        raise ValueError(
            "cube directory must match "
            "Project-Name-rev####-YYYY.MM.DD.HH.MM-lowercase-hyphen-codename"
        )
    groups = match.groupdict()
    return CubeIdentity(
        project=groups["project"],
        revision=groups["revision"],
        timestamp=groups["timestamp"],
        codename=groups["codename"],
        cube_name=name,
        filename=f"{name}.zip",
    )


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _relative_files(root: Path) -> list[Path]:
    return sorted(
        (path.relative_to(root) for path in root.rglob("*") if path.is_file()),
        key=lambda p: p.as_posix(),
    )


def _matches_any(path: str, patterns: Iterable[str]) -> bool:
    return any(fnmatch.fnmatch(path, pattern) for pattern in patterns)


def sha256_file(path: Path, *, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def build_checksum_manifest(root: str | Path) -> dict[str, Any]:
    root_path = Path(root).resolve()
    files: dict[str, dict[str, Any]] = {}
    for relative in _relative_files(root_path):
        key = relative.as_posix()
        if key == "CHECKSUMS.json":
            continue
        absolute = root_path / relative
        files[key] = {"bytes": absolute.stat().st_size, "sha256": sha256_file(absolute)}
    return {"algorithm": "sha256", "files": files}


def write_checksum_manifest(root: str | Path) -> Path:
    root_path = Path(root).resolve()
    output = root_path / "CHECKSUMS.json"
    output.write_text(
        json.dumps(build_checksum_manifest(root_path), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return output


def audit_package_contract(
    root: str | Path,
    *,
    verify_checksums: bool = True,
    check_forbidden: bool = True,
    forbidden_globs: Iterable[str] = DEFAULT_FORBIDDEN_GLOBS,
) -> PackageContractReport:
    root_path = Path(root).resolve()
    report = PackageContractReport(root=str(root_path))

    try:
        identity = parse_cube_name(root_path.name)
    except ValueError as exc:
        report.add_check("cube_name_format", False, str(exc))
        return report

    report.identity = {
        "project": identity.project,
        "revision": identity.revision,
        "timestamp": identity.timestamp,
        "codename": identity.codename,
        "cube_name": identity.cube_name,
        "filename": identity.filename,
    }
    report.add_check("cube_name_format", True, identity.cube_name)

    missing = [path for path in REQUIRED_TOP_LEVEL if not (root_path / path).is_file()]
    report.add_check(
        "required_top_level_files",
        not missing,
        "all required files present" if not missing else f"missing: {', '.join(missing)}",
    )
    if missing:
        return report

    try:
        manifest = _read_json(root_path / "manifest.json")
    except Exception as exc:  # pragma: no cover - defensive I/O path
        report.add_check("manifest_json", False, f"cannot parse manifest.json: {exc}")
        return report
    report.add_check("manifest_json", isinstance(manifest, Mapping), "manifest is a JSON object")
    if not isinstance(manifest, Mapping):
        return report

    expected_manifest = {
        "revision": identity.revision,
        "timestamp": identity.timestamp,
        "codename": identity.codename,
        "cube_name": identity.cube_name,
        "filename": identity.filename,
    }
    mismatches = {
        key: {"expected": expected, "actual": manifest.get(key)}
        for key, expected in expected_manifest.items()
        if manifest.get(key) != expected
    }
    report.add_check(
        "manifest_identity_alignment",
        not mismatches,
        "manifest matches directory and archive identity" if not mismatches else json.dumps(mismatches, sort_keys=True),
    )

    readme_lines = (root_path / "README.md").read_text(encoding="utf-8").splitlines()
    first_nonempty = next((line.strip() for line in readme_lines if line.strip()), "")
    expected_heading = f"# {identity.project} {identity.revision} — {identity.codename}"
    report.add_check(
        "readme_heading_alignment",
        first_nonempty == expected_heading,
        f"expected {expected_heading!r}; found {first_nonempty!r}",
    )

    try:
        revision_log = _read_json(root_path / "data/revision_log.json")
        revisions = revision_log.get("revisions", []) if isinstance(revision_log, Mapping) else []
    except Exception as exc:  # pragma: no cover - defensive I/O path
        report.add_check("revision_log_json", False, f"cannot parse revision log: {exc}")
        revisions = []
    report.add_check("revision_log_nonempty", bool(revisions), f"entries={len(revisions)}")
    if revisions:
        latest = revisions[-1]
        latest_expected = {
            "revision": identity.revision,
            "timestamp": identity.timestamp,
            "codename": identity.codename,
        }
        latest_mismatches = {
            key: {"expected": expected, "actual": latest.get(key)}
            for key, expected in latest_expected.items()
            if not isinstance(latest, Mapping) or latest.get(key) != expected
        }
        report.add_check(
            "revision_log_latest_alignment",
            not latest_mismatches,
            "latest revision-log entry matches package identity"
            if not latest_mismatches
            else json.dumps(latest_mismatches, sort_keys=True),
        )

        seen: set[str] = set()
        duplicates: list[str] = []
        nonmonotonic: list[str] = []
        previous = -1
        for entry in revisions:
            rev = str(entry.get("revision", "")) if isinstance(entry, Mapping) else ""
            if rev in seen:
                duplicates.append(rev)
            seen.add(rev)
            try:
                number = int(rev.removeprefix("rev"))
            except ValueError:
                nonmonotonic.append(rev)
                continue
            if number <= previous:
                nonmonotonic.append(rev)
            previous = number
        report.add_check(
            "revision_log_unique_monotonic",
            not duplicates and not nonmonotonic,
            "revision identifiers are unique and increasing"
            if not duplicates and not nonmonotonic
            else f"duplicates={duplicates}; nonmonotonic={nonmonotonic}",
        )

    actual_files = [path.as_posix() for path in _relative_files(root_path)]
    if check_forbidden:
        forbidden = sorted(path for path in actual_files if _matches_any(path, forbidden_globs))
        report.add_check(
            "forbidden_generated_artifacts_absent",
            not forbidden,
            "no cache/build artifacts in linked package"
            if not forbidden
            else f"found {len(forbidden)}: {forbidden[:20]}",
        )

    if verify_checksums:
        try:
            checksum_doc = _read_json(root_path / "CHECKSUMS.json")
            checksum_files = checksum_doc.get("files", {}) if isinstance(checksum_doc, Mapping) else {}
            algorithm = checksum_doc.get("algorithm") if isinstance(checksum_doc, Mapping) else None
        except Exception as exc:  # pragma: no cover - defensive I/O path
            report.add_check("checksum_manifest_json", False, f"cannot parse CHECKSUMS.json: {exc}")
            return report
        report.add_check("checksum_algorithm", algorithm == "sha256", f"algorithm={algorithm!r}")
        if not isinstance(checksum_files, Mapping):
            report.add_check("checksum_manifest_shape", False, "files must be an object")
            return report

        expected_paths = {path for path in actual_files if path != "CHECKSUMS.json"}
        listed_paths = set(str(path) for path in checksum_files)
        report.checksum_file_count = len(listed_paths)
        report.actual_file_count_excluding_checksum_manifest = len(expected_paths)
        missing_from_manifest = sorted(expected_paths - listed_paths)
        extra_in_manifest = sorted(listed_paths - expected_paths)
        report.add_check(
            "checksum_exact_file_coverage",
            not missing_from_manifest and not extra_in_manifest,
            "checksum manifest covers every file except itself"
            if not missing_from_manifest and not extra_in_manifest
            else f"missing={missing_from_manifest[:20]}; extra={extra_in_manifest[:20]}",
        )

        bad_hashes: list[str] = []
        bad_sizes: list[str] = []
        malformed: list[str] = []
        for relative in sorted(expected_paths & listed_paths):
            entry = checksum_files.get(relative)
            if not isinstance(entry, Mapping):
                malformed.append(relative)
                continue
            absolute = root_path / relative
            actual_size = absolute.stat().st_size
            if entry.get("bytes") != actual_size:
                bad_sizes.append(relative)
            if entry.get("sha256") != sha256_file(absolute):
                bad_hashes.append(relative)
        report.add_check(
            "checksum_entries_well_formed",
            not malformed,
            "all checksum entries are objects" if not malformed else f"malformed={malformed[:20]}",
        )
        report.add_check(
            "checksum_byte_sizes_match",
            not bad_sizes,
            "all recorded byte sizes match" if not bad_sizes else f"mismatches={bad_sizes[:20]}",
        )
        report.add_check(
            "checksum_hashes_match",
            not bad_hashes,
            "all SHA-256 hashes match" if not bad_hashes else f"mismatches={bad_hashes[:20]}",
        )

    environment = _read_json(root_path / "environment.json")
    report.add_check(
        "environment_manifest_shape",
        isinstance(environment, Mapping) and isinstance(environment.get("python"), Mapping),
        "environment.json records Python and direct dependencies",
    )

    return report


__all__ = [
    "CubeIdentity",
    "PackageContractReport",
    "DEFAULT_FORBIDDEN_GLOBS",
    "audit_package_contract",
    "build_checksum_manifest",
    "parse_cube_name",
    "sha256_file",
    "write_checksum_manifest",
]
