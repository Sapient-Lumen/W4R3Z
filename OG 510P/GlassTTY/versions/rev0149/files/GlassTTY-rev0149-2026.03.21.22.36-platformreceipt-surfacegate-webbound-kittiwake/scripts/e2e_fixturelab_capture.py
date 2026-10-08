from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_ROOT = ROOT / 'validation' / 'latest'
DEFAULT_REPORT_PATH = DEFAULT_OUTPUT_ROOT / 'e2e-fixturelab.json'
DEFAULT_CAPTURE_OUTPUT_DIR = DEFAULT_OUTPUT_ROOT / 'e2e-fixturelab-capture'
DEFAULT_HISTORY_PATH = ROOT / 'validation' / 'e2e-fixturelab-captures.json'
COPY_CANDIDATE_SUFFIXES = (
    '.playwright-probe.png',
    '.playwright-trace.zip',
    '.setup-replay.sh',
    '.setup-ledger.json',
    '.setup-summary.md',
    '.stdout.json',
    '.stderr.log',
)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding='utf-8'))


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')


def history_path(root: Path | None = None) -> Path:
    repo_root = root or ROOT
    return repo_root / 'validation' / 'e2e-fixturelab-captures.json'


def report_path_default(root: Path | None = None) -> Path:
    repo_root = root or ROOT
    return repo_root / 'validation' / 'latest' / 'e2e-fixturelab.json'


def capture_output_default(root: Path | None = None) -> Path:
    repo_root = root or ROOT
    return repo_root / 'validation' / 'latest' / 'e2e-fixturelab-capture'


def _as_path(value: Any) -> Path | None:
    if isinstance(value, str) and value.strip():
        return Path(value).expanduser()
    return None



def browser_attempt_artifact_root(report_path: Path) -> Path:
    return report_path.with_name(f'{report_path.stem}.browser-attempts')



def summarize_browser_attempt_artifacts(report_path: Path, *, limit: int = 20) -> dict[str, Any]:
    root = browser_attempt_artifact_root(report_path)
    summary: dict[str, Any] = {
        'path': str(root),
        'exists': root.exists(),
        'attempt_dir_count': 0,
        'attempt_dirs': [],
        'diagnosis_categories': [],
        'latest_diagnosis': None,
        'profile_lock_attempt_count': 0,
    }
    if not root.exists():
        return summary
    try:
        children = sorted([child for child in root.iterdir() if child.is_dir()], key=lambda child: child.name)
    except Exception as exc:  # noqa: BLE001
        summary['read_error'] = str(exc)
        return summary
    summary['attempt_dir_count'] = len(children)
    diagnosis_categories: list[str] = []
    latest_diagnosis: dict[str, Any] | None = None
    profile_lock_attempt_count = 0
    for child in children[:limit]:
        entry: dict[str, Any] = {'name': child.name, 'path': str(child), 'attempt_json_path': str(child / 'attempt.json'), 'attempt_json_exists': (child / 'attempt.json').exists()}
        if entry['attempt_json_exists']:
            try:
                payload = _read_json(child / 'attempt.json')
            except Exception as exc:  # noqa: BLE001
                entry['read_error'] = str(exc)
            else:
                entry['stage'] = payload.get('stage')
                devtools = payload.get('devtools_active_port') if isinstance(payload.get('devtools_active_port'), dict) else {}
                entry['devtools_active_port_exists'] = bool(devtools.get('exists'))
                attempt = payload.get('attempt') if isinstance(payload.get('attempt'), dict) else {}
                entry['mode'] = attempt.get('mode')
                entry['interrupted'] = bool(attempt.get('interrupted'))
                diagnosis = payload.get('diagnosis') if isinstance(payload.get('diagnosis'), dict) else None
                if isinstance(diagnosis, dict):
                    entry['diagnosis_category'] = diagnosis.get('category')
                    entry['diagnosis_summary'] = diagnosis.get('summary')
                    entry['diagnosis_confidence'] = diagnosis.get('confidence')
                    entry['diagnosis_signature_tags'] = list(diagnosis.get('signature_tags') or [])
                    signals = diagnosis.get('signals') if isinstance(diagnosis.get('signals'), dict) else {}
                    entry['profile_lock_artifact_count'] = signals.get('profile_lock_artifact_count')
                    if diagnosis.get('category'):
                        diagnosis_categories.append(str(diagnosis['category']))
                    if 'profile-lock' in (diagnosis.get('signature_tags') or []) or (signals.get('profile_lock_artifact_count') or 0):
                        profile_lock_attempt_count += 1
                    latest_diagnosis = {
                        'attempt_dir': child.name,
                        'category': diagnosis.get('category'),
                        'summary': diagnosis.get('summary'),
                        'confidence': diagnosis.get('confidence'),
                        'signature_tags': list(diagnosis.get('signature_tags') or []),
                        'hints': list(diagnosis.get('hints') or []),
                    }
        summary['attempt_dirs'].append(entry)
    if len(children) > limit:
        summary['truncated'] = True
    summary['diagnosis_categories'] = diagnosis_categories
    summary['latest_diagnosis'] = latest_diagnosis
    summary['profile_lock_attempt_count'] = profile_lock_attempt_count
    return summary



