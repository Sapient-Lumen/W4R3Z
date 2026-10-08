from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE_DIR = ROOT / 'validation' / 'latest'
DEFAULT_OUTPUT_DIR = DEFAULT_SOURCE_DIR / 'validate-release-capture'
DEFAULT_HISTORY_PATH = ROOT / 'validation' / 'validate-release-captures.json'


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding='utf-8'))


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')


def _copy_tree(src: Path, dst: Path) -> int:
    if not src.exists() or not src.is_dir():
        return 0
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    return sum(1 for item in dst.rglob('*') if item.is_file())


def _copy_file(src: Path, dst: Path) -> bool:
    if not src.exists() or not src.is_file():
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return True


def _safe_step_dict(step: Any) -> dict[str, Any] | None:
    return step if isinstance(step, dict) else None


def summarize_validate_release_report(report: dict[str, Any], *, source_dir: Path | None = None) -> dict[str, Any]:
    steps = [_safe_step_dict(step) for step in report.get('steps', [])]
    steps = [step for step in steps if step]
    running_step = report.get('running_step') if isinstance(report.get('running_step'), dict) else None
    first_failed = next((step for step in steps if step.get('required') and not step.get('ok')), None)
    timed_out = [step.get('name') for step in steps if step.get('timed_out') and isinstance(step.get('name'), str)]
    completed = [step for step in steps if step.get('ok') and isinstance(step.get('name'), str)]
    latest_completed = completed[-1].get('name') if completed else None
    planned_steps = [item for item in report.get('planned_steps', []) if isinstance(item, str)]
    selection = report.get('selection') if isinstance(report.get('selection'), dict) else {}
    out_dir = source_dir or Path(report.get('out_dir') or DEFAULT_SOURCE_DIR)
    summary = {
        'path': str(out_dir / 'report.json'),
        'exists': True,
        'timestamp': report.get('timestamp'),
        'ok': bool(report.get('ok')),
        'complete': bool(report.get('complete')),
        'resume_requested': bool(report.get('resume_requested')),
        'run_e2e_requested': bool(selection.get('run_e2e')),
        'start_at': selection.get('start_at'),
        'end_at': selection.get('end_at'),
        'planned_step_count': len(planned_steps),
        'planned_steps': planned_steps,
        'step_count': len(steps),
        'latest_completed_step': latest_completed,
        'running_step_name': running_step.get('name') if isinstance(running_step, dict) else None,
        'required_failed_step': first_failed.get('name') if isinstance(first_failed, dict) else None,
        'timed_out_steps': timed_out,
        'timed_out_step_count': len(timed_out),
        'package_zip_proof': report.get('package_zip_proof') if isinstance(report.get('package_zip_proof'), dict) else None,
        'resume_command': f'python scripts/validate-release.py --out-dir {out_dir.relative_to(ROOT)} --resume' if out_dir.is_relative_to(ROOT) else f'python scripts/validate-release.py --out-dir {out_dir} --resume',
    }
    focus = summary['running_step_name'] or summary['required_failed_step']
    if isinstance(focus, str) and focus:
        prefix = out_dir.relative_to(ROOT) if out_dir.is_relative_to(ROOT) else out_dir
        summary['focus_command'] = f'python scripts/validate-release.py --out-dir {prefix} --start-at {focus} --end-at {focus}'
    return summary


def summarize_report_file(source_dir: Path | None = None) -> dict[str, Any]:
    out_dir = source_dir or DEFAULT_SOURCE_DIR
    report_path = out_dir / 'report.json'
    if not report_path.exists():
        return {'path': str(report_path), 'exists': False, 'summary': None}
    report = _read_json(report_path)
    return {'path': str(report_path), 'exists': True, 'summary': summarize_validate_release_report(report, source_dir=out_dir)}


def _history_entries(path: Path) -> list[dict[str, Any]]:
    try:
        payload = _read_json(path)
    except Exception:
        return []
    entries = payload.get('entries') if isinstance(payload, dict) else None
    return [entry for entry in entries if isinstance(entry, dict)] if isinstance(entries, list) else []


