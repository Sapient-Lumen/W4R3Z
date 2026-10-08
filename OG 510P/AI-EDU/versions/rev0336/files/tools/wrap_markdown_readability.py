"""Soft-wrap long Markdown prose lines without touching tables or code fences."""
from __future__ import annotations

import re
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WIDTH = 100

LIST_RE = re.compile(r'^(\s*)([-*+] |\d+[.)] )(.*)$')


def wrap_line(line: str) -> list[str]:
    if len(line) <= WIDTH:
        return [line]
    if not line.strip():
        return [line]
    stripped = line.lstrip()
    if stripped.startswith(('#', '|', '```', '~~~')):
        return [line]
    if line.startswith('URL: ') or line.startswith('http://') or line.startswith('https://'):
        return [line]

    match = LIST_RE.match(line)
    if match:
        indent, bullet, body = match.groups()
        return textwrap.wrap(
            body,
            width=WIDTH,
            initial_indent=indent + bullet,
            subsequent_indent=indent + ' ' * len(bullet),
            break_long_words=False,
            break_on_hyphens=False,
        ) or [line]

    indent_len = len(line) - len(stripped)
    indent = ' ' * indent_len
    return textwrap.wrap(
        stripped,
        width=WIDTH,
        initial_indent=indent,
        subsequent_indent=indent,
        break_long_words=False,
        break_on_hyphens=False,
    ) or [line]


def wrap_file(path: Path) -> bool:
    text = path.read_text(encoding='utf-8')
    out: list[str] = []
    in_code = False
    changed = False
    for line in text.splitlines():
        fence = line.strip().startswith(('```', '~~~'))
        if fence:
            out.append(line)
            in_code = not in_code
            continue
        if in_code:
            out.append(line)
            continue
        wrapped = wrap_line(line)
        if wrapped != [line]:
            changed = True
        out.extend(wrapped)
    new_text = '\n'.join(out) + ('\n' if text.endswith('\n') else '')
    if new_text != text:
        path.write_text(new_text, encoding='utf-8')
        changed = True
    return changed


changed_files = []
for path in sorted(ROOT.rglob('*.md')):
    if any(part == '__pycache__' for part in path.parts):
        continue
    if wrap_file(path):
        changed_files.append(path.relative_to(ROOT).as_posix())

print(f'wrap_markdown_readability: wrapped {len(changed_files)} files')
for rel in changed_files[:40]:
    print(f'  {rel}')
if len(changed_files) > 40:
    print(f'  ... {len(changed_files) - 40} more')