def _playwright_trace_info(report: dict[str, Any]) -> dict[str, Any] | None:
    playwright = report.get('playwright') if isinstance(report.get('playwright'), dict) else None
    if not isinstance(playwright, dict):
        return None
    persistent = playwright.get('persistent') if isinstance(playwright.get('persistent'), dict) else None
    trace = persistent.get('trace') if isinstance(persistent, dict) and isinstance(persistent.get('trace'), dict) else None
    if not isinstance(trace, dict):
        trace = playwright.get('trace') if isinstance(playwright.get('trace'), dict) else None
    return trace if isinstance(trace, dict) else None


def _playwright_launch_summary(report: dict[str, Any]) -> dict[str, Any]:
    playwright = report.get('playwright') if isinstance(report.get('playwright'), dict) else {}
    persistent = playwright.get('persistent') if isinstance(playwright.get('persistent'), dict) else {}
    launch_plan = persistent.get('launch_plan') if isinstance(persistent.get('launch_plan'), dict) else playwright.get('launch_plan') if isinstance(playwright.get('launch_plan'), dict) else {}
    return {
        'strategy': persistent.get('launch_strategy') or launch_plan.get('strategy'),
        'skip_reason': launch_plan.get('skip_reason'),
        'risky_fallback': bool(persistent.get('risky_fallback') or launch_plan.get('risky_fallback')),
        'system_fallback_used': persistent.get('launch_strategy') == 'system-executable',
    }


