#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Any

from plan_archive_revision_cut import build_plan, current_utc_minute_stamp

ROOT = Path(__file__).resolve().parents[2]
PARENT = ROOT.parent
CHANGELOG_NAME = 'CHANGELOG.md'
PRE_SETTLE_COMMAND = ['python3', 'scripts/tools/settle_archive_truth.py']
POST_RENAME_REFRESH_COMMANDS = [
    ['make', 'update-artifact-buckets'],
    ['make', 'update-archive-size-guardrail-card'],
    ['make', 'update-archive-byte-triage-card'],
    ['make', 'update-archive-size-guardrail-card'],
    ['make', 'update-archive-byte-triage-card'],
    ['make', 'update-archive-package-cut-card'],
    ['make', 'update-archive-reentry-card'],
    ['make', 'update-archive-handoff-pack'],
    ['make', 'update-archive-revision-cut-card'],
    ['make', 'update-archive-zip-lineage-card'],
    ['make', 'update-archive-zip-chronology-card'],
    ['make', 'update-archive-zip-authority-card'],
    ['make', 'update-archive-zip-digest-card'],
    ['make', 'update-archive-zip-size-truth-card'],
]
POST_RENAME_VALIDATE_COMMANDS = [
    ['make', 'test-archive-size-guardrail-card'],
    ['make', 'test-archive-byte-triage-card'],
    ['make', 'test-archive-package-cut-card'],
    ['make', 'test-archive-reentry-card'],
    ['make', 'test-archive-handoff-pack'],
    ['make', 'test-archive-handoff-pack-verify-tool'],
    ['make', 'test-archive-revision-cut-card'],
    ['make', 'test-archive-zip-lineage-card'],
    ['make', 'test-archive-zip-chronology-card'],
    ['make', 'test-archive-zip-authority-card'],
    ['make', 'test-archive-zip-digest-card'],
    ['make', 'test-authoritative-archive-zip-verify-tool'],
    ['make', 'test-archive-zip-size-truth-card'],
]


def _date_from_timestamp(timestamp: str) -> str:
    return timestamp[:10].replace('.', '-')


def _render_changelog_entry(next_revision: int, date: str, summary: str, notes: list[str]) -> str:
    bullets = [summary.strip(), *[note.strip() for note in notes if note.strip()]]
    lines = [f'## rev{next_revision:04d} - {date}', '']
    lines.extend(f'- {bullet}' for bullet in bullets)
    lines.append('')
    return '\n'.join(lines) + '\n'


def _append_changelog_entry(changelog_path: Path, entry: str) -> None:
    existing = changelog_path.read_text(encoding='utf-8')
    prefix = '' if existing.endswith('\n\n') or not existing else ('\n' if existing.endswith('\n') else '\n\n')
    changelog_path.write_text(existing + prefix + entry, encoding='utf-8')


def _run(command: list[str], cwd: Path) -> None:
    proc = subprocess.run(command, cwd=cwd, text=True, capture_output=True)
    if proc.stdout:
        print(proc.stdout, end='')
    if proc.stderr:
        print(proc.stderr, end='', file=sys.stderr)
    if proc.returncode != 0:
        raise SystemExit(f"cut-archive-revision: command failed: {' '.join(command)}")


def _build_zip(source_root: Path, zip_path: Path) -> None:
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(source_root.rglob('*')):
            if path.is_dir():
                continue
            arcname = path.relative_to(source_root.parent).as_posix()
            zf.write(path, arcname)


def _receipt(plan: dict[str, Any], zip_path: Path, pre_settle: bool, post_settle: bool) -> dict[str, Any]:
    return {
        'tool': 'cut_archive_revision',
        'current_root_name': ROOT.name,
        'current_revision_label': plan['current_archive']['revision_label'],
        'next_revision_label': plan['next_revision_label'],
        'next_root_name': plan['next_root_name'],
        'zip_path': zip_path.as_posix(),
        'pre_settle_enabled': pre_settle,
        'post_settle_enabled': post_settle,
        'pre_settle_command': ' '.join(PRE_SETTLE_COMMAND),
        'post_rename_refresh_commands': [' '.join(cmd) for cmd in POST_RENAME_REFRESH_COMMANDS],
        'post_rename_validate_commands': [' '.join(cmd) for cmd in POST_RENAME_VALIDATE_COMMANDS],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Cut the next Golden Rule archive revision: settle, rename, append changelog, refresh name-sensitive cards, and zip.')
    parser.add_argument('--descriptor', required=True, help='next revision descriptor slug')
    parser.add_argument('--summary', required=True, help='first changelog bullet for the new revision')
    parser.add_argument('--note', action='append', default=[], help='additional changelog bullet (repeatable)')
    parser.add_argument('--timestamp', default=None, help='UTC minute stamp in YYYY.MM.DD.HH.MM')
    parser.add_argument('--zip-dir', default=None, help='directory where the final zip should be written (default: parent of the archive root)')
    parser.add_argument('--dry-run', action='store_true', help='emit the planned rename/changelog/zip actions as JSON without mutating anything')
    parser.add_argument('--skip-pre-settle', action='store_true', help='do not run the canonical settle wrapper before the rename')
    parser.add_argument('--skip-post-settle', action='store_true', help='do not rerun the post-rename refresh/validation sequence before zipping')
    args = parser.parse_args()

    timestamp = args.timestamp or current_utc_minute_stamp()
    plan = build_plan(args.descriptor, timestamp, root_name=ROOT.name, changelog_path=ROOT / CHANGELOG_NAME)
    next_root = PARENT / plan['next_root_name']
    zip_dir = Path(args.zip_dir).expanduser().resolve() if args.zip_dir else PARENT
    zip_path = zip_dir / plan['next_zip_name']
    changelog_entry = _render_changelog_entry(plan['next_revision'], _date_from_timestamp(timestamp), args.summary, list(args.note))
    pre_settle = not args.skip_pre_settle
    post_settle = not args.skip_post_settle

    if args.dry_run:
        payload = _receipt(plan, zip_path, pre_settle, post_settle)
        payload['changelog_entry_preview'] = changelog_entry
        payload['zip_dir'] = zip_dir.as_posix()
        json.dump(payload, sys.stdout, indent=2)
        sys.stdout.write('\n')
        return 0

    if next_root.exists():
        raise SystemExit(f'cut-archive-revision: target root already exists: {next_root}')
    if zip_path.exists():
        raise SystemExit(f'cut-archive-revision: target zip already exists: {zip_path}')

    if pre_settle:
        _run(PRE_SETTLE_COMMAND, ROOT)

    shutil.move(ROOT.as_posix(), next_root.as_posix())
    _append_changelog_entry(next_root / CHANGELOG_NAME, changelog_entry)

    if post_settle:
        _run(PRE_SETTLE_COMMAND, next_root)
        for command in POST_RENAME_REFRESH_COMMANDS:
            _run(command, next_root)
        for command in POST_RENAME_VALIDATE_COMMANDS:
            _run(command, next_root)

    _build_zip(next_root, zip_path)

    json.dump(_receipt(plan, zip_path, pre_settle, post_settle), sys.stdout, indent=2)
    sys.stdout.write('\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
