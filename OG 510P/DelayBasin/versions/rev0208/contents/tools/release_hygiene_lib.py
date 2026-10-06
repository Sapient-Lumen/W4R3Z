import pathlib
import re

PACKAGING_EXCLUDED_PARTS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
PACKAGING_EXCLUDED_FILENAMES = {".permtest", ".DS_Store"}
PACKAGING_EXCLUDED_SUFFIXES = {".pyc", ".pyo"}


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