def summarize_capture_history(path: Path | None = None) -> dict[str, Any]:
    history_path = path or DEFAULT_HISTORY_PATH
    entries = _history_entries(history_path)
    payload = _read_json(history_path) if history_path.exists() else None
    latest = entries[-1] if entries else None
    return {
        'path': str(history_path),
        'exists': history_path.exists(),
        'capture_count': len(entries),
        'latest_capture': latest,
        'history': payload,
    }


TRACKED_FIELDS = (
    'ok',
    'complete',
    'running_step_name',
    'required_failed_step',
    'timed_out_step_count',
    'latest_completed_step',
    'planned_step_count',
    'step_count',
)


def _comparison_to_previous(previous: dict[str, Any] | None, current: dict[str, Any]) -> dict[str, Any]:
    comparison: dict[str, Any] = {
        'has_previous_capture': isinstance(previous, dict),
        'previous_captured_at': previous.get('captured_at') if isinstance(previous, dict) else None,
        'current_captured_at': current.get('captured_at'),
        'changed_fields': [],
    }
    if not isinstance(previous, dict):
        comparison['summary'] = 'no previous validate-release capture exists yet'
        return comparison
    for key in TRACKED_FIELDS:
        before = previous.get(key)
        after = current.get(key)
        changed = before != after
        comparison[f'{key}_before'] = before
        comparison[f'{key}_after'] = after
        comparison[f'{key}_changed'] = changed
        if changed:
            comparison['changed_fields'].append(key)
    comparison['summary'] = 'validate-release drift detected' if comparison['changed_fields'] else 'validate-release capture matches the previous one on tracked fields'
    return comparison


def _history_payload(entries: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        'schema_version': 1,
        'updated_at': utc_now_iso(),
        'capture_count': len(entries),
        'entries': entries,
    }


def _update_history(current: dict[str, Any], *, path: Path) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    entries = _history_entries(path)
    previous = entries[-1] if entries else None
    entries.append(current)
    payload = _history_payload(entries)
    _write_json(path, payload)
    return {
        'path': str(path),
        'capture_count_after_write': len(entries),
        'latest_capture': current,
        'previous_capture': previous,
        'history': payload,
    }


def _capture_entry(bundle: dict[str, Any], *, output_dir: Path) -> dict[str, Any]:
    summary = bundle.get('validation_summary') if isinstance(bundle.get('validation_summary'), dict) else {}
    captured_files = bundle.get('captured_files') if isinstance(bundle.get('captured_files'), dict) else {}
    return {
        'captured_at': bundle.get('captured_at'),
        'output_dir': str(output_dir),
        'bundle_summary_path': str(output_dir / 'bundle-summary.json'),
        'summary_markdown_path': str(output_dir / 'SUMMARY.md'),
        'report_path': summary.get('path'),
        'ok': summary.get('ok'),
        'complete': summary.get('complete'),
        'running_step_name': summary.get('running_step_name'),
        'required_failed_step': summary.get('required_failed_step'),
        'timed_out_step_count': summary.get('timed_out_step_count'),
        'timed_out_steps': summary.get('timed_out_steps'),
        'latest_completed_step': summary.get('latest_completed_step'),
        'planned_step_count': summary.get('planned_step_count'),
        'step_count': summary.get('step_count'),
        'resume_command': summary.get('resume_command'),
        'focus_command': summary.get('focus_command'),
        'steps_file_count': captured_files.get('steps_file_count'),
        'copied': captured_files,
    }


