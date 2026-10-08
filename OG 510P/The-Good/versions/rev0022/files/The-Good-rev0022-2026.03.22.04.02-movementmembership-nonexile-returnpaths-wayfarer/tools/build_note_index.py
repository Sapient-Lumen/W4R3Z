#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

from archive_meta import ARCHIVE, ROOT, TAG_RULES, current_revision


def first_heading(path: Path) -> str:
    for line in path.read_text(errors='ignore').splitlines():
        if line.startswith('# '):
            heading = line[2:].strip()
            parts = heading.split(' — ', 1)
            return parts[1] if len(parts) == 2 else heading
    return path.stem


def extract_one_line_thesis(path: Path) -> str:
    lines = path.read_text(errors='ignore').splitlines()
    capture = False
    for line in lines:
        if line.strip() == '## One-line thesis':
            capture = True
            continue
        if capture and line.startswith('## '):
            break
        if capture and line.strip():
            return line.strip()
    return ''


def infer_tags(text: str) -> list[str]:
    haystack = text.lower()
    tags: list[str] = []
    for tag, keywords in TAG_RULES.items():
        if any(keyword in haystack for keyword in keywords):
            tags.append(tag)
    return sorted(set(tags))


def main() -> None:
    items = []
    for path in sorted(ARCHIVE.glob('[0-9][0-9][0-9]-*.md')):
        m = re.match(r'^(\d{3})-(.+)\.md$', path.name)
        if not m:
            continue
        heading = first_heading(path)
        thesis = extract_one_line_thesis(path)
        body = path.read_text(errors='ignore')
        items.append(
            {
                'number': int(m.group(1)),
                'slug': m.group(2),
                'file': str(path.relative_to(ROOT)),
                'title': heading,
                'one_line_thesis': thesis,
                'tags': infer_tags(body),
            }
        )

    out_json = {'revision': current_revision(), 'count': len(items), 'items': items}
    (ROOT / 'ARCHIVE_INDEX.json').write_text(json.dumps(out_json, indent=2) + '\n')

    lines = [f'# Index — {current_revision()}', '', f'Total notes: **{len(items)}**', '']
    for item in items:
        tags = ', '.join(f'`{t}`' for t in item['tags']) if item['tags'] else '_none_'
        lines.extend(
            [
                f"## {item['number']:03d} — {item['title']}",
                '',
                f"- file: `{item['file']}`",
                f'- tags: {tags}',
                f"- thesis: {item['one_line_thesis']}",
                '',
            ]
        )
    (ROOT / 'INDEX.md').write_text('\n'.join(lines) + '\n')


if __name__ == '__main__':
    main()
