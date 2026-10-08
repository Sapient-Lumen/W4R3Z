#!/usr/bin/env python3
from pathlib import Path
import sys

sys.dont_write_bytecode = True

from restart_mirror_family import load_state, render_generated_restart_mirror_block, replace_generated_restart_mirror_block


def write_archive_index(root: Path) -> None:
    paths = sorted(
        p for p in root.rglob('*')
        if p.is_file() and p.suffix in {'.md', '.json', '.py'} and '.zip' not in p.name
    )
    lines = ['# Filesystem index', '', f'Total tracked text surfaces: {len(paths)}', '']
    for p in paths:
        rel = p.relative_to(root).as_posix()
        lines.append(f'- `{rel}`')
    (root / 'ARCHIVE_INDEX.generated.md').write_text('\n'.join(lines) + '\n')
    print('wrote ARCHIVE_INDEX.generated.md')


def sync_start_here(root: Path) -> None:
    state = load_state(root)
    start_here_path = root / 'START_HERE.md'
    rendered = render_generated_restart_mirror_block(state)
    updated = replace_generated_restart_mirror_block(start_here_path.read_text(), rendered)
    start_here_path.write_text(updated)
    print('synced START_HERE.md restart mirror family block')


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    sync_start_here(root)
    write_archive_index(root)


if __name__ == '__main__':
    main()
