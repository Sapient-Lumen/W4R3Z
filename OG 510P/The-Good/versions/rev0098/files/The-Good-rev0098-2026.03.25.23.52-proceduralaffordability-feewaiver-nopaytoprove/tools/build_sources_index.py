#!/usr/bin/env python3
from __future__ import annotations

import json

from archive_meta import NOTE_SOURCE_MAP, ROOT, SOURCE_CATALOG, current_revision


def main() -> None:
    reverse = {key: [] for key in SOURCE_CATALOG}
    for note, source_keys in NOTE_SOURCE_MAP.items():
        for key in source_keys:
            reverse[key].append(note)

    out = {
        'revision': current_revision(),
        'sources': [
            {
                'key': key,
                **SOURCE_CATALOG[key],
                'usage_count': len(reverse[key]),
                'used_by': reverse[key],
            }
            for key in sorted(SOURCE_CATALOG)
        ],
        'note_source_map': NOTE_SOURCE_MAP,
    }
    (ROOT / 'SOURCES.json').write_text(json.dumps(out, indent=2) + '\n')

    lines = [
        f'# Sources — {current_revision()}',
        '',
        'The archive keeps citations compact by storing sources here and linking them to notes through stable keys.',
        'Each source now carries a lightweight type and stability tag so philosophy references, policy frameworks, scientific assessments, and scientific statements do not blur together.',
        '',
        '## Source catalog',
        '',
    ]
    for key in sorted(SOURCE_CATALOG):
        entry = SOURCE_CATALOG[key]
        used_by = reverse[key]
        lines.extend(
            [
                f"### {key} — {entry['title']}",
                '',
                f"- publisher: {entry['publisher']}",
                f"- kind: {entry['kind']}",
                f"- stability: {entry['stability']}",
                f"- url: {entry['url']}",
                f"- usage count: {len(used_by)}",
                f"- used by: {', '.join(f'`{p}`' for p in used_by) if used_by else '_unused_'}",
                '',
            ]
        )
    lines.append('## Note-to-source map')
    lines.append('')
    for note, source_keys in NOTE_SOURCE_MAP.items():
        lines.append(f"- `{note}` → {', '.join(f'`{k}`' for k in source_keys)}")
    lines.append('')
    (ROOT / 'SOURCES.md').write_text('\n'.join(lines))


if __name__ == '__main__':
    main()
