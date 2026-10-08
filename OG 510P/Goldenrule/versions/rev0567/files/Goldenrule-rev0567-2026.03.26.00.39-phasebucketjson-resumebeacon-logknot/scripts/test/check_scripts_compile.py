#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import py_compile
import sys
import tempfile
from pathlib import Path


SKIP_PARTS = {'__pycache__', '.mypy_cache', '.pytest_cache', '.ruff_cache'}


def iter_python_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for base in [root / 'scripts', root / 'grlab']:
        for path in base.rglob('*.py'):
            rel = path.relative_to(root)
            if any(part in SKIP_PARTS for part in rel.parts):
                continue
            files.append(path)
    return sorted(files)


def compile_tree(root: Path) -> tuple[bool, list[str]]:
    errors: list[str] = []
    files = iter_python_files(root)
    with tempfile.TemporaryDirectory(prefix='grlab-compile-') as tmpdir:
        tmp_root = Path(tmpdir)
        for path in files:
            rel = path.relative_to(root).as_posix()
            digest = hashlib.sha1(rel.encode('utf-8')).hexdigest()[:16]
            cfile = tmp_root / f'{digest}.pyc'
            try:
                py_compile.compile(str(path), cfile=str(cfile), doraise=True)
            except py_compile.PyCompileError as exc:
                errors.append(f'{rel}: {exc.msg}')
            except OSError as exc:
                errors.append(f'{rel}: {exc}')
    return (not errors, errors)


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    ok, errors = compile_tree(root)
    if not ok:
        print('scripts-compile: compile failure', file=sys.stderr)
        for msg in errors:
            print(f'  - {msg}', file=sys.stderr)
        return 1

    print('scripts-compile: ok')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
