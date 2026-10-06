import pathlib
import re

PACKAGING_EXCLUDED_PARTS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
PACKAGING_EXCLUDED_FILENAMES = {".permtest", ".DS_Store"}
PACKAGING_EXCLUDED_SUFFIXES = {".pyc", ".pyo"}


def build_bundle_name(revision: str, timestamp: str, slug: str) -> str:
    return f"DelayBasin-{revision}-{timestamp}-{slug}.zip"


def is_frozen_bundle_part(part: str) -> bool:
    return bool(re.fullmatch(r"DelayBasin-rev\d{4}-.*", part))


def should_skip_release_path(path: pathlib.Path, bundle_name: str | None = None) -> bool:
    excluded_parts = set(PACKAGING_EXCLUDED_PARTS)
    if bundle_name:
        excluded_parts.add(bundle_name)
    if any(part in excluded_parts or is_frozen_bundle_part(part) for part in path.parts):
        return True
    if path.name in PACKAGING_EXCLUDED_FILENAMES:
        return True
    if path.suffix in PACKAGING_EXCLUDED_SUFFIXES:
        return True
    return False


def extract_revision_from_changelog(changelog_text: str) -> str:
    match = re.search(r"(rev\d{4})", changelog_text)
    if not match:
        raise ValueError("CHANGELOG.md missing rev header")
    return match.group(1)


def build_release_manifest(revision: str, timestamp: str, slug: str) -> dict[str, str]:
    return {
        "project": "DelayBasin",
        "revision": revision,
        "timestamp": timestamp,
        "slug": slug,
        "bundle": build_bundle_name(revision, timestamp, slug),
    }