def _write_summary_markdown(bundle: dict[str, Any], *, output_dir: Path) -> Path:
    summary = bundle.get('validation_summary') if isinstance(bundle.get('validation_summary'), dict) else {}
    history_update = bundle.get('history_update') if isinstance(bundle.get('history_update'), dict) else {}
    comparison = bundle.get('comparison_to_previous') if isinstance(bundle.get('comparison_to_previous'), dict) else {}
    lines = [
        '# validate-release capture summary',
        '',
        f"- captured_at: {bundle.get('captured_at')}",
        f"- report_ok: {summary.get('ok')}",
        f"- report_complete: {summary.get('complete')}",
        f"- running_step_name: {summary.get('running_step_name')}",
        f"- required_failed_step: {summary.get('required_failed_step')}",
        f"- timed_out_step_count: {summary.get('timed_out_step_count')}",
        f"- latest_completed_step: {summary.get('latest_completed_step')}",
        f"- capture_history_count: {history_update.get('capture_count_after_write')}",
        f"- comparison_summary: {comparison.get('summary')}",
        '',
        '## commands',
        '',
        f"- resume: `{summary.get('resume_command')}`",
    ]
    if summary.get('focus_command'):
        lines.append(f"- focus: `{summary.get('focus_command')}`")
    lines.extend([
        '',
        '## copied files',
        '',
        f"- report_json: {bundle.get('captured_files', {}).get('report_json')}",
        f"- summary_md: {bundle.get('captured_files', {}).get('summary_md')}",
        f"- current_step_json: {bundle.get('captured_files', {}).get('current_step_json')}",
        f"- steps_file_count: {bundle.get('captured_files', {}).get('steps_file_count')}",
        '',
        '## tracked drift',
        '',
        f"- changed_fields: {', '.join(comparison.get('changed_fields') or []) if comparison.get('changed_fields') else '(none)'}",
    ])
    path = output_dir / 'SUMMARY.md'
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return path


def capture_validate_release(*, source_dir: Path = DEFAULT_SOURCE_DIR, output_dir: Path = DEFAULT_OUTPUT_DIR, history_path: Path = DEFAULT_HISTORY_PATH) -> dict[str, Any]:
    report_path = source_dir / 'report.json'
    if not report_path.exists():
        raise FileNotFoundError(f'validate-release report does not exist: {report_path}')
    report = _read_json(report_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    captured_files = {
        'report_json': _copy_file(source_dir / 'report.json', output_dir / 'report.json'),
        'summary_md': _copy_file(source_dir / 'SUMMARY.md', output_dir / 'SUMMARY.md.source'),
        'current_step_json': _copy_file(source_dir / 'current_step.json', output_dir / 'current_step.json'),
        'steps_file_count': _copy_tree(source_dir / 'steps', output_dir / 'steps'),
    }
    bundle = {
        'captured_at': utc_now_iso(),
        'source_dir': str(source_dir),
        'output_dir': str(output_dir),
        'validation_summary': summarize_validate_release_report(report, source_dir=source_dir),
        'captured_files': captured_files,
    }
    entry = _capture_entry(bundle, output_dir=output_dir)
    history_update = _update_history(entry, path=history_path)
    comparison = _comparison_to_previous(history_update.get('previous_capture'), entry)
    bundle['history_update'] = history_update
    bundle['comparison_to_previous'] = comparison
    _write_json(output_dir / 'bundle-summary.json', bundle)
    _write_json(output_dir / 'capture-history.json', history_update)
    _write_json(output_dir / 'capture-diff.json', comparison)
    _write_summary_markdown(bundle, output_dir=output_dir)
    return bundle


def main() -> None:
    parser = argparse.ArgumentParser(description='Freeze validate-release output into a durable bundle and history ledger.')
    subparsers = parser.add_subparsers(dest='command')

    history_parser = subparsers.add_parser('history', help='Show validate-release capture history')
    history_parser.add_argument('--history-path', default=str(DEFAULT_HISTORY_PATH))
    history_parser.add_argument('--pretty', action='store_true')

    parser.add_argument('--source-dir', default=str(DEFAULT_SOURCE_DIR))
    parser.add_argument('--output-dir', default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument('--history-path', default=str(DEFAULT_HISTORY_PATH))
    parser.add_argument('--pretty', action='store_true')
    args = parser.parse_args()

    if args.command == 'history':
        payload = summarize_capture_history(Path(args.history_path))
        print(json.dumps(payload, indent=2 if args.pretty else None))
        return

    bundle = capture_validate_release(source_dir=Path(args.source_dir), output_dir=Path(args.output_dir), history_path=Path(args.history_path))
    print(json.dumps(bundle, indent=2 if args.pretty else None))


if __name__ == '__main__':
    main()
