import datetime as _dt
import pathlib
import re
from typing import Any

PROJECT_NAME = "DelayBasin"
REVISION_RE = re.compile(r"rev\d{4}")
TIMESTAMP_RE = re.compile(r"\d{4}\.\d{2}\.\d{2}\.\d{2}\.\d{2}")
SLUG_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
BUNDLE_RE = re.compile(r"DelayBasin-(?P<revision>rev\d{4})-(?P<timestamp>\d{4}\.\d{2}\.\d{2}\.\d{2}\.\d{2})-(?P<slug>[a-z0-9]+(?:-[a-z0-9]+)*)\.zip")

PACKAGING_EXCLUDED_PARTS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
PACKAGING_EXCLUDED_FILENAMES = {".permtest", ".DS_Store"}
PACKAGING_EXCLUDED_SUFFIXES = {".pyc", ".pyo"}
PACKAGING_EXCLUDED_NAME_PATTERNS = (
    r"apply_rev\d+\.py",
    r"complete_rev\d+\.py",
    r"finalize_rev\d+\.py",
    r"finish_rev\d+\.py",
)


def _validate_timestamp_calendar(timestamp: str) -> None:
    try:
        _dt.datetime.strptime(timestamp, "%Y.%m.%d.%H.%M")
    except ValueError as exc:
        raise ValueError(f"release timestamp is not a real YYYY.MM.DD.HH.MM calendar time: {timestamp}") from exc


def validate_release_identity(revision: str, timestamp: str, slug: str) -> dict[str, str]:
    """Validate the canonical release filename components before any path is built."""
    if not REVISION_RE.fullmatch(revision):
        raise ValueError(f"release revision must match rev####: {revision}")
    if not TIMESTAMP_RE.fullmatch(timestamp):
        raise ValueError(f"release timestamp must match YYYY.MM.DD.HH.MM: {timestamp}")
    _validate_timestamp_calendar(timestamp)
    if not SLUG_RE.fullmatch(slug):
        raise ValueError(f"release slug must be lowercase dash words only: {slug}")
    bundle = f"{PROJECT_NAME}-{revision}-{timestamp}-{slug}.zip"
    if pathlib.PurePosixPath(bundle).name != bundle or pathlib.PureWindowsPath(bundle).name != bundle:
        raise ValueError(f"release bundle must be a single filename, not a path: {bundle}")
    if not BUNDLE_RE.fullmatch(bundle):
        raise ValueError(f"release bundle failed canonical filename pattern: {bundle}")
    return {"project": PROJECT_NAME, "revision": revision, "timestamp": timestamp, "slug": slug, "bundle": bundle}


def parse_bundle_name(bundle: str) -> dict[str, str]:
    match = BUNDLE_RE.fullmatch(bundle)
    if not match:
        raise ValueError(f"release bundle failed canonical filename pattern: {bundle}")
    data = match.groupdict()
    return validate_release_identity(data["revision"], data["timestamp"], data["slug"])


def build_bundle_name(revision: str, timestamp: str, slug: str) -> str:
    return validate_release_identity(revision, timestamp, slug)["bundle"]


def release_identity_canary_results() -> list[dict[str, Any]]:
    """Run filename-structure canaries without invoking package release."""
    rows: list[dict[str, Any]] = []
    valid = validate_release_identity("rev9999", "2099.12.31.23.59", "safe-lowercase-slug")
    rows.append({
        "id": "release-identity-valid-canonical-name",
        "expected": "valid components produce one canonical DelayBasin release zip filename",
        "observed": valid,
        "status": "pass" if valid["bundle"] == "DelayBasin-rev9999-2099.12.31.23.59-safe-lowercase-slug.zip" else "fail",
    })
    scenarios = [
        ("release-identity-bad-revision", ("rev999", "2099.12.31.23.59", "safe-slug"), "rev####"),
        ("release-identity-bad-calendar", ("rev9999", "2099.02.31.23.59", "safe-slug"), "real YYYY.MM.DD.HH.MM"),
        ("release-identity-uppercase-slug", ("rev9999", "2099.12.31.23.59", "Bad-Slug"), "lowercase dash words"),
        ("release-identity-slash-slug", ("rev9999", "2099.12.31.23.59", "bad/slug"), "lowercase dash words"),
        ("release-identity-dotdot-slug", ("rev9999", "2099.12.31.23.59", "bad-..-slug"), "lowercase dash words"),
        ("release-identity-empty-slug", ("rev9999", "2099.12.31.23.59", ""), "lowercase dash words"),
    ]
    for row_id, args, token in scenarios:
        try:
            validate_release_identity(*args)
        except ValueError as exc:
            message = str(exc)
            rows.append({
                "id": row_id,
                "expected_failure_contains": token,
                "observed_failure": message,
                "status": "pass" if token in message else "fail",
            })
        else:
            rows.append({
                "id": row_id,
                "expected_failure_contains": token,
                "observed_failure": None,
                "status": "fail",
            })
    return rows


def is_frozen_bundle_part(part: str) -> bool:
    return bool(re.fullmatch(r"DelayBasin-rev\d{4}-.*", part))


def release_relative_parts(path: pathlib.Path, root: pathlib.Path) -> tuple[str, ...]:
    """Return archive-relative path parts for packaging hygiene decisions.

    Release hygiene must ignore the absolute parent directories that happen to
    contain the checkout. Otherwise a working directory whose name looks like a
    frozen DelayBasin bundle can accidentally suppress every release file.
    """
    try:
        return path.relative_to(root).parts
    except ValueError:
        return path.parts


def should_skip_release_path(path: pathlib.Path, bundle_name: str | None = None, root: pathlib.Path | None = None) -> bool:
    excluded_parts = set(PACKAGING_EXCLUDED_PARTS)
    if bundle_name:
        excluded_parts.add(bundle_name)
    parts = release_relative_parts(path, root) if root is not None else path.parts
    if any(part in excluded_parts or is_frozen_bundle_part(part) for part in parts):
        return True
    if path.name in PACKAGING_EXCLUDED_FILENAMES:
        return True
    if any(re.fullmatch(pattern, path.name) for pattern in PACKAGING_EXCLUDED_NAME_PATTERNS):
        return True
    if path.suffix in PACKAGING_EXCLUDED_SUFFIXES:
        return True
    return False


def iter_release_paths(root: pathlib.Path, bundle_name: str | None = None):
    paths = []
    for path in root.rglob("*"):
        if path.is_dir():
            continue
        if should_skip_release_path(path, bundle_name, root):
            continue
        paths.append(path)
    yield from sorted(paths, key=lambda p: p.relative_to(root).as_posix())


def extract_revision_from_changelog(changelog_text: str) -> str:
    match = re.search(r"(rev\d{4})", changelog_text)
    if not match:
        raise ValueError("CHANGELOG.md missing rev header")
    return match.group(1)


def build_release_manifest(revision: str, timestamp: str, slug: str) -> dict[str, str | bool]:
    identity = validate_release_identity(revision, timestamp, slug)
    bundle = identity["bundle"]
    return {
        "project": identity["project"],
        "revision": identity["revision"],
        "timestamp": identity["timestamp"],
        "slug": identity["slug"],
        "bundle": bundle,
        "file_manifest": "FILE-MANIFEST.json",
        "checksums": "CHECKSUMS.sha256",
        "provenance": "RELEASE-PROVENANCE.json",
        "deterministic_zip": True,
    }
