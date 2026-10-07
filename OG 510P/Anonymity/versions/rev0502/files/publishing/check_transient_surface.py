#!/usr/bin/env python3
"""Fail-closed audit for transient artifacts that should not ship inside the archive."""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

DISALLOWED_SUFFIXES = (
    '.aux', '.log', '.out', '.fls', '.fdb_latexmk', '.bcf', '.run.xml', '.synctex.gz', '.bbl', '.blg', '.toc', '.lof', '.lot'
)
PYTHON_BYTECODE_SUFFIXES = ('.pyc', '.pyo')
SERIES_RENDER_DIR_RE = re.compile(r'^series/.+/render\d+$')


def is_disallowed(rel: str, is_dir: bool) -> tuple[bool, str | None]:
    path = pathlib.Path(rel)
    name = path.name
    if any(part == '__pycache__' for part in path.parts):
        return True, 'python_bytecode_cache_dir' if is_dir else 'python_bytecode_cache_file'
    if (not is_dir) and any(name.endswith(s) for s in PYTHON_BYTECODE_SUFFIXES):
        return True, 'python_bytecode_file'
    if (not is_dir) and any(name.endswith(s) for s in DISALLOWED_SUFFIXES):
        return True, 'latex_build_byproduct'
    if is_dir and SERIES_RENDER_DIR_RE.match(rel):
        return True, 'series_review_render_dir'
    if (not is_dir) and any(SERIES_RENDER_DIR_RE.match('/'.join(path.parts[:i])) for i in range(1, len(path.parts))):
        return True, 'series_review_render_file'
    if (not is_dir) and rel.startswith('series/') and name.endswith('.pdf'):
        return True, 'compiled_series_pdf'
    if (not is_dir) and rel == 'build/root_latex/paper.pdf':
        return True, 'ad_hoc_root_compile_pdf'
    return False, None


def audit(root: pathlib.Path) -> dict:
    findings = []
    by_category: dict[str, int] = {}
    for p in sorted(root.rglob('*')):
        rel = p.relative_to(root).as_posix()
        bad, category = is_disallowed(rel, p.is_dir())
        if bad:
            findings.append({'path': rel, 'category': category})
            by_category[category] = by_category.get(category, 0) + 1
    return {
        'status': 'pass' if not findings else 'fail',
        'checked_root': '.',
        'policy': 'PRUNING_POLICY.md',
        'pruned_paths_log': 'PRUNED_TRANSIENT.paths',
        'findings': findings,
        'summary': {
            'disallowed_file_count': len(findings),
            'categories': by_category,
        },
        'fail_closed_rule': 'If this audit fails, default to no publication and prune transient files before trusting the shipped archive surface.'
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default='.')
    ap.add_argument('--write-report', default='')
    args = ap.parse_args()
    root = pathlib.Path(args.root).resolve()
    report = audit(root)
    text = json.dumps(report, indent=2) + '\n'
    if args.write_report:
        out = (root / args.write_report).resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding='utf-8')
    sys.stdout.write(text)
    return 0 if report['status'] == 'pass' else 1


if __name__ == '__main__':
    raise SystemExit(main())