def summarize_fixturelab_report(report: dict[str, Any], *, report_path: Path | None = None) -> dict[str, Any]:
    cdp = report.get('cdp') if isinstance(report.get('cdp'), dict) else {}
    native_bootstrap = report.get('native_bootstrap') if isinstance(report.get('native_bootstrap'), dict) else {}
    cli_proof = report.get('cli_proof') if isinstance(report.get('cli_proof'), dict) else {}
    probe_json = report.get('probe_json') if isinstance(report.get('probe_json'), dict) else {}
    extension_contexts = report.get('extension_contexts') if isinstance(report.get('extension_contexts'), dict) else {}
    trace = _playwright_trace_info(report) or {}
    launch = _playwright_launch_summary(report)
    playwright = report.get('playwright') if isinstance(report.get('playwright'), dict) else {}
    setup = report.get('setup') if isinstance(report.get('setup'), dict) else {}
    setup_actions = [item for item in (setup.get('actions') or []) if isinstance(item, dict)]
    setup_environment = setup.get('environment_fingerprint') if isinstance(setup.get('environment_fingerprint'), dict) else {}
    setup_next_action = setup.get('recommended_next_action') if isinstance(setup.get('recommended_next_action'), dict) else {}
    replay_script = _as_path(setup.get('replay_script_path'))
    setup_ledger = _as_path(setup.get('ledger_path'))
    setup_summary = _as_path(setup.get('summary_path'))
    browser_attempts = [item for item in (report.get('browser_attempts') or []) if isinstance(item, dict)]
    interrupted_browser_attempts = [item for item in browser_attempts if item.get('interrupted')]
    inflight = report.get('browser_attempt_inflight') if isinstance(report.get('browser_attempt_inflight'), dict) else {}
    service_worker_urls: list[str] = []
    for values in (playwright.get('service_worker_urls'), ((playwright.get('persistent') or {}).get('service_worker_urls') if isinstance(playwright.get('persistent'), dict) else None)):
        if isinstance(values, list):
            service_worker_urls.extend(str(item) for item in values if item)
    service_worker_seen = bool(cdp.get('service_worker_seen') or cdp.get('browser_service_worker_seen') or service_worker_urls or extension_contexts.get('background_context_seen'))
    extension_visible = bool(cdp.get('extension_visible') or cdp.get('extension_pages') or cdp.get('service_worker_seen') or cdp.get('browser_extension_pages') or cdp.get('browser_service_worker_seen') or extension_contexts.get('runtime_id_matches_extension'))
    attempt_artifacts = summarize_browser_attempt_artifacts(report_path) if report_path else {'path': None, 'exists': False, 'attempt_dir_count': 0, 'attempt_dirs': []}
    return {
        'report_path': str(report_path) if report_path else None,
        'report_timestamp': report.get('timestamp'),
        'finished_at': report.get('finished_at'),
        'phase': report.get('phase'),
        'ok': bool(report.get('ok')),
        'error': report.get('error'),
        'browser_mode_requested': report.get('browser_mode_requested'),
        'browser_mode_selected': report.get('browser_mode_selected'),
        'playwright_available': bool(playwright.get('available')),
        'playwright_launch': launch,
        'playwright_trace_requested_path': trace.get('requested_path'),
        'playwright_trace_saved': bool(trace.get('saved')),
        'playwright_trace_exists': bool(trace.get('exists')),
        'setup_action_count': len(setup_actions),
        'executed_setup_action_count': sum(1 for item in setup_actions if item.get('executed')),
        'failed_setup_action_count': sum(1 for item in setup_actions if item.get('executed') and item.get('ok') is False),
        'failed_setup_action_names': [str(item.get('name')) for item in setup_actions if item.get('executed') and item.get('ok') is False and item.get('name')],
        'last_setup_action_name': str(setup_actions[-1].get('name')) if setup_actions else None,
        'last_setup_action_state': (
            'executed-ok' if setup_actions and setup_actions[-1].get('executed') and setup_actions[-1].get('ok') else
            'executed-failed' if setup_actions and setup_actions[-1].get('executed') else
            'skipped' if setup_actions and setup_actions[-1].get('skipped') else
            'planned-only' if setup_actions else None
        ),
        'setup_replay_script_path': str(replay_script) if replay_script else None,
        'setup_replay_script_exists': bool(replay_script and replay_script.exists()),
        'setup_ledger_path': str(setup_ledger) if setup_ledger else None,
        'setup_ledger_exists': bool(setup_ledger and setup_ledger.exists()),
        'setup_summary_path': str(setup_summary) if setup_summary else None,
        'setup_summary_exists': bool(setup_summary and setup_summary.exists()),
        'setup_recommended_next_summary': setup_next_action.get('summary'),
        'setup_recommended_next_command': setup_next_action.get('command'),
        'setup_environment_browser_family': ((setup_environment.get('default_browser') or {}).get('browser_family') if isinstance(setup_environment.get('default_browser'), dict) else None),
        'setup_environment_playwright_browser_family': ((setup_environment.get('playwright_browser') or {}).get('browser_family') if isinstance(setup_environment.get('playwright_browser'), dict) else None),
        'setup_environment_playwright_channel_ready': setup_environment.get('playwright_channel_ready'),
        'setup_environment_cache_alignment_status': setup_environment.get('playwright_cache_alignment_status'),
        'setup_environment_native_host_targets': list(setup_environment.get('native_host_install_targets') or []) if isinstance(setup_environment.get('native_host_install_targets'), list) else None,
        'terminated': bool(report.get('terminated')),
        'terminated_signal': report.get('terminated_signal'),
        'browser_attempt_count': len(browser_attempts),
        'interrupted_browser_attempt_count': len(interrupted_browser_attempts),
        'last_browser_attempt_mode': browser_attempts[-1].get('mode') if browser_attempts else None,
        'last_browser_attempt_interrupted': bool(browser_attempts[-1].get('interrupted')) if browser_attempts else False,
        'browser_attempt_inflight_mode': inflight.get('mode'),
        'browser_attempt_artifact_root': attempt_artifacts.get('path'),
        'browser_attempt_artifact_root_exists': bool(attempt_artifacts.get('exists')),
        'browser_attempt_artifact_dir_count': attempt_artifacts.get('attempt_dir_count'),
        'browser_attempt_artifact_dirs': [item.get('name') for item in (attempt_artifacts.get('attempt_dirs') or []) if isinstance(item, dict)],
        'browser_attempt_diagnosis_categories': list(attempt_artifacts.get('diagnosis_categories') or []),
        'latest_browser_attempt_diagnosis': attempt_artifacts.get('latest_diagnosis'),
        'profile_lock_browser_attempt_count': attempt_artifacts.get('profile_lock_attempt_count'),
        'socket_exists_after_launch': bool(report.get('socket_exists_after_launch')),
        'native_oneshot_ok': bool(native_bootstrap.get('oneshot_ok')),
        'cli_proof_ok': bool(cli_proof.get('ok')),
        'cli_proof_skipped': bool(cli_proof.get('skipped')),
        'extension_visible': extension_visible,
        'service_worker_seen': service_worker_seen,
        'runtime_id_matches_extension': bool(extension_contexts.get('runtime_id_matches_extension')),
        'background_context_seen': bool(extension_contexts.get('background_context_seen')),
        'offscreen_context_seen': bool(extension_contexts.get('offscreen_context_seen')),
        'probe_ok': bool(probe_json.get('ok')),
        'probe_receiver_count': len(probe_json.get('receivers') or []) if isinstance(probe_json.get('receivers'), list) else None,
        'doctor_hint_count': len(report.get('doctor', {}).get('hints') or []) if isinstance(report.get('doctor'), dict) else None,
    }


