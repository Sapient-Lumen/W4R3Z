#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tempfile
from typing import Any, Iterable

sys.dont_write_bytecode = True

from publication_rights_gate import assert_publication_rights_ready

ROOT = Path(__file__).resolve().parent.parent
QUEUE_MAP = {'candidate': 'candidates', 'hold': 'hold', 'published_ready': 'published_ready', 'published': 'published'}
DATE_RE = re.compile(r'^\d{4}-\d{2}-\d{2}$')
SAFE_ID_RE = re.compile(r'^[A-Za-z0-9][A-Za-z0-9._:-]{0,180}$')
MAX_RELEASE_SLUG_BYTES = 160
QUEUE_REL_ROOT = "release_queue"


def fail(msg: str) -> None:
    print(f"publish-queue-item: FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def _path_parts_relative_to_root(path: Path) -> tuple[str, ...] | None:
    try:
        return path.relative_to(ROOT).parts
    except ValueError:
        try:
            return path.resolve(strict=False).relative_to(ROOT.resolve()).parts
        except ValueError:
            return None


def first_symlink_component(path: Path) -> Path | None:
    """Return the first symlink component for a ROOT-confined path, if any."""
    parts = _path_parts_relative_to_root(path)
    if parts is None:
        return path if path.is_symlink() else None
    cursor = ROOT
    if ROOT.is_symlink():
        return ROOT
    for part in parts:
        cursor = cursor / part
        if cursor.is_symlink():
            return cursor
    return None


def fail_on_symlink_path(path: Path, field: str) -> None:
    symlink = first_symlink_component(path)
    if symlink is not None:
        try:
            rel = symlink.relative_to(ROOT).as_posix()
        except ValueError:
            rel = str(symlink)
        fail(f'{field} resolves through a symlink component: {rel}')


def load_json(path: Path):
    fail_on_symlink_path(path, f'JSON input {path}')
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception as exc:
        fail(f"invalid JSON in {path}: {exc}")


def slugify(s: str) -> str:
    out = []
    prev_dash = False
    for ch in s.lower():
        if ch.isalnum():
            out.append(ch)
            prev_dash = False
        elif not prev_dash:
            out.append('-')
            prev_dash = True
    slug = ''.join(out).strip('-') or 'release'
    # Keep path components comfortably below common filesystem limits while
    # preserving deterministic behavior for long operator-supplied labels.
    return slug.encode('utf-8')[:MAX_RELEASE_SLUG_BYTES].decode('utf-8', errors='ignore').strip('-') or 'release'


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    fail_on_symlink_path(path, f'SHA-256 input {path}')
    return sha256_bytes(path.read_bytes())


def require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value:
        fail(f'{field} must be a non-empty string')
    return value


def validate_iso_date(value: Any, field: str = 'date') -> str:
    text = require_string(value, field)
    if not DATE_RE.match(text):
        fail(f'{field} must be YYYY-MM-DD, got {text!r}')
    return text


def validate_safe_identifier(value: Any, field: str) -> str:
    text = require_string(value, field)
    if not SAFE_ID_RE.match(text):
        fail(f'{field} contains unsafe characters: {text!r}')
    return text


def clean_relative_archive_path(value: Any, field: str) -> str:
    """Validate a metadata path as a portable archive-relative POSIX path."""
    text = require_string(value, field)
    if '\x00' in text or '\\' in text:
        fail(f'{field} must be a clean POSIX relative archive path: {text!r}')
    pure = PurePosixPath(text)
    if pure.is_absolute():
        fail(f'{field} must not be absolute: {text!r}')
    parts = pure.parts
    if not parts or any(part in {'', '.', '..'} for part in parts):
        fail(f'{field} must not contain empty, dot, or parent components: {text!r}')
    return pure.as_posix()


def archive_file_path(rel: Any, field: str, *, must_exist: bool = True) -> Path:
    """Return a ROOT-confined file path and reject traversal/symlink boundaries."""
    clean = clean_relative_archive_path(rel, field)
    root_resolved = ROOT.resolve()
    candidate = ROOT.joinpath(*PurePosixPath(clean).parts)
    fail_on_symlink_path(candidate, field)
    resolved = candidate.resolve(strict=False)
    try:
        resolved.relative_to(root_resolved)
    except ValueError:
        fail(f'{field} escapes archive root: {clean}')
    if must_exist and not candidate.is_file():
        fail(f'{field} does not name an existing regular file: {clean}')
    return candidate


def prepare_publication_output_path(path: Path, field: str) -> None:
    """Reject output destinations outside ROOT or through symlinked parents.

    Input readers already reject traversal and symlink boundaries.  Public release
    writers need the same check at the write helper itself because callers can
    construct paths directly from ROOT (for example published/releases/*.json).
    The check is repeated after directory creation so a pre-existing symlinked
    parent cannot redirect same-directory temporary files outside the archive.
    """
    if _path_parts_relative_to_root(path) is None:
        fail(f'{field} publication output path escapes archive root: {path}')
    fail_on_symlink_path(path, field)
    if path.exists() and path.is_dir():
        fail(f'{field} publication output path is a directory: {path}')
    if path.parent.exists() and not path.parent.is_dir():
        fail(f'{field} publication output parent is not a directory: {path.parent}')


def validate_public_paths(public_paths: Any) -> list[str]:
    if not isinstance(public_paths, list) or not public_paths:
        fail('decision.public_paths must be a non-empty list for publication')
    clean: list[str] = []
    seen: set[str] = set()
    duplicates: list[str] = []
    for idx, rel in enumerate(public_paths):
        path = clean_relative_archive_path(rel, f'decision.public_paths[{idx}]')
        if path in seen:
            duplicates.append(path)
        seen.add(path)
        clean.append(path)
    if duplicates:
        fail('decision.public_paths contains duplicate entries: ' + ', '.join(sorted(set(duplicates))[:10]))
    return clean


def validate_public_paths_against_snapshot(public_paths: list[str], snapshot_data: dict[str, Any]) -> None:
    """Bind queue authorization to the public-surface snapshot payload.

    The release record must not claim paths absent from the snapshot, and the
    snapshot must not digest public entry-point payloads that the queue decision
    did not authorize.  The source manifest is recorded separately and may be
    listed in decision.public_paths, but every snapshot entry_point is treated as
    publication content requiring explicit decision coverage.
    """
    entries = snapshot_data.get('entry_points')
    if not isinstance(entries, list):
        fail('public surface snapshot entry_points must be a list')
    snapshot_entry_paths: list[str] = []
    seen_snapshot: set[str] = set()
    duplicate_snapshot: list[str] = []
    for idx, entry in enumerate(entries):
        if not isinstance(entry, dict):
            fail(f'public surface snapshot entry_points[{idx}] must be an object')
        path = clean_relative_archive_path(entry.get('path'), f'public surface snapshot entry_points[{idx}].path')
        if path in seen_snapshot:
            duplicate_snapshot.append(path)
        seen_snapshot.add(path)
        snapshot_entry_paths.append(path)
    source_manifest = snapshot_data.get('source_manifest')
    snapshot_claimable_paths = set(snapshot_entry_paths)
    if source_manifest is not None:
        manifest_path = clean_relative_archive_path(source_manifest, 'public surface snapshot source_manifest')
        if manifest_path in seen_snapshot:
            duplicate_snapshot.append(manifest_path)
        snapshot_claimable_paths.add(manifest_path)
    if duplicate_snapshot:
        fail('published/PUBLIC_SURFACE.json contains duplicate entry paths: ' + ', '.join(sorted(set(duplicate_snapshot))[:10]))
    missing = sorted(set(public_paths) - snapshot_claimable_paths)
    if missing:
        fail('decision.public_paths absent from published/PUBLIC_SURFACE.json snapshot: ' + ', '.join(missing[:10]))
    unauthorized_entries = sorted(set(snapshot_entry_paths) - set(public_paths))
    if unauthorized_entries:
        fail('published/PUBLIC_SURFACE.json snapshot contains entry paths not authorized by decision.public_paths: ' + ', '.join(unauthorized_entries[:10]))


def validate_queue_item(item: dict[str, Any]) -> tuple[str, str, str]:
    if not isinstance(item, dict):
        fail('queue item must be a JSON object')
    item_id = validate_safe_identifier(item.get('item_id'), 'queue_item.item_id')
    date = validate_iso_date(item.get('date'), 'queue_item.date')
    decision_id = validate_safe_identifier(item.get('decision_id'), 'queue_item.decision_id')
    return item_id, date, decision_id


def validate_decision(decision: dict[str, Any], expected_decision_id: str) -> list[str]:
    if not isinstance(decision, dict):
        fail('decision must be a JSON object')
    decision_id = validate_safe_identifier(decision.get('decision_id'), 'decision.decision_id')
    if decision_id != expected_decision_id:
        fail(f'decision_id mismatch: queue item expects {expected_decision_id}, decision file declares {decision_id}')
    if decision.get('status') != 'publish':
        fail('queue item decision must have status publish')
    return validate_public_paths(decision.get('public_paths', []))


def fsync_directory(path: Path) -> None:
    """Best-effort fsync for a directory entry update on POSIX filesystems."""
    try:
        fd = os.open(path, os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(fd)
    except OSError:
        # Some platforms/filesystems do not support directory fsync.  The file
        # payload has still been fsynced; keep publication behavior portable.
        pass
    finally:
        os.close(fd)


def atomic_write_bytes(path: Path, payload: bytes, *, overwrite: bool = True) -> None:
    """Write bytes through a same-directory temporary file.

    When overwrite is false, publish paths are created with a no-clobber
    hard-link commit so a concurrent publisher cannot overwrite a release output
    after the pre-existence check.  The temporary file is fully written and
    fsynced before it becomes visible at the final path.
    """
    prepare_publication_output_path(path, 'atomic output')
    path.parent.mkdir(parents=True, exist_ok=True)
    prepare_publication_output_path(path, 'atomic output')
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    tmp_path = Path(tmp_name)
    committed = False
    try:
        with os.fdopen(fd, "wb") as f:
            os.fchmod(f.fileno(), 0o644)
            f.write(payload)
            f.flush()
            os.fsync(f.fileno())
        if overwrite:
            os.replace(tmp_path, path)
            committed = True
        else:
            try:
                os.link(tmp_path, path)
            except FileExistsError:
                raise FileExistsError(f"target already exists: {path}")
            committed = True
        fsync_directory(path.parent)
    finally:
        if tmp_path.exists():
            tmp_path.unlink()
        if committed:
            fsync_directory(path.parent)


def atomic_write_text(path: Path, text: str, *, overwrite: bool = True) -> None:
    atomic_write_bytes(path, text.encode("utf-8"), overwrite=overwrite)


def remove_created_outputs(paths: list[Path]) -> None:
    """Best-effort cleanup after a post-write publication transition failure."""
    for path in paths:
        try:
            if path.exists():
                path.unlink()
        except OSError:
            pass


def release_field_line(label: str, value: object) -> str:
    text = '' if value is None else str(value)
    return f"- {label}: `{text}`" if text else f"- {label}:"


def render_public_release_markdown(data: dict) -> str:
    """Render the canonical human companion for a public release record."""
    lines = [
        '# Public release',
        '',
        release_field_line('Release ID', data.get('release_id')),
        release_field_line('Date', data.get('date')),
        release_field_line('Status', data.get('status')),
        release_field_line('Decision', data.get('decision_id')),
        release_field_line('Queue item', data.get('queue_item_id')),
        release_field_line('Revision', data.get('revision')),
        release_field_line('Public surface manifest', data.get('public_surface_manifest')),
        release_field_line('Public surface manifest sha256', data.get('public_surface_manifest_sha256')),
        release_field_line('Public surface snapshot', data.get('public_surface_snapshot')),
        release_field_line('Public surface snapshot sha256', data.get('public_surface_snapshot_sha256')),
        '',
        '## Summary',
        data.get('summary', ''),
        '',
        '## Public paths',
    ]
    public_paths = data.get('public_paths', [])
    if public_paths:
        lines.extend(f'- `{rel}`' for rel in public_paths)
    else:
        lines.append('-')
    lines.extend([
        '',
        '## Public surface snapshot',
        f"- `{data.get('public_surface_snapshot', '')}`",
        '',
        '## Release artifact',
        f"- `{data.get('artifact_zip', '')}`",
        f"- `{data.get('artifact_manifest', '')}`",
        '',
        '## Archive note',
        data.get('archive_note', ''),
    ])
    return '\n'.join(lines) + '\n'


def iter_queue_state_json_files(dirname: str) -> Iterable[Path]:
    validate_safe_identifier(dirname, 'queue state directory')
    state_dir = ROOT / QUEUE_REL_ROOT / dirname
    fail_on_symlink_path(state_dir, f'{QUEUE_REL_ROOT}/{dirname}')
    if not state_dir.exists():
        return []
    if not state_dir.is_dir():
        fail(f'{QUEUE_REL_ROOT}/{dirname} is not a directory')
    paths = sorted(state_dir.glob('*.json'))
    for path in paths:
        fail_on_symlink_path(path, f'queue state item {path.name}')
    return paths


def iter_decision_json_files() -> Iterable[Path]:
    decision_dir = ROOT / QUEUE_REL_ROOT / 'decisions'
    fail_on_symlink_path(decision_dir, f'{QUEUE_REL_ROOT}/decisions')
    if not decision_dir.exists():
        return []
    if not decision_dir.is_dir():
        fail(f'{QUEUE_REL_ROOT}/decisions is not a directory')
    paths = sorted(decision_dir.glob('*.json'))
    for path in paths:
        fail_on_symlink_path(path, f'decision file {path.name}')
    return paths


def find_item(name: str):
    validate_safe_identifier(name, 'item argument')
    for state, dirname in QUEUE_MAP.items():
        for path in iter_queue_state_json_files(dirname):
            if path.stem == name:
                return state, path
            data = load_json(path)
            if data.get('item_id') == name:
                return state, path
    fail(f"queue item not found: {name}")


def latest_revision() -> str:
    changelog = ROOT / 'CHANGELOG.md'
    fail_on_symlink_path(changelog, 'CHANGELOG.md')
    text = changelog.read_text(encoding='utf-8')
    m = re.search(r'^## (rev[0-9]{4})\b', text, re.M)
    if not m:
        fail('could not determine latest revision from CHANGELOG.md')
    return m.group(1)


def build_public_surface_snapshot(release_id: str, date: str, revision: str):
    """Build the public-surface snapshot object without writing it.

    `publish_queue_item.py --dry-run` is an operator preview mode, so it must
    not create snapshot files.  Keep byte construction separate from emission so
    the dry-run and write paths share the same SHA-256 calculation.
    """
    public_surface_path = archive_file_path('published/PUBLIC_SURFACE.json', 'public_surface_manifest')
    public_surface = load_json(public_surface_path)
    if not isinstance(public_surface, dict):
        fail('published/PUBLIC_SURFACE.json must be a JSON object')
    entry_points = public_surface.get('entry_points')
    if not isinstance(entry_points, list):
        fail('published/PUBLIC_SURFACE.json entry_points must be a list')
    rel = f'published/releases/snapshots/{release_id}.surface.json'
    clean_relative_archive_path(rel, 'public_surface_snapshot')
    entries = []
    for idx, entry in enumerate(entry_points):
        if not isinstance(entry, dict):
            fail(f'public_surface.entry_points[{idx}] must be a JSON object')
        entry_rel = clean_relative_archive_path(entry.get('path'), f'public_surface.entry_points[{idx}].path')
        src = archive_file_path(entry_rel, f'public_surface.entry_points[{idx}].path')
        role = require_string(entry.get('role'), f'public_surface.entry_points[{idx}].role')
        payload = src.read_bytes()
        entries.append({
            'path': entry_rel,
            'role': role,
            'sha256': sha256_bytes(payload),
            'size_bytes': len(payload),
        })
    data = {
        'owner': 'published/releases/snapshots/',
        'release_id': validate_safe_identifier(release_id, 'release_id'),
        'date': validate_iso_date(date, 'release date'),
        'revision': validate_safe_identifier(revision, 'revision'),
        'source_manifest': 'published/PUBLIC_SURFACE.json',
        'source_manifest_sha256': sha256_file(public_surface_path),
        'manifest_version': public_surface.get('version'),
        'entry_points': entries,
        'canonical_context': public_surface.get('canonical_context'),
        'principles': public_surface.get('principles'),
    }
    return rel, data, data['source_manifest_sha256']


def public_surface_snapshot_bytes(data: dict) -> bytes:
    return (json.dumps(data, indent=2) + '\n').encode('utf-8')


def write_public_surface_snapshot(rel: str, payload: bytes) -> None:
    target = archive_file_path(rel, 'public_surface_snapshot', must_exist=False)
    atomic_write_bytes(target, payload, overwrite=False)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--item', required=True, help='basename or queue item id in published_ready')
    ap.add_argument('--release-slug', required=True)
    ap.add_argument('--summary', default='')
    ap.add_argument('--archive-note', default='')
    ap.add_argument('--owner', default='EvidenceVault publishing pass')
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    assert_publication_rights_ready(ROOT, 'publish-queue-item')

    state, path = find_item(args.item)
    if state != 'published_ready':
        fail('queue item must currently be in published_ready state')
    item = load_json(path)
    item_id, item_date, decision_id = validate_queue_item(item)

    decision_path = ROOT / QUEUE_REL_ROOT / 'decisions' / f'{path.stem}.json'
    if decision_path.exists():
        fail_on_symlink_path(decision_path, f'decision file {decision_path.name}')
    else:
        decision_path = None
        for cand in iter_decision_json_files():
            data = load_json(cand)
            if data.get('decision_id') == decision_id:
                decision_path = cand
                break
        if decision_path is None:
            fail(f'could not locate decision for {decision_id}')
    decision = load_json(decision_path)
    public_paths = validate_decision(decision, decision_id)

    slug = slugify(args.release_slug)
    release_id = validate_safe_identifier(f"EV-PUB-{item_date}-{slug}", 'release_id')
    basename = f"{item_date}-{slug}"
    clean_relative_archive_path(f'published/releases/{basename}.json', 'release_json_path')
    clean_relative_archive_path(f'published/releases/{basename}.md', 'release_markdown_path')
    record_json = ROOT / 'published' / 'releases' / f'{basename}.json'
    record_md = ROOT / 'published' / 'releases' / f'{basename}.md'
    if record_json.exists() or record_md.exists():
        fail(f'public release already exists: {basename}')

    revision = latest_revision()
    snapshot_rel, snapshot_data, manifest_sha = build_public_surface_snapshot(release_id, item_date, revision)
    validate_public_paths_against_snapshot(public_paths, snapshot_data)
    snapshot_path = ROOT / snapshot_rel
    if snapshot_path.exists():
        fail(f'public release snapshot already exists: {snapshot_rel}')
    snapshot_payload = public_surface_snapshot_bytes(snapshot_data)
    snapshot_sha = sha256_bytes(snapshot_payload)
    summary = args.summary or decision.get('summary') or item.get('summary') or f'Publish {release_id}.'
    archive_note = args.archive_note or 'This public release is a stable surface, not a mirror of the full working archive.'
    record = {
        'release_id': release_id,
        'date': item_date,
        'status': 'published',
        'revision': revision,
        'decision_id': decision_id,
        'queue_item_id': item_id,
        'public_surface_manifest': 'published/PUBLIC_SURFACE.json',
        'public_surface_manifest_sha256': manifest_sha,
        'public_surface_snapshot': snapshot_rel,
        'public_surface_snapshot_sha256': snapshot_sha,
        'public_paths': public_paths,
        'summary': summary,
        'notes_path': record_md.relative_to(ROOT).as_posix(),
        'archive_note': archive_note,
        'artifact_manifest': f'published/releases/artifacts/{release_id}.bundle.json',
        'artifact_zip': f'published/releases/artifacts/{release_id}.zip',
    }
    rendered_markdown = render_public_release_markdown(record)

    if args.dry_run:
        print(json.dumps(record, indent=2))
        return

    created_outputs: list[Path] = []
    try:
        write_public_surface_snapshot(snapshot_rel, snapshot_payload)
        created_outputs.append(snapshot_path)
        atomic_write_text(record_json, json.dumps(record, indent=2) + '\n', overwrite=False)
        created_outputs.append(record_json)
        atomic_write_text(record_md, rendered_markdown, overwrite=False)
        created_outputs.append(record_md)

        transition_script = archive_file_path('scripts/transition_queue_item.py', 'transition_queue_item')
        env = os.environ.copy()
        env['PYTHONDONTWRITEBYTECODE'] = '1'
        env['PYTHONUNBUFFERED'] = '1'
        subprocess.run([
            sys.executable, str(transition_script),
            '--item', item_id, '--to-state', 'published',
            '--decision-id', decision_id, '--public-release-id', release_id,
            '--next-action', 'Update only if a later public release supersedes this executed item.'
        ], cwd=ROOT, env=env, check=True)
    except subprocess.CalledProcessError as exc:
        remove_created_outputs(created_outputs)
        fail(f'queue transition failed after output writes; rolled back created outputs: {exc}')
    except Exception:
        remove_created_outputs(created_outputs)
        raise

    print(f"publish-queue-item: OK ({release_id})")


if __name__ == '__main__':
    main()
