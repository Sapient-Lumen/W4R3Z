#!/usr/bin/env python3
"""Check that promoted voter-facing family-tail surfaces appear in core entrypoints."""

from __future__ import annotations

from pathlib import Path

from _shared.voter_surface_registry import load_surface_registry

ROOT = Path(__file__).resolve().parents[1]
UPPER_BAND_START = 335
ENTRYPOINTS = [
    (ROOT / 'README.md', 'full'),
    (ROOT / 'ARCHIVE_INDEX.md', 'full'),
    (ROOT / 'docs' / 'START_HERE.md', 'full'),
    (ROOT / 'docs' / '242-audience-reading-paths-and-what-to-ignore.md', 'full'),
    (ROOT / 'docs' / '13-artifact-index.md', 'basename'),
    (ROOT / 'docs' / '310-voter-facing-public-answer-surfaces-family-map-and-promotion-rules.md', 'full'),
]


def main() -> int:
    table = load_surface_registry()
    rows = []
    for row in table.rows:
        if not any(row.values()):
            continue
        doc_id = int(row['doc_id'])
        if doc_id < UPPER_BAND_START:
            continue
        doc_path = row['doc_path']
        rows.append((doc_id, doc_path, Path(doc_path).name))

    errors: list[str] = []
    for path, mode in ENTRYPOINTS:
        if not path.exists():
            errors.append(f'missing entrypoint file: {path.relative_to(ROOT)}')
            continue
        text = path.read_text(encoding='utf-8')
        for doc_id, full, base in rows:
            needle = full if mode == 'full' else base
            if needle not in text:
                errors.append(
                    f"{path.relative_to(ROOT)}: missing voter-facing family-tail doc {doc_id} ({needle})"
                )

    if errors:
        for e in errors:
            print('ERROR:', e)
        return 2

    print(
        'PASS: voter-facing family-tail entrypoint coverage '
        f'(docs {rows[0][0]}–{rows[-1][0]} present across {len(ENTRYPOINTS)} core entrypoints)'
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