def summarize_report_file(report_path: Path | None = None) -> dict[str, Any]:
    path = report_path or DEFAULT_REPORT_PATH
    if not path.exists():
        return {'path': str(path), 'exists': False, 'summary': None}
    report = _read_json(path)
    return {'path': str(path), 'exists': True, 'summary': summarize_fixturelab_report(report, report_path=path)}


def _artifact_candidates(report: dict[str, Any], *, report_path: Path) -> list[tuple[str, Path]]:
    candidates: list[tuple[str, Path]] = [('report', report_path)]
    seen: set[str] = {str(report_path.resolve())}
    attempt_root = browser_attempt_artifact_root(report_path)
    attempt_root_key = str(attempt_root.resolve())
    if attempt_root_key not in seen:
        candidates.append(('sibling-dir:browser-attempts', attempt_root))
        seen.add(attempt_root_key)
    for suffix in COPY_CANDIDATE_SUFFIXES:
        sibling = report_path.with_suffix(suffix)
        key = str(sibling.resolve())
        if key not in seen:
            candidates.append((f'sibling:{suffix.lstrip(".")}', sibling))
            seen.add(key)
    trace = _playwright_trace_info(report) or {}
    for label, value in (
        ('report_output_path', report.get('output_path')),
        ('playwright_trace', trace.get('requested_path')),
        ('playwright_screenshot', (report.get('playwright') or {}).get('screenshot_path') if isinstance(report.get('playwright'), dict) else None),
        ('persistent_screenshot', (((report.get('playwright') or {}).get('persistent') or {}).get('screenshot_path')) if isinstance((report.get('playwright') or {}).get('persistent'), dict) else None),
    ):
        path = _as_path(value)
        if path is None:
            continue
        resolved = str(path.resolve())
        if resolved in seen:
            continue
        candidates.append((label, path))
        seen.add(resolved)
    return candidates


def _copy_artifacts(report: dict[str, Any], *, report_path: Path, output_dir: Path) -> list[dict[str, Any]]:
    artifact_dir = output_dir / 'artifacts'
    artifact_dir.mkdir(parents=True, exist_ok=True)
    copied: list[dict[str, Any]] = []
    for kind, source in _artifact_candidates(report, report_path=report_path):
        target = artifact_dir / source.name
        entry: dict[str, Any] = {'kind': kind, 'source_path': str(source), 'copied_path': str(target), 'exists': source.exists(), 'copied': False}
        if source.exists() and source.is_file():
            shutil.copy2(source, target)
            entry['copied'] = True
            entry['size_bytes'] = target.stat().st_size
        elif source.exists() and source.is_dir():
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(source, target)
            entry['copied'] = True
            entry['copied_dir'] = True
            entry['entry_count'] = sum(1 for _ in target.rglob('*'))
        copied.append(entry)
    return copied


def _read_history(path: Path) -> dict[str, Any] | None:
    try:
        payload = _read_json(path)
    except FileNotFoundError:
        return None
    except Exception:
        return None
    return payload if isinstance(payload, dict) else None


