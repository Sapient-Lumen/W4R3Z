#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_ROOT = Path(__file__).resolve().parent.parent

READ_FIRST = [
    'README.md',
    'STATUS.md',
    'MEMORY.md',
    'DECISIONS.md',
    'AGENTS.md',
    'TASKS.md',
    'PROJECT_MAP.md',
    '.llm/SESSION_START.md',
]

ACTIVE_TRACKS = [
    'chromium native messaging',
    'local broker socket',
    'side-panel operator surface',
    'persistent target-tab routing',
    'claude adapter',
    'support-truth backfill',
    'control-plane fused review',
    'navigation truth and history witnesses',
    'install/bootstrap receipts',
    'frozen support-surface snapshots',
    'opening contract conformance',
    'truth-surface lineage register',
    'current-root truth refresh',
    'revision receipts',
    'truth-surface warning ledger',
    'validation artifact buckets',
    'support bundle queue and publication holds',
    'published support surface and citable truth',
    'support bundle transition tooling',
    'support publish gate and head guards',
    'release manifest self-verification',
    'fixture lab',
    'playwright lab',
]

KNOWN_UNPROVEN = [
    'live Chromium native-messaging round-trip',
    'live Claude.ai DOM extraction against current UI',
    'CLI to browser request flow with a real extension ID',
    'selected-target routing in a real multi-tab session',
    'live before/after coverage proof for a dynamic content-script experiment',
]

NEXT_TASKS = [
    'capture one live logged-in Claude support bundle with route/history witness and before/after state',
    'promote or replace the held Claude support bundle once live official-surface proof exists',
    'keep SUPPORT-PUBLIC-SURFACE.json honest so citable support truth stays separate from held or candidate evidence',
    'keep validation artifact buckets honest as new capture families are added',
    'refresh support-bundle queue, support publish gate, truth-surface warnings, and revision receipt after meaningful archive changes',
]

ARCHIVE_NAME_RE = re.compile(r'^GlassTTY-rev(?P<revision>\d+)-(?P<stamp>\d{4}\.\d{2}\.\d{2}\.\d{2}\.\d{2})-(?P<slug>.+)$')


def _display_path(path: Path, *, root: Path = DEFAULT_ROOT) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def count_files(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for p in path.rglob('*') if p.is_file())


def normalize_archive_name(value: str | Path) -> str:
    raw = Path(value).name if isinstance(value, Path) else str(value).strip()
    if raw.endswith('.zip'):
        raw = raw[:-4]
    return Path(raw).name


def parse_archive_name(value: str | Path) -> dict[str, object]:
    name = normalize_archive_name(value)
    match = ARCHIVE_NAME_RE.match(name)
    parsed: dict[str, object] = {'archive_name': name}
    if not match:
        return parsed
    parsed['archive_revision'] = int(match.group('revision'))
    parsed['archive_created_at_from_name'] = match.group('stamp')
    parsed['archive_slug'] = match.group('slug')
    return parsed


