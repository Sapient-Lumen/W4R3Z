#!/usr/bin/env python3
from pathlib import Path
import json
import sys
import zipfile

sys.dont_write_bytecode = True

TRANSIENT_DIR_NAMES = {"__pycache__", ".pytest_cache", ".mypy_cache", ".git"}
TRANSIENT_FILE_SUFFIXES = {".pyc", ".pyo", ".pyd", ".tmp", ".swp"}
TRANSIENT_FILE_NAMES = {".DS_Store"}


def canonical_release_root_name(manifest: dict) -> str:
    bundle = manifest['bundle']
    return bundle[:-4] if bundle.endswith('.zip') else bundle


def is_transient_release_path(path: Path, root: Path) -> bool:
    rel = path.relative_to(root)
    if any(part in TRANSIENT_DIR_NAMES for part in rel.parts):
        return True
    if path.name in TRANSIENT_FILE_NAMES:
        return True
    if path.suffix in TRANSIENT_FILE_SUFFIXES:
        return True
    return False


def iter_release_files(root: Path):
    for p in root.rglob('*'):
        if p.is_file() and not is_transient_release_path(p, root):
            yield p


def build_release(root: Path) -> Path:
    manifest = json.loads((root / 'RELEASE-MANIFEST.json').read_text())
    out = root.parent / manifest['bundle']
    archive_root = Path(canonical_release_root_name(manifest))
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED, compresslevel=1) as zf:
        for p in iter_release_files(root):
            if p.name != out.name:
                zf.write(p, archive_root / p.relative_to(root))
    return out


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    print(build_release(root))


if __name__ == '__main__':
    main()