def _history_entries(path: Path) -> list[dict[str, Any]]:
    payload = _read_history(path)
    entries = payload.get('entries') if isinstance(payload, dict) else None
    return [entry for entry in entries if isinstance(entry, dict)] if isinstance(entries, list) else []


def summarize_capture_history(path: Path | None = None) -> dict[str, Any]:
    history_file = path or DEFAULT_HISTORY_PATH
    payload = _read_history(history_file)
    entries = _history_entries(history_file)
    latest = entries[-1] if entries else None
    return {'path': str(history_file), 'exists': history_file.exists(), 'capture_count': len(entries), 'latest_capture': latest, 'history': payload}


TRACKED_FIELDS = (
    'ok',
    'phase',
    'browser_mode_selected',
    'terminated',
    'interrupted_browser_attempt_count',
    'latest_browser_attempt_diagnosis',
    'profile_lock_browser_attempt_count',
    'socket_exists_after_launch',
    'native_oneshot_ok',
    'cli_proof_ok',
    'cli_proof_skipped',
    'extension_visible',
    'service_worker_seen',
    'playwright_trace_saved',
)


def _comparison_to_previous(previous: dict[str, Any] | None, current: dict[str, Any]) -> dict[str, Any]:
    comparison: dict[str, Any] = {'has_previous_capture': isinstance(previous, dict), 'previous_captured_at': previous.get('captured_at') if isinstance(previous, dict) else None, 'current_captured_at': current.get('captured_at'), 'changed_fields': []}
    if not isinstance(previous, dict):
        comparison['summary'] = 'no previous fixture-lab capture exists yet'
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
    comparison['summary'] = 'fixture-lab smoke drift detected' if comparison['changed_fields'] else 'fixture-lab smoke capture matches the previous one on tracked fields'
    return comparison


def _history_payload(entries: list[dict[str, Any]]) -> dict[str, Any]:
    return {'schema_version': 1, 'updated_at': utc_now_iso(), 'capture_count': len(entries), 'entries': entries}


def _update_history(current: dict[str, Any], *, path: Path) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    entries = _history_entries(path)
    previous = entries[-1] if entries else None
    entries.append(current)
    payload = _history_payload(entries)
    _write_json(path, payload)
    return {'path': str(path), 'capture_count_after_write': len(entries), 'latest_capture': current, 'previous_capture': previous, 'history': payload}


def _capture_entry(bundle: dict[str, Any], *, output_dir: Path) -> dict[str, Any]:
    summary = bundle.get('smoke_summary') if isinstance(bundle.get('smoke_summary'), dict) else {}
    copied_artifacts = [item.get('kind') for item in (bundle.get('copied_artifacts') or []) if isinstance(item, dict) and item.get('copied')]
    launch = summary.get('playwright_launch') if isinstance(summary.get('playwright_launch'), dict) else {}
    return {
        'captured_at': bundle.get('captured_at'),
        'output_dir': str(output_dir),
        'bundle_summary_path': str(output_dir / 'bundle-summary.json'),
        'summary_markdown_path': str(output_dir / 'SUMMARY.md'),
        'report_path': summary.get('report_path'),
        'report_timestamp': summary.get('report_timestamp'),
        'ok': summary.get('ok'),
        'phase': summary.get('phase'),
        'browser_mode_selected': summary.get('browser_mode_selected'),
        'terminated': summary.get('terminated'),
        'terminated_signal': summary.get('terminated_signal'),
        'browser_attempt_count': summary.get('browser_attempt_count'),
        'interrupted_browser_attempt_count': summary.get('interrupted_browser_attempt_count'),
        'last_browser_attempt_mode': summary.get('last_browser_attempt_mode'),
        'last_browser_attempt_interrupted': summary.get('last_browser_attempt_interrupted'),
        'latest_browser_attempt_diagnosis': summary.get('latest_browser_attempt_diagnosis'),
        'profile_lock_browser_attempt_count': summary.get('profile_lock_browser_attempt_count'),
        'socket_exists_after_launch': summary.get('socket_exists_after_launch'),
        'native_oneshot_ok': summary.get('native_oneshot_ok'),
        'cli_proof_ok': summary.get('cli_proof_ok'),
        'cli_proof_skipped': summary.get('cli_proof_skipped'),
        'extension_visible': summary.get('extension_visible'),
        'service_worker_seen': summary.get('service_worker_seen'),
        'playwright_trace_saved': summary.get('playwright_trace_saved'),
        'playwright_launch_strategy': launch.get('strategy'),
        'playwright_risky_fallback': launch.get('risky_fallback'),
        'copied_artifacts': copied_artifacts,
    }