def summarize_validation(path: Path, *, root: Path = DEFAULT_ROOT) -> dict[str, object]:
    if not path.exists():
        return {'exists': False}
    report_path = path / 'report.json'
    summary_md_path = path / 'SUMMARY.md'
    summary_json_path = path / 'summary.json'
    info: dict[str, object] = {
        'exists': True,
        'path': _display_path(path, root=root),
        'report_json': _display_path(report_path, root=root) if report_path.exists() else None,
        'summary_markdown': _display_path(summary_md_path, root=root) if summary_md_path.exists() else None,
        'summary_json': _display_path(summary_json_path, root=root) if summary_json_path.exists() else None,
    }
    if report_path.exists():
        try:
            report = json.loads(report_path.read_text(encoding='utf-8'))
        except Exception:
            report = None
        if isinstance(report, dict):
            info['overall_ok'] = report.get('ok')
            if isinstance(report.get('package_zip_proof'), dict):
                info['package_zip_proof'] = report['package_zip_proof']
            if 'package_zip_retained' in report:
                info['package_zip_retained'] = report.get('package_zip_retained')
            steps = report.get('steps')
            if isinstance(steps, list):
                info['step_count'] = len(steps)
                info['required_ok_count'] = sum(
                    1
                    for step in steps
                    if isinstance(step, dict)
                    and step.get('ok')
                    and step.get('required', True) is not False
                )
            return info
    if summary_json_path.exists():
        try:
            summary = json.loads(summary_json_path.read_text(encoding='utf-8'))
        except Exception:
            summary = None
        if isinstance(summary, dict):
            bool_checks = {
                key: value
                for key, value in summary.items()
                if isinstance(value, bool) and not key.endswith('_retained')
            }
            info['overall_ok'] = bool(bool_checks) and all(bool_checks.values())
            info['check_count'] = len(bool_checks)
            info['check_names'] = sorted(bool_checks)
            info['check_ok_count'] = sum(1 for value in bool_checks.values() if value)
            if isinstance(summary.get('package_zip'), str):
                info['package_zip'] = summary['package_zip']
            if isinstance(summary.get('package_zip_proof'), dict):
                info['package_zip_proof'] = summary['package_zip_proof']
            if 'package_zip_retained' in summary:
                info['package_zip_retained'] = summary.get('package_zip_retained')
            if isinstance(summary.get('resume_report'), str):
                info['resume_report'] = summary['resume_report']
            if isinstance(summary.get('resume_proof_summary'), str):
                info['resume_proof_summary'] = summary['resume_proof_summary']
    return info


def main() -> None:
    parser = argparse.ArgumentParser(description='Refresh GlassTTY archive manifest metadata')
    parser.add_argument('--root', default=str(DEFAULT_ROOT), help='Repo root to refresh; defaults to the script parent repo.')
    parser.add_argument('--revision', type=int, default=None)
    parser.add_argument('--summary', required=True)
    parser.add_argument('--codename', default='switchyard')
    parser.add_argument('--created-at', default=datetime.now(timezone.utc).isoformat())
    parser.add_argument('--archive-name', default=None, help='Archive identity to record, such as GlassTTY-rev0073-.... May be a .zip filename.')
    parser.add_argument('--base-archive', default=None, help='Newest audited baseline archive name')
    parser.add_argument('--ready-for-handoff', action='store_true', help='Mark the archive as handoff-ready after validation')
    parser.add_argument('--validation-dir', default='validation/latest', help='Validation directory to summarize in the manifest')
    args = parser.parse_args()

    root = Path(args.root).resolve()
    archive_identity_source = args.archive_name or root.name
    parsed_name = parse_archive_name(archive_identity_source)
    revision = args.revision if args.revision is not None else parsed_name.get('archive_revision')
    manifest: dict[str, Any] = {
        'project': 'GlassTTY',
        **parsed_name,
        'archive_revision': revision,
        'archive_created_at': args.created_at,
        'codename': args.codename,
        'summary': args.summary,
        'product_identity': 'local-first control plane for browser-native AI systems',
        'first_working_adapter_target': 'Claude.ai',
        'base_archive': args.base_archive,
        'ready_for_handoff': args.ready_for_handoff,
        'read_first': READ_FIRST,
        'active_tracks': ACTIVE_TRACKS,
        'known_unproven': KNOWN_UNPROVEN,
        'next_tasks': NEXT_TASKS,
        'worktree_name': root.name,
        'archive_identity_source': normalize_archive_name(archive_identity_source),
        'repo_counts': {
            'docs_files': count_files(root / 'docs'),
            'extension_files': count_files(root / 'extension'),
            'daemon_files': count_files(root / 'daemon'),
            'tests_files': count_files(root / 'tests'),
            'fixture_files': count_files(root / 'fixtures'),
            'validation_files': count_files(root / 'validation'),
        },
        'validation_summary': summarize_validation(root / args.validation_dir, root=root),
        'generated_by': 'scripts/refresh-archive.py',
    }

    target = root / 'ARCHIVE_MANIFEST.json'
    target.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print(target)


if __name__ == '__main__':
    main()