def _render_summary_markdown(bundle: dict[str, Any]) -> str:
    summary = bundle.get('smoke_summary') if isinstance(bundle.get('smoke_summary'), dict) else {}
    history = bundle.get('capture_history') if isinstance(bundle.get('capture_history'), dict) else {}
    comparison = bundle.get('comparison_to_previous_capture') if isinstance(bundle.get('comparison_to_previous_capture'), dict) else {}
    artifacts = [item for item in (bundle.get('copied_artifacts') or []) if isinstance(item, dict)]
    launch = summary.get('playwright_launch') if isinstance(summary.get('playwright_launch'), dict) else {}
    lines = [
        '# GlassTTY fixture-lab smoke capture',
        '',
        f"- captured_at: {bundle.get('captured_at')}",
        f"- report_path: {summary.get('report_path')}",
        f"- report_timestamp: {summary.get('report_timestamp')}",
        f"- ok: {summary.get('ok')}",
        f"- phase: {summary.get('phase')}",
        f"- browser_mode_selected: {summary.get('browser_mode_selected')}",
        f"- terminated: {summary.get('terminated')}",
        f"- terminated_signal: {summary.get('terminated_signal')}",
        f"- browser_attempt_count: {summary.get('browser_attempt_count')}",
        f"- interrupted_browser_attempt_count: {summary.get('interrupted_browser_attempt_count')}",
        f"- last_browser_attempt_mode: {summary.get('last_browser_attempt_mode')}",
        f"- last_browser_attempt_interrupted: {summary.get('last_browser_attempt_interrupted')}",
        f"- latest_browser_attempt_diagnosis: {((summary.get('latest_browser_attempt_diagnosis') or {}).get('summary') if isinstance(summary.get('latest_browser_attempt_diagnosis'), dict) else None)}",
        f"- latest_browser_attempt_diagnosis_category: {((summary.get('latest_browser_attempt_diagnosis') or {}).get('category') if isinstance(summary.get('latest_browser_attempt_diagnosis'), dict) else None)}",
        f"- profile_lock_browser_attempt_count: {summary.get('profile_lock_browser_attempt_count')}",
        f"- socket_exists_after_launch: {summary.get('socket_exists_after_launch')}",
        f"- native_oneshot_ok: {summary.get('native_oneshot_ok')}",
        f"- cli_proof_ok: {summary.get('cli_proof_ok')}",
        f"- extension_visible: {summary.get('extension_visible')}",
        f"- service_worker_seen: {summary.get('service_worker_seen')}",
        f"- playwright_launch_strategy: {launch.get('strategy')}",
        f"- playwright_risky_fallback: {launch.get('risky_fallback')}",
        f"- playwright_trace_saved: {summary.get('playwright_trace_saved')}",
        f"- setup_action_count: {summary.get('setup_action_count')}",
        f"- failed_setup_action_count: {summary.get('failed_setup_action_count')}",
        f"- setup_ledger_exists: {summary.get('setup_ledger_exists')}",
        f"- setup_summary_exists: {summary.get('setup_summary_exists')}",
        f"- capture_history_count: {history.get('capture_count_after_write')}",
        '',
        '## Capture history',
        '',
        f"- ledger_path: `{history.get('path')}`",
        f"- comparison_summary: {comparison.get('summary')}",
    ]
    if comparison.get('changed_fields'):
        lines.append(f"- changed_fields: {', '.join(str(item) for item in comparison.get('changed_fields') or [])}")
    lines.extend([
        '',
        '## Recommended commands',
        '',
        f"- capture_latest: `python scripts/e2e-fixturelab-capture.py --report {summary.get('report_path') or 'validation/latest/e2e-fixturelab.json'} --output-dir validation/latest/e2e-fixturelab-capture`",
        '- capture_history: `python scripts/e2e-fixturelab-capture.py history --pretty`',
        '',
        '## Copied artifacts',
        '',
    ])
    for item in artifacts:
        lines.append(f"- {item.get('kind')}: exists={item.get('exists')} copied={item.get('copied')} path=`{item.get('copied_path')}`")
    lines.extend([
        '',
        '## Bundle files',
        '',
        '- `bundle-summary.json`',
        '- `e2e-fixturelab-report.json`',
        '- `smoke-summary.json`',
        '- `smoke-history.json`',
        '- `smoke-diff.json`',
        '- `artifacts/`',
    ])
    if bundle.get('doctor') is not None:
        lines.append('- `doctor.json`')
    if bundle.get('probe_json') is not None:
        lines.append('- `probe-json.json`')
    if bundle.get('cli_proof') is not None:
        lines.append('- `cli-proof.json`')
    return '\n'.join(lines) + '\n'


def build_capture_bundle(*, report_path: Path | None = None, output_dir: Path | None = None, history_file: Path | None = None) -> dict[str, Any]:
    resolved_report_path = (report_path or DEFAULT_REPORT_PATH).resolve()
    if not resolved_report_path.exists():
        raise FileNotFoundError(f'fixture-lab report does not exist: {resolved_report_path}')
    resolved_output_dir = (output_dir or DEFAULT_CAPTURE_OUTPUT_DIR).resolve()
    resolved_output_dir.mkdir(parents=True, exist_ok=True)
    history_target = (history_file or DEFAULT_HISTORY_PATH).resolve()
    report = _read_json(resolved_report_path)
    smoke_summary = summarize_fixturelab_report(report, report_path=resolved_report_path)
    copied_artifacts = _copy_artifacts(report, report_path=resolved_report_path, output_dir=resolved_output_dir)
    bundle = {
        'captured_at': utc_now_iso(),
        'report_path': str(resolved_report_path),
        'output_dir': str(resolved_output_dir),
        'smoke_summary': smoke_summary,
        'copied_artifacts': copied_artifacts,
        'doctor': report.get('doctor') if isinstance(report.get('doctor'), dict) else None,
        'probe_json': report.get('probe_json') if isinstance(report.get('probe_json'), dict) else None,
        'cli_proof': report.get('cli_proof') if isinstance(report.get('cli_proof'), dict) else None,
    }
    entry = _capture_entry(bundle, output_dir=resolved_output_dir)
    history_update = _update_history(entry, path=history_target)
    comparison = _comparison_to_previous(history_update.get('previous_capture'), entry)
    bundle['capture_history'] = history_update
    bundle['comparison_to_previous_capture'] = comparison

    _write_json(resolved_output_dir / 'bundle-summary.json', bundle)
    shutil.copy2(resolved_report_path, resolved_output_dir / 'e2e-fixturelab-report.json')
    _write_json(resolved_output_dir / 'smoke-summary.json', smoke_summary)
    _write_json(resolved_output_dir / 'smoke-history.json', history_update['history'])
    _write_json(resolved_output_dir / 'smoke-diff.json', comparison)
    if bundle['doctor'] is not None:
        _write_json(resolved_output_dir / 'doctor.json', bundle['doctor'])
    if bundle['probe_json'] is not None:
        _write_json(resolved_output_dir / 'probe-json.json', bundle['probe_json'])
    if bundle['cli_proof'] is not None:
        _write_json(resolved_output_dir / 'cli-proof.json', bundle['cli_proof'])
    (resolved_output_dir / 'SUMMARY.md').write_text(_render_summary_markdown(bundle), encoding='utf-8')
    return bundle


def cli(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description='Freeze a durable bundle around a GlassTTY e2e-fixturelab smoke report.')
    sub = parser.add_subparsers(dest='command')
    history = sub.add_parser('history', help='Inspect the saved e2e-fixturelab capture ledger')
    history.add_argument('--pretty', action='store_true')
    history.add_argument('--history-path', default=str(DEFAULT_HISTORY_PATH))

    parser.add_argument('--report', default=str(DEFAULT_REPORT_PATH))
    parser.add_argument('--output-dir', default=str(DEFAULT_CAPTURE_OUTPUT_DIR))
    parser.add_argument('--history-path', default=str(DEFAULT_HISTORY_PATH))
    parser.add_argument('--pretty', action='store_true')
    args = parser.parse_args(argv)

    if args.command == 'history':
        payload = summarize_capture_history(Path(args.history_path).expanduser())
        print(json.dumps(payload, indent=2 if args.pretty else None))
        return

    bundle = build_capture_bundle(report_path=Path(args.report).expanduser(), output_dir=Path(args.output_dir).expanduser(), history_file=Path(args.history_path).expanduser())
    print(json.dumps(bundle, indent=2 if args.pretty else None))


if __name__ == '__main__':
    cli()
