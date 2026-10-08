#!/usr/bin/env python3
from __future__ import annotations

import argparse
import atexit
import inspect
import json
import os
import re
import shutil
import shlex
import signal
import socket
import subprocess
import sys
import tempfile
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parent.parent
SCRIPT_DIR = Path(__file__).resolve().parent
for candidate in (str(SCRIPT_DIR), str(ROOT), str(ROOT / 'daemon' / 'src')):
    if candidate not in sys.path:
        sys.path.insert(0, candidate)

from browser_binaries import discover_browser_executable
from playwright_browsers import (
    discover_playwright_browser_install,
    existing_playwright_browsers_path,
    playwright_browser_choice,
    playwright_extension_launch_plan,
    PLAYWRIGHT_DRY_RUN_TIMEOUT_ENV,
)
from profile_metadata import parse_devtools_active_port

try:
    from cdp_inspect import choose_target, evaluate_target, extension_url_prefix, inspect_cdp
except ModuleNotFoundError:
    from scripts.cdp_inspect import choose_target, evaluate_target, extension_url_prefix, inspect_cdp

try:
    from playwright.sync_api import sync_playwright
except Exception as exc:  # noqa: BLE001
    sync_playwright = None
    PLAYWRIGHT_IMPORT_ERROR = str(exc)
else:
    PLAYWRIGHT_IMPORT_ERROR = None

EXTENSION_DIR = ROOT / 'extension'
FIXTURE_LAB_SCRIPT = ROOT / 'scripts' / 'fixture-lab.py'
INSTALL_NATIVE_HOST = ROOT / 'scripts' / 'install-native-host.sh'
WRAPPER_PATH = ROOT / 'scripts' / 'native-host-wrapper.sh'
DOCTOR_SCRIPT = ROOT / 'scripts' / 'doctor.py'
DEFAULT_WRITE_TEXT = 'hello from GlassTTY e2e smoke'
CLI_WRITE_TEXT = 'hello from GlassTTY cli proof'
CLI_TIMEOUT = 12.0
BROWSER_ATTEMPT_PROFILE_ARTIFACTS = (
    ('devtools_active_port', Path('DevToolsActivePort'), Path('profile-artifacts') / 'DevToolsActivePort'),
    ('local_state', Path('Local State'), Path('profile-artifacts') / 'Local State'),
    ('first_run', Path('First Run'), Path('profile-artifacts') / 'First Run'),
    ('last_version', Path('Last Version'), Path('profile-artifacts') / 'Last Version'),
    ('singleton_lock', Path('SingletonLock'), Path('profile-artifacts') / 'SingletonLock'),
    ('singleton_socket', Path('SingletonSocket'), Path('profile-artifacts') / 'SingletonSocket'),
    ('singleton_cookie', Path('SingletonCookie'), Path('profile-artifacts') / 'SingletonCookie'),
    ('default_preferences', Path('Default') / 'Preferences', Path('profile-artifacts') / 'Default' / 'Preferences'),
)

BROWSER_ATTEMPT_TEXT_TAIL_MAX_CHARS = 4000
BROWSER_ATTEMPT_TEXT_TAIL_MAX_LINES = 40
BROWSER_ATTEMPT_PROFILE_LOCK_SIGNATURES = (
    'ProcessSingleton',
    'SingletonLock',
    'SingletonSocket',
    'SingletonCookie',
    'profile appears to be in use',
    'Opening in existing browser session',
)
BROWSER_ATTEMPT_SANDBOX_SIGNATURES = (
    'Running as root without --no-sandbox',
    'No usable sandbox',
    'setuid sandbox',
)
BROWSER_ATTEMPT_DISPLAY_SIGNATURES = (
    'Missing X server',
    'ozone_platform_x11',
    'cannot open display',
    'Failed to connect to the bus',
)
BROWSER_ATTEMPT_CRASH_SIGNATURES = (
    'Received signal',
    'Trace/breakpoint trap',
    'Segmentation fault',
    'core dumped',
)


def utc_now() -> str:
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())


def _json_safe(value: Any) -> Any:
    if isinstance(value, bytes):
        return value.decode('utf-8', errors='replace')
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(_json_safe(key)): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_json_safe(item) for item in value]
    return value


def write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_name(f'.{path.name}.tmp')
    tmp_path.write_text(json.dumps(_json_safe(payload), indent=2) + '\n', encoding='utf-8')
    tmp_path.replace(path)


def shell_join(argv: list[str]) -> str:
    return shlex.join([str(part) for part in argv])


SETUP_TEXT_TAIL_MAX_CHARS = 2000
SETUP_TEXT_TAIL_MAX_LINES = 20


def trim_text_tail(value: Any, *, max_chars: int = SETUP_TEXT_TAIL_MAX_CHARS, max_lines: int = SETUP_TEXT_TAIL_MAX_LINES) -> str:
    if value is None:
        return ''
    text = value.decode('utf-8', errors='replace') if isinstance(value, bytes) else str(value)
    if not text:
        return ''
    lines = text.splitlines()
    if max_lines > 0 and len(lines) > max_lines:
        lines = ['[… trimmed …]'] + lines[-max_lines:]
    trimmed = '\n'.join(lines)
    if max_chars > 0 and len(trimmed) > max_chars:
        trimmed = '[… trimmed …]\n' + trimmed[-max_chars:]
    if text.endswith('\n') and not trimmed.endswith('\n'):
        trimmed += '\n'
    return trimmed


def ensure_setup_section(report: dict[str, Any]) -> dict[str, Any]:
    setup = report.setdefault('setup', {})
    if not isinstance(setup, dict):
        setup = {}
        report['setup'] = setup
    actions = setup.get('actions')
    if not isinstance(actions, list):
        setup['actions'] = []
    if not isinstance(setup.get('replay_script_path'), str):
        setup.setdefault('replay_script_path', None)
    if not isinstance(setup.get('ledger_path'), str):
        setup.setdefault('ledger_path', None)
    if not isinstance(setup.get('summary_path'), str):
        setup.setdefault('summary_path', None)
    return setup


def append_setup_action(report: dict[str, Any], action: dict[str, Any]) -> dict[str, Any]:
    setup = ensure_setup_section(report)
    actions = setup.setdefault('actions', [])
    assert isinstance(actions, list)
    actions.append(action)
    return action


def run_command_record(argv: list[str], *, cwd: Path = ROOT, env: dict[str, str] | None = None, timeout: float = 60.0) -> dict[str, Any]:
    started_at = utc_now()
    started = time.time()
    result = subprocess.run(argv, cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout, check=False)
    record: dict[str, Any] = {
        'argv': [str(part) for part in argv],
        'command': shell_join(argv),
        'cwd': str(cwd),
        'started_at': started_at,
        'seconds': round(time.time() - started, 3),
        'returncode': result.returncode,
        'stdout': result.stdout,
        'stderr': result.stderr,
        'ok': result.returncode == 0,
    }
    parsed_json = maybe_parse_json(result.stdout) if isinstance(result.stdout, str) else None
    if parsed_json is not None:
        record['stdout_json'] = parsed_json
    return record


def planned_playwright_channel_prepare(playwright: dict[str, Any] | None, *, policy: str = 'if-needed') -> dict[str, Any]:
    if policy not in {'never', 'if-needed', 'always'}:
        raise ValueError(f'unsupported playwright channel policy: {policy}')
    playwright = playwright if isinstance(playwright, dict) else {}
    launch_plan = playwright.get('launch_plan') if isinstance(playwright.get('launch_plan'), dict) else {}
    command = launch_plan.get('recommended_channel_ready_command') or launch_plan.get('recommended_ensure_channel_ready_command')
    available = bool(playwright.get('available'))
    channel_ready = bool(launch_plan.get('channel_ready'))
    action: dict[str, Any] = {
        'name': 'playwright_channel_ready',
        'kind': 'playwright-channel-ready',
        'policy': policy,
        'command': command,
        'channel_ready_before': channel_ready,
        'cache_alignment_status_before': launch_plan.get('cache_alignment_status'),
        'cache_alignment_reason_before': launch_plan.get('cache_alignment_reason'),
        'available': available,
        'will_run': False,
        'executed': False,
        'reason': None,
        'skipped': False,
    }
    if policy == 'never':
        action['skipped'] = True
        action['reason'] = 'policy disabled automatic Playwright channel recovery'
        return action
    if not available:
        action['skipped'] = True
        action['reason'] = 'Playwright is unavailable in this environment'
        return action
    if not isinstance(command, str) or not command.strip():
        action['skipped'] = True
        action['reason'] = 'launch plan did not provide a channel-ready recovery command'
        return action
    if channel_ready and policy != 'always':
        action['skipped'] = True
        action['reason'] = 'Playwright cache is already channel-ready'
        return action
    action['will_run'] = True
    if channel_ready and policy == 'always':
        action['reason'] = 'policy requested a one-shot channel-ready recheck even though the cache already looks aligned'
    else:
        action['reason'] = 'Playwright cache is not channel-ready, so smoke will try to restore the supported channel-based lane first'
    return action


def build_setup_replay_script(report: dict[str, Any], *, cwd: Path = ROOT) -> str:
    setup = ensure_setup_section(report)
    actions = [item for item in setup.get('actions', []) if isinstance(item, dict)]
    lines = [
        '#!/usr/bin/env bash',
        'set -euo pipefail',
        f'cd {shlex.quote(str(cwd))}',
        '',
        '# Replay the most relevant GlassTTY smoke setup commands.',
        '# Commands that were only recommended or skipped stay commented out for operator review.',
        '',
    ]
    if not actions:
        lines.append('# No setup actions were recorded for this smoke run.')
    for action in actions:
        name = str(action.get('name') or action.get('kind') or 'setup-action')
        command = action.get('command')
        state = 'executed-ok' if action.get('executed') and action.get('ok') else 'executed-failed' if action.get('executed') else 'planned-only'
        lines.append(f'# {name}: {state}')
        reason = action.get('reason')
        if isinstance(reason, str) and reason.strip():
            lines.append(f'# reason: {reason.strip()}')
        if isinstance(command, str) and command.strip():
            if action.get('executed'):
                lines.append(command.strip())
            else:
                lines.append(f'# {command.strip()}')
        lines.append('')
    return '\n'.join(lines).rstrip() + '\n'


def write_setup_replay_script(output_path: Path, report: dict[str, Any]) -> Path:
    path = output_path.with_suffix('.setup-replay.sh')
    path.write_text(build_setup_replay_script(report), encoding='utf-8')
    try:
        path.chmod(path.stat().st_mode | 0o755)
    except OSError:
        pass
    ensure_setup_section(report)['replay_script_path'] = str(path)
    return path


def _compact_setup_browser_choice(choice: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(choice, dict):
        return None
    compact = {
        'browser_family': choice.get('browser_family'),
        'version': choice.get('version'),
        'source': choice.get('source'),
        'path': choice.get('path'),
        'native_messaging_targets': list(choice.get('native_messaging_targets') or []) if isinstance(choice.get('native_messaging_targets'), list) else None,
        'native_messaging_primary_target': choice.get('native_messaging_primary_target'),
    }
    compact = {key: value for key, value in compact.items() if value not in (None, [], {})}
    return compact or None



def build_setup_environment_fingerprint(report: dict[str, Any]) -> dict[str, Any]:
    setup = ensure_setup_section(report)
    playwright = report.get('playwright') if isinstance(report.get('playwright'), dict) else {}
    launch_plan = playwright.get('launch_plan') if isinstance(playwright.get('launch_plan'), dict) else {}
    browser_choice = _compact_setup_browser_choice(report.get('browser_choice') if isinstance(report.get('browser_choice'), dict) else None)
    playwright_choice = _compact_setup_browser_choice(playwright.get('browser_choice') if isinstance(playwright.get('browser_choice'), dict) else None)
    browser_env = report.get('browser_env') if isinstance(report.get('browser_env'), dict) else {}
    profile_dir = report.get('profile_dir')
    if not isinstance(profile_dir, str) and report.get('temp_root'):
        profile_dir = str(Path(str(report['temp_root'])) / 'profile')
    fingerprint: dict[str, Any] = {
        'browser_mode_requested': report.get('browser_mode_requested'),
        'browser_mode_selected': report.get('browser_mode_selected'),
        'fixture_lab_url': report.get('fixture_lab_url'),
        'playwright_channel_policy': setup.get('playwright_channel_policy'),
        'playwright_available': bool(playwright.get('available')),
        'playwright_launch_strategy': launch_plan.get('strategy'),
        'playwright_channel_ready': launch_plan.get('channel_ready'),
        'playwright_cache_alignment_status': launch_plan.get('cache_alignment_status'),
        'playwright_cache_alignment_reason': launch_plan.get('cache_alignment_reason'),
        'playwright_root': browser_env.get('PLAYWRIGHT_BROWSERS_PATH'),
        'glasstty_home': browser_env.get('GLASSTTY_HOME'),
        'chrome_config_home': browser_env.get('CHROME_CONFIG_HOME') or browser_env.get('XDG_CONFIG_HOME'),
        'runtime_dir': browser_env.get('XDG_RUNTIME_DIR'),
        'profile_dir': profile_dir,
        'native_host_install_targets': list(report.get('native_host_install_targets') or native_host_install_targets(report.get('browser_choice') if isinstance(report.get('browser_choice'), dict) else None, playwright.get('browser_choice') if isinstance(playwright.get('browser_choice'), dict) else None)),
        'default_browser': browser_choice,
        'playwright_browser': playwright_choice,
    }
    return {key: value for key, value in fingerprint.items() if value not in (None, [], {})}



def setup_action_environment_fingerprint(report: dict[str, Any], action: dict[str, Any]) -> dict[str, Any]:
    base = build_setup_environment_fingerprint(report)
    fingerprint: dict[str, Any] = {
        'browser_mode_requested': base.get('browser_mode_requested'),
        'playwright_channel_policy': base.get('playwright_channel_policy'),
        'playwright_root': base.get('playwright_root'),
        'profile_dir': base.get('profile_dir'),
        'native_host_install_targets': base.get('native_host_install_targets'),
    }
    if base.get('default_browser'):
        fingerprint['default_browser'] = base['default_browser']
    if base.get('playwright_browser'):
        fingerprint['playwright_browser'] = base['playwright_browser']
    kind = str(action.get('kind') or '')
    name = str(action.get('name') or '')
    if kind == 'playwright-channel-ready' or name == 'playwright_channel_ready':
        fingerprint.update({
            'playwright_channel_ready_before': action.get('channel_ready_before'),
            'playwright_channel_ready_after': action.get('channel_ready_after'),
            'playwright_cache_alignment_status_before': action.get('cache_alignment_status_before'),
            'playwright_cache_alignment_status_after': action.get('cache_alignment_status_after'),
            'playwright_cache_alignment_reason_before': action.get('cache_alignment_reason_before'),
            'playwright_cache_alignment_reason_after': action.get('cache_alignment_reason_after'),
        })
    if kind == 'native-host-install' or name.startswith('native_host_install_'):
        fingerprint['native_host_target'] = action.get('target')
    return {key: value for key, value in fingerprint.items() if value not in (None, [], {})}



def summarize_setup_action(action: dict[str, Any], *, report: dict[str, Any] | None = None) -> dict[str, Any]:
    summary: dict[str, Any] = {
        'name': action.get('name') or action.get('kind') or 'setup-action',
        'kind': action.get('kind'),
        'target': action.get('target'),
        'policy': action.get('policy'),
        'command': action.get('command'),
        'argv': list(action.get('argv') or []) if isinstance(action.get('argv'), list) else None,
        'will_run': bool(action.get('will_run')),
        'executed': bool(action.get('executed')),
        'ok': action.get('ok'),
        'skipped': bool(action.get('skipped')),
        'reason': action.get('reason'),
        'seconds': action.get('seconds'),
        'returncode': action.get('returncode'),
        'started_at': action.get('started_at'),
        'channel_ready_before': action.get('channel_ready_before'),
        'channel_ready_after': action.get('channel_ready_after'),
        'cache_alignment_status_before': action.get('cache_alignment_status_before'),
        'cache_alignment_status_after': action.get('cache_alignment_status_after'),
        'cache_alignment_reason_before': action.get('cache_alignment_reason_before'),
        'cache_alignment_reason_after': action.get('cache_alignment_reason_after'),
    }
    if isinstance(report, dict):
        fingerprint = setup_action_environment_fingerprint(report, action)
        if fingerprint:
            summary['environment_fingerprint'] = fingerprint
    stdout_tail = trim_text_tail(action.get('stdout'))
    stderr_tail = trim_text_tail(action.get('stderr'))
    if stdout_tail:
        summary['stdout_tail'] = stdout_tail
    if stderr_tail:
        summary['stderr_tail'] = stderr_tail
    stdout_json = action.get('stdout_json') if isinstance(action.get('stdout_json'), dict) else None
    if stdout_json is not None:
        summary['stdout_json_keys'] = sorted(str(key) for key in stdout_json.keys())
    return {key: value for key, value in summary.items() if value not in (None, [], {})}



def derive_setup_next_action(report: dict[str, Any], *, replay_path: str | None = None) -> dict[str, Any] | None:
    setup = ensure_setup_section(report)
    actions = [item for item in (setup.get('actions') or []) if isinstance(item, dict)]
    playwright = report.get('playwright') if isinstance(report.get('playwright'), dict) else {}
    launch_plan = playwright.get('launch_plan') if isinstance(playwright.get('launch_plan'), dict) else {}
    if replay_path is None:
        replay_path = setup.get('replay_script_path')

    def _replay_command() -> str | None:
        if isinstance(replay_path, str) and replay_path.strip():
            return f"bash {shlex.quote(replay_path)}"
        return None

    failed = [item for item in actions if item.get('executed') and item.get('ok') is False]
    if failed:
        action = failed[0]
        name = str(action.get('name') or action.get('kind') or 'setup-action')
        kind = str(action.get('kind') or '')
        if kind == 'playwright-channel-ready' or name == 'playwright_channel_ready':
            command = action.get('command') or launch_plan.get('recommended_channel_ready_command') or 'python scripts/playwright-browsers.py inspect --pretty'
            return {
                'action_name': name,
                'summary': 'Repair or inspect Playwright cache alignment before rerunning fixture-lab smoke.',
                'command': command,
                'reason': action.get('reason') or launch_plan.get('cache_alignment_reason') or 'Playwright channel recovery failed during smoke setup.',
            }
        if kind == 'native-host-install' or name.startswith('native_host_install_'):
            target = action.get('target') or name.removeprefix('native_host_install_')
            return {
                'action_name': name,
                'summary': 'Reinstall the native host for the failed browser-family target before rerunning smoke.',
                'command': action.get('command'),
                'reason': f'Native-host installation failed for target {target}.',
            }
        return {
            'action_name': name,
            'summary': 'Replay the first failed smoke setup action before rerunning the browser lane.',
            'command': action.get('command') or _replay_command(),
            'reason': action.get('reason') or 'The first recorded setup failure should be retried directly.',
        }

    for action in actions:
        if action.get('will_run') and not action.get('executed') and action.get('command'):
            return {
                'action_name': str(action.get('name') or action.get('kind') or 'setup-action'),
                'summary': 'Run the highest-priority planned setup step before the next live smoke attempt.',
                'command': action.get('command'),
                'reason': action.get('reason') or 'Smoke recorded this setup step as the next action to run.',
            }
    replay_command = _replay_command()
    if replay_command:
        return {
            'action_name': 'setup-replay',
            'summary': 'Replay the saved GlassTTY smoke setup recipe before the next browser attempt.',
            'command': replay_command,
            'reason': 'The recorded setup completed or was only partially executed; replay the saved recipe to reproduce it.',
        }
    return None



def build_setup_ledger(report: dict[str, Any], *, cwd: Path = ROOT) -> dict[str, Any]:
    setup = ensure_setup_section(report)
    actions = [item for item in (setup.get('actions') or []) if isinstance(item, dict)]
    summaries = [summarize_setup_action(action, report=report) for action in actions]
    executed = [item for item in summaries if item.get('executed')]
    failed = [item for item in executed if item.get('ok') is False]
    skipped = [item for item in summaries if item.get('skipped')]
    planned_only = [item for item in summaries if not item.get('executed')]
    next_action = derive_setup_next_action(report, replay_path=setup.get('replay_script_path'))
    ledger: dict[str, Any] = {
        'generated_at': utc_now(),
        'cwd': str(cwd),
        'report_timestamp': report.get('timestamp'),
        'report_phase': report.get('phase'),
        'playwright_channel_policy': setup.get('playwright_channel_policy'),
        'replay_script_path': setup.get('replay_script_path'),
        'environment_fingerprint': build_setup_environment_fingerprint(report),
        'actions': summaries,
        'counts': {
            'total': len(summaries),
            'executed': len(executed),
            'failed': len(failed),
            'skipped': len(skipped),
            'planned_only': len(planned_only),
        },
        'failed_action_names': [item.get('name') for item in failed if item.get('name')],
        'last_action_name': summaries[-1].get('name') if summaries else None,
        'last_action_state': (
            'executed-ok' if summaries and summaries[-1].get('executed') and summaries[-1].get('ok') else
            'executed-failed' if summaries and summaries[-1].get('executed') else
            'skipped' if summaries and summaries[-1].get('skipped') else
            'planned-only' if summaries else None
        ),
        'recommended_replay_command': None,
        'recommended_next_action': next_action,
    }
    if failed:
        first_failure = failed[0]
        ledger['first_failure'] = {
            'name': first_failure.get('name'),
            'command': first_failure.get('command'),
            'returncode': first_failure.get('returncode'),
            'reason': first_failure.get('reason'),
        }
    return ledger



def build_setup_summary_markdown(report: dict[str, Any], *, output_path: Path | None = None) -> str:
    setup = ensure_setup_section(report)
    ledger = build_setup_ledger(report)
    replay_path = setup.get('replay_script_path') or (str(output_path.with_suffix('.setup-replay.sh')) if output_path else None)
    ledger_path = setup.get('ledger_path') or (str(output_path.with_suffix('.setup-ledger.json')) if output_path else None)
    lines = [
        '# GlassTTY smoke setup summary',
        '',
        f"- report_phase: {report.get('phase')}",
        f"- report_timestamp: {report.get('timestamp')}",
        f"- setup_action_count: {ledger['counts']['total']}",
        f"- executed_setup_action_count: {ledger['counts']['executed']}",
        f"- failed_setup_action_count: {ledger['counts']['failed']}",
        f"- skipped_setup_action_count: {ledger['counts']['skipped']}",
    ]
    if replay_path:
        lines.append(f"- setup_replay_script: `{replay_path}`")
    if ledger_path:
        lines.append(f"- setup_ledger_json: `{ledger_path}`")
    fingerprint = ledger.get('environment_fingerprint') if isinstance(ledger.get('environment_fingerprint'), dict) else {}
    if fingerprint:
        lines.extend(['', '## Environment fingerprint', ''])
        for key in (
            'browser_mode_requested',
            'browser_mode_selected',
            'playwright_channel_policy',
            'playwright_launch_strategy',
            'playwright_channel_ready',
            'playwright_cache_alignment_status',
            'playwright_root',
            'profile_dir',
            'native_host_install_targets',
        ):
            if key not in fingerprint:
                continue
            value = fingerprint[key]
            lines.append(f"- {key}: `{json.dumps(value, sort_keys=True)}`" if isinstance(value, (list, dict)) else f"- {key}: {value}")
        default_browser = fingerprint.get('default_browser') if isinstance(fingerprint.get('default_browser'), dict) else None
        playwright_browser = fingerprint.get('playwright_browser') if isinstance(fingerprint.get('playwright_browser'), dict) else None
        if default_browser:
            lines.append(f"- default_browser: `{json.dumps(default_browser, sort_keys=True)}`")
        if playwright_browser:
            lines.append(f"- playwright_browser: `{json.dumps(playwright_browser, sort_keys=True)}`")
    next_action = ledger.get('recommended_next_action') if isinstance(ledger.get('recommended_next_action'), dict) else None
    if next_action:
        lines.extend(['', '## Recommended next action', ''])
        lines.append(f"- summary: {next_action.get('summary')}")
        if next_action.get('command'):
            lines.append(f"- command: `{next_action.get('command')}`")
        if next_action.get('reason'):
            lines.append(f"- reason: {next_action.get('reason')}")
        if next_action.get('action_name'):
            lines.append(f"- source_action: `{next_action.get('action_name')}`")
    lines.extend(['', '## Actions', ''])
    if not ledger['actions']:
        lines.append('- No setup actions were recorded.')
    for action in ledger['actions']:
        state = 'executed-ok' if action.get('executed') and action.get('ok') else 'executed-failed' if action.get('executed') else 'skipped' if action.get('skipped') else 'planned-only'
        command = action.get('command')
        lines.append(f"- `{action.get('name')}` — {state}")
        if action.get('reason'):
            lines.append(f"  - reason: {action.get('reason')}")
        if command:
            lines.append(f"  - command: `{command}`")
        action_fingerprint = action.get('environment_fingerprint') if isinstance(action.get('environment_fingerprint'), dict) else None
        if action_fingerprint:
            lines.append(f"  - environment_fingerprint: `{json.dumps(action_fingerprint, sort_keys=True)}`")
        if action.get('stdout_tail'):
            lines.append('  - stdout_tail:')
            lines.append('')
            lines.append('    ```text')
            for raw_line in str(action['stdout_tail']).splitlines():
                lines.append(f'    {raw_line}')
            lines.append('    ```')
        if action.get('stderr_tail'):
            lines.append('  - stderr_tail:')
            lines.append('')
            lines.append('    ```text')
            for raw_line in str(action['stderr_tail']).splitlines():
                lines.append(f'    {raw_line}')
            lines.append('    ```')
    lines.append('')
    return '\n'.join(lines).rstrip() + '\n'



def write_setup_ledger(output_path: Path, report: dict[str, Any]) -> Path:
    path = output_path.with_suffix('.setup-ledger.json')
    ledger = build_setup_ledger(report)
    ledger['recommended_replay_command'] = f"bash {shlex.quote(str(output_path.with_suffix('.setup-replay.sh')))}"
    write_json_atomic(path, ledger)
    setup = ensure_setup_section(report)
    setup['ledger_path'] = str(path)
    setup['environment_fingerprint'] = ledger.get('environment_fingerprint')
    setup['recommended_next_action'] = ledger.get('recommended_next_action')
    return path



def write_setup_summary(output_path: Path, report: dict[str, Any]) -> Path:
    path = output_path.with_suffix('.setup-summary.md')
    path.write_text(build_setup_summary_markdown(report, output_path=output_path), encoding='utf-8')
    ensure_setup_section(report)['summary_path'] = str(path)
    return path



def write_setup_artifacts(output_path: Path, report: dict[str, Any]) -> None:
    write_setup_replay_script(output_path, report)
    write_setup_ledger(output_path, report)
    write_setup_summary(output_path, report)
    write_json_atomic(output_path, report)


def checkpoint_report(report: dict[str, Any], output_path: Path, *, phase: str, note: str | None = None, event: dict[str, Any] | None = None) -> None:
    report['phase'] = phase
    checkpoint = report.setdefault('checkpoint', {})
    sequence = int(checkpoint.get('sequence') or 0) + 1
    checkpoint.update({'sequence': sequence, 'phase': phase, 'timestamp': utc_now()})
    if note:
        checkpoint['note'] = note
    events = report.setdefault('events', [])
    if note or event:
        entry: dict[str, Any] = {'sequence': sequence, 'phase': phase, 'timestamp': checkpoint['timestamp']}
        if note:
            entry['note'] = note
        if event:
            entry.update(event)
        events.append(entry)
    write_json_atomic(output_path, report)
    try:
        write_setup_artifacts(output_path, report)
    except Exception:
        pass


def append_step(report: dict[str, Any], step: str) -> None:
    steps = report.setdefault('steps', [])
    if step not in steps:
        steps.append(step)


def mark_browser_attempt_inflight(report: dict[str, Any], attempt: dict[str, Any]) -> None:
    report['browser_attempt_inflight'] = {
        'started_at': utc_now(),
        **_json_safe(attempt),
    }


def clear_browser_attempt_inflight(report: dict[str, Any]) -> None:
    report.pop('browser_attempt_inflight', None)


def finalize_browser_attempt(
    report: dict[str, Any],
    attempt: dict[str, Any] | None,
    *,
    process: subprocess.Popen[str] | None = None,
    interrupted: bool = False,
    interruption_reason: str | None = None,
) -> dict[str, Any] | None:
    if not isinstance(attempt, dict):
        clear_browser_attempt_inflight(report)
        return None
    if process is not None:
        mode = attempt.get('mode') if isinstance(attempt.get('mode'), str) else 'unknown'
        stop_process(process, name=f'chromium_{mode}', report=attempt)
    if interrupted or interruption_reason:
        attempt['interrupted'] = True
        if interruption_reason:
            attempt['interruption_reason'] = interruption_reason
    attempts = report.setdefault('browser_attempts', [])
    if attempt not in attempts:
        attempts.append(attempt)
    clear_browser_attempt_inflight(report)
    return attempt


SERVICE_WORKER_EVENT_LIMIT = 40


def _maybe_call(value: Any) -> Any:
    if callable(value):
        try:
            return value()
        except TypeError:
            return value
        except Exception:
            return None
    return value


def _safe_attr(obj: Any, name: str, default: Any = None) -> Any:
    if not hasattr(obj, name):
        return default
    try:
        return _maybe_call(getattr(obj, name))
    except Exception:
        return default


def _append_limited(items: list[dict[str, Any]], entry: dict[str, Any], *, limit: int = SERVICE_WORKER_EVENT_LIMIT) -> None:
    if len(items) < limit:
        items.append(entry)


def _console_message_summary(message: Any) -> dict[str, Any]:
    return {
        'type': _safe_attr(message, 'type', '<unknown>') or '<unknown>',
        'text': _safe_attr(message, 'text', '') or '',
    }


def _service_worker_snapshot(worker: Any, *, evaluate_runtime: bool = True) -> dict[str, Any]:
    snapshot: dict[str, Any] = {'url': _safe_attr(worker, 'url')}
    if evaluate_runtime and hasattr(worker, 'evaluate'):
        try:
            runtime = worker.evaluate(
                "() => ({ locationHref: self.location?.href ?? null, origin: self.location?.origin ?? null, userAgent: self.navigator?.userAgent ?? null, hasClientsMatchAll: typeof self.clients?.matchAll === 'function', scope: self.registration?.scope ?? null })"
            )
        except Exception as exc:  # noqa: BLE001
            snapshot['evaluate_error'] = str(exc)
        else:
            if isinstance(runtime, dict):
                snapshot['runtime'] = runtime
    return snapshot


def _service_workers_from_context(context: Any) -> list[Any]:
    workers = getattr(context, 'service_workers', [])
    try:
        resolved = workers() if callable(workers) else workers
    except Exception:
        resolved = []
    if not resolved:
        return []
    if isinstance(resolved, list):
        return list(resolved)
    try:
        return list(resolved)
    except Exception:
        return []


def _extension_id_from_worker(worker: Any) -> str | None:
    url = _safe_attr(worker, 'url', '') or ''
    if not isinstance(url, str) or not url.startswith('chrome-extension://'):
        return None
    parts = url.split('/')
    if len(parts) < 3:
        return None
    return parts[2] or None


def wait_for_healthy_extension_service_worker(
    context: Any,
    *,
    expected_extension_id: str | None,
    timeout: float,
    report: dict[str, Any] | None = None,
    poll_interval: float = 0.2,
) -> tuple[Any, dict[str, Any], dict[str, Any]]:
    deadline = time.time() + max(timeout, 0.0)
    wait_report: dict[str, Any] = {
        'expected_extension_id': expected_extension_id,
        'attempts': 0,
        'matching_worker_count': 0,
        'worker_urls_seen': [],
        'selected_worker_url': None,
        'healthy': False,
        'timed_out': False,
        'last_evaluate_error': None,
        'notes': [],
    }
    seen_urls: set[str] = set()
    stale_snapshots: list[dict[str, Any]] = []
    last_snapshot: dict[str, Any] | None = None

    while True:
        wait_report['attempts'] = int(wait_report['attempts']) + 1
        workers = _service_workers_from_context(context)
        matching = [worker for worker in workers if expected_extension_id and _extension_id_from_worker(worker) == expected_extension_id]
        candidates = matching or workers
        wait_report['matching_worker_count'] = max(int(wait_report['matching_worker_count']), len(candidates))
        for worker in candidates:
            url = _safe_attr(worker, 'url')
            if isinstance(url, str) and url and url not in seen_urls:
                seen_urls.add(url)
                wait_report['worker_urls_seen'].append(url)
            snapshot = _service_worker_snapshot(worker)
            snapshot['wait_attempt'] = wait_report['attempts']
            last_snapshot = snapshot
            evaluate_error = snapshot.get('evaluate_error')
            if evaluate_error:
                wait_report['last_evaluate_error'] = str(evaluate_error)
                if len(stale_snapshots) < SERVICE_WORKER_EVENT_LIMIT:
                    stale_snapshots.append({
                        'url': snapshot.get('url'),
                        'wait_attempt': wait_report['attempts'],
                        'evaluate_error': str(evaluate_error),
                    })
                continue
            wait_report['healthy'] = True
            wait_report['selected_worker_url'] = snapshot.get('url')
            wait_report['selected_snapshot'] = snapshot
            if stale_snapshots:
                wait_report['stale_snapshots'] = stale_snapshots
            if report is not None:
                report['service_worker_wait'] = wait_report
            return worker, snapshot, wait_report

        if time.time() >= deadline:
            wait_report['timed_out'] = True
            if stale_snapshots:
                wait_report['stale_snapshots'] = stale_snapshots
            if last_snapshot is not None:
                wait_report['last_snapshot'] = last_snapshot
            if report is not None:
                report['service_worker_wait'] = wait_report
            detail = ''
            if wait_report.get('worker_urls_seen'):
                detail = f"; worker_urls={wait_report['worker_urls_seen']}"
            if wait_report.get('last_evaluate_error'):
                detail += f"; last_evaluate_error={wait_report['last_evaluate_error']}"
            raise RuntimeError(f'Playwright never observed a healthy extension service worker{detail}')

        time.sleep(max(0.01, poll_interval))


def _request_summary(request: Any, *, event: str) -> dict[str, Any]:
    service_worker = _safe_attr(request, 'service_worker')
    summary: dict[str, Any] = {
        'event': event,
        'url': _safe_attr(request, 'url'),
        'method': _safe_attr(request, 'method'),
        'resource_type': _safe_attr(request, 'resource_type'),
        'is_navigation_request': bool(_safe_attr(request, 'is_navigation_request', False)),
        'service_worker_url': _safe_attr(service_worker, 'url'),
    }
    failure = _safe_attr(request, 'failure')
    if failure:
        summary['failure'] = failure
    response = None
    try:
        response_attr = getattr(request, 'response', None)
    except Exception:
        response_attr = None
    if callable(response_attr):
        try:
            response = response_attr()
        except Exception:
            response = None
    elif response_attr is not None:
        response = response_attr
    if response is not None:
        status = _safe_attr(response, 'status')
        if status is not None:
            summary['response_status'] = status
    return summary


def attach_context_telemetry(context: Any, *, report: dict[str, Any]) -> None:
    report.setdefault('context_console_messages', [])
    report.setdefault('context_weberrors', [])
    report.setdefault('service_worker_events', [])
    report.setdefault('service_worker_snapshots', [])
    report.setdefault('service_worker_console_messages', [])
    report.setdefault('service_worker_requests', [])
    report.setdefault('service_worker_request_failures', [])
    report.setdefault('service_worker_event_limit', SERVICE_WORKER_EVENT_LIMIT)

    registered_workers: set[int] = set()

    def register_worker(worker: Any, *, source: str) -> None:
        marker = id(worker)
        if marker in registered_workers:
            return
        registered_workers.add(marker)
        snapshot = _service_worker_snapshot(worker)
        snapshot['source'] = source
        _append_limited(report['service_worker_snapshots'], snapshot)
        _append_limited(report['service_worker_events'], {'event': 'seen', 'source': source, 'url': snapshot.get('url')})
        if hasattr(worker, 'on'):
            try:
                worker.on('close', lambda _worker=None, worker=worker: _append_limited(report['service_worker_events'], {'event': 'close', 'url': _safe_attr(worker, 'url')}))
            except Exception:
                pass
            try:
                worker.on('console', lambda message, worker=worker: _append_limited(report['service_worker_console_messages'], {'url': _safe_attr(worker, 'url'), **_console_message_summary(message)}))
            except Exception:
                pass

    for existing_worker in _service_workers_from_context(context):
        register_worker(existing_worker, source='existing')

    if hasattr(context, 'on'):
        try:
            context.on('serviceworker', lambda worker: register_worker(worker, source='event'))
        except Exception:
            pass
        try:
            context.on('console', lambda message: _append_limited(report['context_console_messages'], _console_message_summary(message)))
        except Exception:
            pass
        try:
            context.on('weberror', lambda error: _append_limited(report['context_weberrors'], {'message': str(error)}))
        except Exception:
            pass

        def maybe_record_request(request: Any, *, event: str) -> None:
            if _safe_attr(request, 'service_worker') is None:
                return
            summary = _request_summary(request, event=event)
            _append_limited(report['service_worker_requests'], summary)
            if event == 'requestfailed':
                _append_limited(report['service_worker_request_failures'], summary)

        for event_name in ('request', 'requestfinished', 'requestfailed'):
            try:
                context.on(event_name, lambda request, event_name=event_name: maybe_record_request(request, event=event_name))
            except Exception:
                pass


def install_termination_checkpoint(report: dict[str, Any], output_path: Path) -> tuple[Callable[[], None], dict[int, Any]]:
    previous_handlers: dict[int, Any] = {}

    def _write_termination(signum: int) -> None:
        report['terminated'] = True
        report['terminated_signal'] = signum
        checkpoint_report(
            report,
            output_path,
            phase='terminated',
            note=f'received signal {signum}',
            event={'kind': 'signal', 'signal': signum},
        )

    def _handler(signum: int, _frame: Any) -> None:
        try:
            _write_termination(signum)
        finally:
            raise SystemExit(128 + signum)

    for signum in (getattr(signal, 'SIGTERM', None), getattr(signal, 'SIGINT', None)):
        if signum is None:
            continue
        previous_handlers[signum] = signal.getsignal(signum)
        signal.signal(signum, _handler)

    def restore() -> None:
        for signum, handler in previous_handlers.items():
            signal.signal(signum, handler)

    return restore, previous_handlers


def connect_over_cdp_kwargs(chromium: Any, *, endpoint: str, timeout: float) -> dict[str, Any]:
    kwargs: dict[str, Any] = {
        'endpoint_url': endpoint,
        'timeout': max(1, int(timeout * 1000)),
    }
    try:
        parameters = inspect.signature(chromium.connect_over_cdp).parameters
    except (TypeError, ValueError):
        parameters = {}
    if 'is_local' in parameters:
        kwargs['is_local'] = True
    return kwargs


def make_tree_writable(path: Path) -> None:
    if not path.exists():
        return
    for candidate in [path, *path.rglob('*')]:
        try:
            mode = candidate.stat().st_mode
            candidate.chmod(mode | 0o200)
        except (FileNotFoundError, PermissionError):
            continue


def extension_dist_ready(extension_dir: Path) -> bool:
    required = [
        extension_dir / 'manifest.json',
        extension_dir / 'probe' / 'index.html',
        extension_dir / 'offscreen' / 'index.html',
        extension_dir / 'dist' / 'background' / 'main.js',
        extension_dir / 'dist' / 'content' / 'main.js',
        extension_dir / 'dist' / 'probe' / 'main.js',
        extension_dir / 'dist' / 'offscreen' / 'main.js',
    ]
    return all(path.exists() for path in required)


def free_tcp_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(('127.0.0.1', 0))
        return int(sock.getsockname()[1])


def fetch_json(url: str, timeout: float) -> Any:
    with urllib.request.urlopen(url, timeout=timeout) as response:
        return json.loads(response.read().decode('utf-8'))


def wait_for_http(url: str, timeout: float) -> None:
    deadline = time.time() + timeout
    last_error: Exception | None = None
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1) as response:
                if response.status == 200:
                    return
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            time.sleep(0.1)
    raise RuntimeError(f'timed out waiting for {url}: {last_error}')


def run(argv: list[str], *, cwd: Path = ROOT, env: dict[str, str] | None = None, timeout: float = 60.0, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(argv, cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout, check=False)
    if check and result.returncode != 0:
        raise RuntimeError(
            f"command failed ({result.returncode}): {' '.join(argv)}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
    return result


def maybe_parse_json(text: str) -> Any:
    body = text.strip()
    if not body:
        return None
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return None


def cli_argv(*parts: str) -> list[str]:
    return [sys.executable, '-m', 'glassttyd.cli', *parts]


def run_cli_step(name: str, argv: list[str], *, env: dict[str, str], timeout: float, cwd: Path = ROOT, retries: int = 2, retry_sleep: float = 0.4) -> dict[str, Any]:
    attempts: list[dict[str, Any]] = []
    for attempt in range(1, retries + 1):
        started = time.time()
        result = subprocess.run(argv, cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout, check=False)
        attempts.append({
            'attempt': attempt,
            'argv': argv,
            'returncode': result.returncode,
            'seconds': round(time.time() - started, 3),
            'stdout': result.stdout,
            'stderr': result.stderr,
        })
        if result.returncode == 0:
            break
        if attempt < retries:
            time.sleep(retry_sleep)
    final = attempts[-1]
    parsed_json = maybe_parse_json(final.get('stdout', '')) if isinstance(final.get('stdout', ''), str) else None
    return {'name': name, 'ok': final.get('returncode') == 0, 'attempts': attempts, 'stdout_json': parsed_json}


def run_cli_proof(*, env: dict[str, str], timeout: float, expected_prompt: str | None, latest_expected: str | None, fixtures_dir: Path) -> dict[str, Any]:
    fixtures_dir.mkdir(parents=True, exist_ok=True)
    proof: dict[str, Any] = {'ok': False, 'timeout': timeout, 'expected_prompt_before': expected_prompt, 'expected_latest': latest_expected, 'write_text': CLI_WRITE_TEXT, 'steps': []}

    def add(name: str, *parts: str) -> dict[str, Any]:
        step = run_cli_step(name, cli_argv(*parts), env=env, timeout=timeout)
        proof['steps'].append(step)
        return step

    bridge_status = add('bridge_status', 'bridge-status', '--wait', '--timeout', str(timeout))
    contexts = add('contexts', 'contexts', '--wait', '--timeout', str(timeout))
    trace = add('trace', 'trace', '--wait', '--timeout', str(timeout), '--limit', '20')
    prompt_before = add('read_prompt_before', 'read-prompt', '--wait', '--timeout', str(timeout), '--text')
    add('write_prompt', 'write-prompt', CLI_WRITE_TEXT, '--wait', '--timeout', str(timeout))
    prompt_after = add('read_prompt_after', 'read-prompt', '--wait', '--timeout', str(timeout), '--text')
    latest = add('read_latest', 'read-latest', '--wait', '--timeout', str(timeout), '--text')
    capture = add('capture_fixture', 'capture-fixture', '--timeout', str(timeout), '--output-dir', str(fixtures_dir))

    bridge_payload = (((bridge_status.get('stdout_json') or {}).get('message') or {}).get('payload') or {}) if isinstance(bridge_status.get('stdout_json'), dict) else {}
    contexts_payload = (((contexts.get('stdout_json') or {}).get('message') or {}).get('payload') or {}) if isinstance(contexts.get('stdout_json'), dict) else {}
    trace_payload = (((trace.get('stdout_json') or {}).get('message') or {}).get('payload') or {}) if isinstance(trace.get('stdout_json'), dict) else {}
    prompt_before_text = str((prompt_before['attempts'][-1].get('stdout') or '')).strip()
    prompt_after_text = str((prompt_after['attempts'][-1].get('stdout') or '')).strip()
    latest_text = str((latest['attempts'][-1].get('stdout') or '')).strip()
    capture_text = str((capture['attempts'][-1].get('stdout') or '')).strip()
    capture_path = Path(capture_text.splitlines()[-1]) if capture_text else None

    proof['bridge_payload'] = bridge_payload
    proof['contexts_payload'] = contexts_payload
    proof['trace_payload'] = trace_payload
    proof['prompt_before_text'] = prompt_before_text
    proof['prompt_after_text'] = prompt_after_text
    proof['latest_text'] = latest_text
    proof['capture_fixture_path'] = str(capture_path) if capture_path else None
    proof['capture_fixture_exists'] = bool(capture_path and capture_path.exists())

    errors: list[str] = []
    if expected_prompt is not None and prompt_before_text != expected_prompt:
        errors.append(f'CLI read-prompt before write mismatch: expected {expected_prompt!r} got {prompt_before_text!r}')
    if prompt_after_text != CLI_WRITE_TEXT:
        errors.append(f'CLI read-prompt after write mismatch: expected {CLI_WRITE_TEXT!r} got {prompt_after_text!r}')
    if latest_expected is not None and latest_text != latest_expected:
        errors.append(f'CLI read-latest mismatch: expected {latest_expected!r} got {latest_text!r}')
    native_connection = bridge_payload.get('nativeConnection') if isinstance(bridge_payload, dict) else None
    if not isinstance(native_connection, dict) or not native_connection.get('connected'):
        errors.append('CLI bridge-status did not report a connected nativeConnection')
    if not isinstance(contexts_payload, dict) or not contexts_payload.get('runtimeId'):
        errors.append('CLI contexts did not report runtimeId')
    trace_events = trace_payload.get('events') if isinstance(trace_payload, dict) else None
    if not isinstance(trace_events, list) or not trace_events:
        errors.append('CLI trace did not report recent events')
    if not proof['capture_fixture_exists']:
        errors.append('CLI capture-fixture did not produce a saved fixture file')
    for step in proof['steps']:
        if not step.get('ok'):
            errors.append(f"CLI step failed: {step['name']}")
    proof['errors'] = errors
    proof['ok'] = not errors
    return proof


def native_bootstrap_summary(probe_json: dict[str, Any] | None) -> dict[str, Any]:
    bridge = probe_json.get('bridge') if isinstance(probe_json, dict) else None
    status = bridge.get('status') if isinstance(bridge, dict) else None
    native = status.get('nativeConnection') if isinstance(status, dict) else None
    if not isinstance(native, dict):
        return {'available': False, 'connected': False, 'oneshot_ok': False, 'native_host': None, 'socket_path': None}
    return {
        'available': True,
        'connected': bool(native.get('connected')),
        'persistent_ok': bool(native.get('connected')) and native.get('lastHealthOk') is not False and not native.get('lastHealthError'),
        'oneshot_ok': bool(native.get('lastOneShotProbeOk')) and not native.get('lastOneShotProbeError'),
        'oneshot_error': native.get('lastOneShotProbeError'),
        'native_host': native.get('nativeHost') or native.get('lastOneShotProbeHost'),
        'socket_path': native.get('socketPath') or native.get('lastOneShotProbeSocketPath'),
        'health_error': native.get('lastHealthError'),
        'disconnect_reason': native.get('lastDisconnectReason'),
    }


def extension_context_summary(probe_json: dict[str, Any] | None, *, expected_extension_id: str | None = None) -> dict[str, Any]:
    bridge = probe_json.get('bridge') if isinstance(probe_json, dict) else None
    contexts = bridge.get('contexts') if isinstance(bridge, dict) else None
    if not isinstance(contexts, dict):
        return {
            'available': False,
            'runtime_id': None,
            'runtime_id_matches_extension': False,
            'has_runtime_get_contexts': False,
            'context_count': 0,
            'context_types': [],
            'background_contexts': [],
            'background_context_count': 0,
            'background_context_seen': False,
            'offscreen_contexts': [],
            'offscreen_context_count': 0,
            'offscreen_context_seen': False,
            'side_panel_context_count': 0,
            'tab_context_count': 0,
        }
    open_contexts = contexts.get('openContexts') if isinstance(contexts.get('openContexts'), list) else []
    typed_contexts = [item for item in open_contexts if isinstance(item, dict)]
    context_types = sorted({str(item.get('contextType')) for item in typed_contexts if item.get('contextType') is not None})
    background_contexts = [item for item in typed_contexts if item.get('contextType') == 'BACKGROUND']
    side_panel_contexts = [item for item in typed_contexts if item.get('contextType') == 'SIDE_PANEL']
    offscreen_contexts = [item for item in typed_contexts if item.get('contextType') == 'OFFSCREEN_DOCUMENT']
    tab_contexts = [item for item in typed_contexts if item.get('contextType') == 'TAB']
    runtime_id = contexts.get('runtimeId') if isinstance(contexts.get('runtimeId'), str) else None
    return {
        'available': True,
        'runtime_id': runtime_id,
        'runtime_id_matches_extension': bool(expected_extension_id) and runtime_id == expected_extension_id,
        'has_runtime_get_contexts': bool(contexts.get('hasRuntimeGetContexts')),
        'context_count': len(typed_contexts),
        'context_types': context_types,
        'background_contexts': background_contexts,
        'background_context_count': len(background_contexts),
        'background_context_seen': bool(background_contexts),
        'offscreen_contexts': offscreen_contexts,
        'offscreen_context_count': len(offscreen_contexts),
        'offscreen_context_seen': bool(offscreen_contexts),
        'side_panel_context_count': len(side_panel_contexts),
        'tab_context_count': len(tab_contexts),
    }


def native_host_install_targets(browser_choice: dict[str, Any] | None, playwright_choice: dict[str, Any] | None = None) -> list[str]:
    ordered: list[str] = []
    seen: set[str] = set()
    for choice in (playwright_choice, browser_choice):
        for target in list((choice or {}).get('native_messaging_targets') or []):
            normalized = str(target).strip()
            if not normalized or normalized in seen:
                continue
            ordered.append(normalized)
            seen.add(normalized)
    return ordered or ['chromium']



def browser_attempt_artifact_root(output_path: Path) -> Path:
    return output_path.with_name(f'{output_path.stem}.browser-attempts')


def _tail_text(value: str | None, *, max_chars: int = BROWSER_ATTEMPT_TEXT_TAIL_MAX_CHARS, max_lines: int = BROWSER_ATTEMPT_TEXT_TAIL_MAX_LINES) -> str | None:
    if not isinstance(value, str):
        return None
    text = value.replace('\r\n', '\n').replace('\r', '\n')
    if max_chars > 0 and len(text) > max_chars:
        text = text[-max_chars:]
    if max_lines > 0:
        lines = text.splitlines()
        if len(lines) > max_lines:
            text = '\n'.join(lines[-max_lines:])
    return text


def _read_text_tail(path: Path, *, max_chars: int = BROWSER_ATTEMPT_TEXT_TAIL_MAX_CHARS, max_lines: int = BROWSER_ATTEMPT_TEXT_TAIL_MAX_LINES) -> str | None:
    try:
        return _tail_text(path.read_text(encoding='utf-8', errors='replace'), max_chars=max_chars, max_lines=max_lines)
    except Exception:
        return None


def diagnose_browser_attempt_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    attempt = snapshot.get('attempt') if isinstance(snapshot.get('attempt'), dict) else {}
    cdp = attempt.get('cdp') if isinstance(attempt.get('cdp'), dict) else {}
    devtools = snapshot.get('devtools_active_port') if isinstance(snapshot.get('devtools_active_port'), dict) else {}
    crash_reports = snapshot.get('crash_reports') if isinstance(snapshot.get('crash_reports'), dict) else {}
    copied_artifacts = [item for item in (snapshot.get('copied_artifacts') or []) if isinstance(item, dict)]
    copied_by_label = {str(item.get('label')): item for item in copied_artifacts if item.get('label')}
    profile_lock_artifacts = [
        label
        for label in ('singleton_lock', 'singleton_socket', 'singleton_cookie')
        if bool((copied_by_label.get(label) or {}).get('exists'))
    ]
    artifact_dir = Path(snapshot['artifact_dir']) if isinstance(snapshot.get('artifact_dir'), str) and snapshot.get('artifact_dir') else None
    chrome_debug_log_tail = _read_text_tail(artifact_dir / 'browser-config' / 'chrome_debug.log') if artifact_dir else None
    stderr_tail_parts = [
        _tail_text(attempt.get('chromium_unknown_stderr')),
        _tail_text(attempt.get('chromium_headless-new_stderr')),
        _tail_text(attempt.get('chromium_headed_stderr')),
        _tail_text(attempt.get('chromium_stderr')),
        _tail_text(attempt.get('stderr')),
    ]
    stderr_tail = '\n'.join(part for part in stderr_tail_parts if isinstance(part, str) and part.strip()) or None
    combined_tail = '\n'.join(part for part in (stderr_tail, chrome_debug_log_tail) if isinstance(part, str) and part.strip())
    interrupted = bool(attempt.get('interrupted'))
    cdp_available = bool(cdp.get('available'))
    extension_visible = bool(cdp.get('extension_visible') or cdp.get('extension_pages') or cdp.get('service_worker_seen') or cdp.get('browser_extension_pages') or cdp.get('browser_service_worker_seen'))
    early_returncode = attempt.get('returncode_early')
    browser_returncode = None
    for key, value in attempt.items():
        if key.endswith('_returncode') and value is not None:
            browser_returncode = value
            break
    crash_report_count = int(crash_reports.get('entry_count') or 0) if isinstance(crash_reports.get('entry_count'), (int, float)) else 0
    signature_tags: list[str] = []
    hints: list[str] = []
    summary = 'Browser launch evidence is incomplete; inspect the sidecar bundle directly.'
    category = 'inconclusive-launch-state'
    confidence = 'low'

    if extension_visible:
        category = 'extension-visible'
        confidence = 'high'
        summary = 'CDP saw extension targets during browser launch.'
    elif interrupted:
        category = 'launch-interrupted'
        confidence = 'high'
        summary = 'Browser launch was interrupted before the outcome stabilized.'
        hints.append('Preserve the current sidecar bundle and rerun the same launch mode on a browser-capable machine before changing flags.')
    elif cdp_available:
        category = 'cdp-up-extension-hidden'
        confidence = 'medium'
        summary = 'CDP became available, but no extension page or service worker was confirmed.'
        hints.append('Inspect Target.getTargets and the extension load flags; the browser came up, but GlassTTY did not yet prove the MV3 contexts were present.')
    elif devtools.get('exists'):
        category = 'devtools-file-present-cdp-unreachable'
        confidence = 'medium'
        summary = 'DevToolsActivePort exists, but the smoke harness did not confirm a reachable CDP session.'
        hints.append('Treat the saved DevToolsActivePort as potentially stale and compare it with the sidecar browser stderr and chrome_debug.log.')
    elif early_returncode is not None or browser_returncode is not None:
        category = 'browser-exited-before-cdp'
        confidence = 'high'
        summary = 'Browser exited before CDP became available.'
        hints.append('Check the saved browser stderr/stdout logs first; the browser quit before GlassTTY could inspect extension targets.')
    else:
        category = 'launch-incomplete-no-cdp'
        confidence = 'medium'
        summary = 'Launch never reached a confirmed CDP endpoint.'
        hints.append('Prefer the sidecar browser stderr/stdout and chrome_debug.log over generic timeout guesses.')

    lowered = combined_tail.lower()
    profile_lock_signature = any(signature.lower() in lowered for signature in BROWSER_ATTEMPT_PROFILE_LOCK_SIGNATURES)
    if profile_lock_artifacts or profile_lock_signature:
        signature_tags.append('profile-lock')
        if category in {'browser-exited-before-cdp', 'launch-incomplete-no-cdp', 'devtools-file-present-cdp-unreachable'}:
            category = 'profile-lock-or-stale-profile'
            confidence = 'medium' if not profile_lock_signature else 'high'
            summary = 'Profile-lock artifacts were present during browser startup.'
        hints.append('Use a fresh non-default user-data-dir or clean up stale Singleton* files before retrying the same launch mode.')
    if any(signature.lower() in lowered for signature in BROWSER_ATTEMPT_SANDBOX_SIGNATURES):
        signature_tags.append('sandbox')
        hints.append('This looks like a sandbox/root launch issue; keep using a disposable profile and verify the chosen browser mode still adds the expected sandbox flags.')
    if any(signature.lower() in lowered for signature in BROWSER_ATTEMPT_DISPLAY_SIGNATURES):
        signature_tags.append('display')
        hints.append('This looks display/X11-related; prefer headless Chromium or a workstation with a real display server for the next live attempt.')
    if 'devtoolsactiveport' in lowered and not devtools.get('exists'):
        signature_tags.append('missing-devtools-active-port')
        hints.append('Chrome mentions DevToolsActivePort explicitly; compare the requested remote-debugging port with the saved profile artifacts and startup log.')
    if any(signature.lower() in lowered for signature in BROWSER_ATTEMPT_CRASH_SIGNATURES) or crash_report_count:
        signature_tags.append('crash-artifacts' if crash_report_count else 'crash-signature')
        hints.append('Crash evidence exists; preserve the sidecar bundle before any cleanup so a later session can inspect the startup failure without rerunning it.')

    signals = {
        'interrupted': interrupted,
        'cdp_available': cdp_available,
        'extension_visible': extension_visible,
        'devtools_active_port_exists': bool(devtools.get('exists')),
        'devtools_port': devtools.get('port'),
        'profile_lock_artifact_count': len(profile_lock_artifacts),
        'profile_lock_artifacts': profile_lock_artifacts,
        'crash_report_count': crash_report_count,
        'returncode_early': early_returncode,
        'browser_returncode': browser_returncode,
    }
    return {
        'category': category,
        'summary': summary,
        'confidence': confidence,
        'signature_tags': signature_tags,
        'signals': signals,
        'hints': hints,
        'stderr_tail': stderr_tail,
        'chrome_debug_log_tail': chrome_debug_log_tail,
    }



def browser_attempt_artifact_dir(*, output_path: Path, sequence: int, mode: str) -> Path:
    slug = re.sub(r'[^a-zA-Z0-9._-]+', '-', mode).strip('-') or 'attempt'
    return browser_attempt_artifact_root(output_path) / f'{sequence:02d}-{slug}'



def summarize_directory_entries(path: Path, *, limit: int = 20) -> dict[str, Any]:
    summary: dict[str, Any] = {'path': str(path), 'exists': path.exists(), 'entries': [], 'entry_count': 0}
    if not path.exists():
        return summary
    try:
        items = sorted(path.iterdir(), key=lambda item: item.name)
    except Exception as exc:  # noqa: BLE001
        summary['read_error'] = str(exc)
        return summary
    summary['entry_count'] = len(items)
    for item in items[:limit]:
        entry: dict[str, Any] = {'name': item.name, 'is_dir': item.is_dir()}
        try:
            entry['size_bytes'] = item.stat().st_size
        except Exception:
            entry['size_bytes'] = None
        summary['entries'].append(entry)
    if len(items) > limit:
        summary['truncated'] = True
    return summary



def _browser_attempt_source_artifacts(profile_dir: Path, *, env: dict[str, str] | None = None) -> list[tuple[str, Path, Path]]:
    candidates = list(BROWSER_ATTEMPT_PROFILE_ARTIFACTS)
    if env and env.get('CHROME_CONFIG_HOME'):
        candidates.append(('chrome_debug_log', Path(env['CHROME_CONFIG_HOME']) / 'chrome_debug.log', Path('browser-config') / 'chrome_debug.log'))
    return [(label, source if source.is_absolute() else profile_dir / source, target) for label, source, target in candidates]



def snapshot_browser_attempt_artifacts(*, attempt: dict[str, Any], artifact_dir: Path, profile_dir: Path, env: dict[str, str] | None = None, stage: str) -> dict[str, Any]:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    copied: list[dict[str, Any]] = []
    for label, source, relative_target in _browser_attempt_source_artifacts(profile_dir, env=env):
        target = artifact_dir / relative_target
        entry: dict[str, Any] = {'label': label, 'source_path': str(source), 'copied_path': str(target), 'exists': source.exists(), 'copied': False}
        if source.exists() and source.is_file():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            entry['copied'] = True
            entry['size_bytes'] = target.stat().st_size
        copied.append(entry)
    crash_reports = None
    if env and env.get('CHROME_CONFIG_HOME'):
        crash_reports = summarize_directory_entries(Path(env['CHROME_CONFIG_HOME']) / 'Crash Reports')
    snapshot = {
        'captured_at': utc_now(),
        'stage': stage,
        'artifact_dir': str(artifact_dir),
        'attempt': _json_safe(attempt),
        'profile_dir': str(profile_dir),
        'devtools_active_port': parse_devtools_active_port(profile_dir),
        'copied_artifacts': copied,
        'crash_reports': crash_reports,
    }
    snapshot['diagnosis'] = diagnose_browser_attempt_snapshot(snapshot)
    write_json_atomic(artifact_dir / 'attempt.json', snapshot)
    return snapshot



def browser_env(temp_home: Path) -> dict[str, str]:
    env = dict(os.environ)
    env['HOME'] = str(temp_home)
    env['XDG_CONFIG_HOME'] = str(temp_home / '.config')
    env['XDG_CACHE_HOME'] = str(temp_home / '.cache')
    env['XDG_RUNTIME_DIR'] = str(temp_home / '.runtime')
    env['CHROME_CONFIG_HOME'] = str(Path(env['XDG_CONFIG_HOME']) / 'chromium')
    env['PYTHONPATH'] = os.pathsep.join([str(ROOT), str(ROOT / 'daemon' / 'src')] + ([env['PYTHONPATH']] if env.get('PYTHONPATH') else []))
    env['GLASSTTY_HOME'] = str(temp_home / '.local' / 'share' / 'glasstty')
    if not env.get('PLAYWRIGHT_BROWSERS_PATH'):
        browsers_root = existing_playwright_browsers_path(env=env)
        if browsers_root:
            env['PLAYWRIGHT_BROWSERS_PATH'] = str(browsers_root)
    for candidate in (
        Path(env['XDG_CONFIG_HOME']),
        Path(env['XDG_CACHE_HOME']),
        Path(env['XDG_RUNTIME_DIR']),
        Path(env['CHROME_CONFIG_HOME']),
        Path(env['CHROME_CONFIG_HOME']) / 'Crash Reports',
    ):
        candidate.mkdir(parents=True, exist_ok=True)
    return env


def probe_url(extension_id: str, fixture_url: str | None = None, write_text: str | None = DEFAULT_WRITE_TEXT, autorun: bool = True) -> str:
    query_params: dict[str, str] = {}
    if autorun:
        query_params['run'] = '1'
    if fixture_url:
        query_params['fixture'] = fixture_url
    if write_text is not None:
        query_params['write'] = write_text
    query = urllib.parse.urlencode(query_params)
    base = f'chrome-extension://{extension_id}/probe/index.html'
    return f'{base}?{query}' if query else base


def extract_probe_page_result(page: Any, *, timeout: float, screenshot_path: Path | None = None) -> tuple[dict[str, Any], dict[str, Any]]:
    page.wait_for_selector('body[data-probe-ready="1"]', timeout=max(1, int(timeout * 1000)))
    result = page.evaluate("() => ({ ready: document.body?.dataset?.probeReady ?? null, ok: document.body?.dataset?.probeOk ?? null, summary: document.getElementById('summary')?.textContent ?? '', json: document.getElementById('probe-json')?.textContent ?? '' })")
    if screenshot_path:
        screenshot_path.parent.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(screenshot_path), full_page=True)
    parsed_json: dict[str, Any] = {}
    raw_json = result.get('json') if isinstance(result, dict) else None
    if isinstance(raw_json, str) and raw_json.strip():
        parsed_json = json.loads(raw_json)
    return result if isinstance(result, dict) else {}, parsed_json


def open_probe_page(context: Any, *, extension_id: str, timeout: float, fixture_url: str | None = None, write_text: str | None = DEFAULT_WRITE_TEXT, screenshot_path: Path | None = None) -> tuple[Any, dict[str, Any], dict[str, Any], list[dict[str, str]]]:
    page = context.new_page()
    console_messages: list[dict[str, str]] = []

    def on_console(message: Any) -> None:
        console_messages.append({'type': getattr(message, 'type', '<unknown>'), 'text': message.text})

    if hasattr(page, 'on'):
        page.on('console', on_console)
    page.goto(probe_url(extension_id, fixture_url, write_text=write_text), wait_until='load', timeout=max(1, int(timeout * 1000)))
    result, parsed_json = extract_probe_page_result(page, timeout=timeout, screenshot_path=screenshot_path)
    return page, result, parsed_json, console_messages


def stop_extension_service_worker_playwright(browser: Any, *, extension_id: str, timeout: float = 3.0) -> dict[str, Any]:
    report: dict[str, Any] = {
        'extension_id': extension_id,
        'closed': False,
        'error': None,
        'matched_targets': [],
        'targets': [],
    }
    session = None
    try:
        session = browser.new_browser_cdp_session()
        targets = session.send('Target.getTargets')
        target_infos = targets.get('targetInfos') if isinstance(targets, dict) else None
        if not isinstance(target_infos, list):
            target_infos = targets.get('target_infos') if isinstance(targets, dict) else None
        if not isinstance(target_infos, list):
            target_infos = []
        prefix = extension_url_prefix(extension_id)
        selected: dict[str, Any] | None = None
        for item in target_infos:
            if not isinstance(item, dict):
                continue
            normalized = {
                'targetId': item.get('targetId') or item.get('target_id'),
                'type': item.get('type'),
                'url': item.get('url'),
                'title': item.get('title'),
                'attached': item.get('attached'),
            }
            report['targets'].append(normalized)
            if normalized.get('type') == 'service_worker' and str(normalized.get('url') or '').startswith(prefix):
                report['matched_targets'].append(normalized)
                if selected is None:
                    selected = normalized
        if selected is None:
            report['error'] = f'extension service worker target not found for {extension_id}'
            return report
        if not selected.get('targetId'):
            report['error'] = 'matching extension service worker target is missing targetId'
            return report
        close_result = session.send('Target.closeTarget', {'targetId': selected['targetId']})
        report['close_result'] = close_result
        report['closed_target_id'] = selected['targetId']
        report['closed'] = bool((close_result or {}).get('success', True))
        return report
    except Exception as exc:  # noqa: BLE001
        report['error'] = str(exc)
        return report
    finally:
        if session is not None:
            detach = getattr(session, 'detach', None)
            if callable(detach):
                try:
                    detach()
                except Exception:
                    pass


def _resume_probe_bits(probe_json: dict[str, Any] | None) -> dict[str, Any]:
    bridge = probe_json.get('bridge') if isinstance(probe_json, dict) else None
    status = bridge.get('status') if isinstance(bridge, dict) else None
    persistent = status.get('persistentDiagnostics') if isinstance(status, dict) else None
    runtime_hint = persistent.get('runtimeHint') if isinstance(persistent, dict) and isinstance(persistent.get('runtimeHint'), dict) else {}
    worker_boots = persistent.get('workerBoots') if isinstance(persistent, dict) and isinstance(persistent.get('workerBoots'), list) else []
    current_boot_id = persistent.get('currentBootId') if isinstance(persistent, dict) else None
    boot_count = None
    if isinstance(worker_boots, list):
        boot_counts = [item.get('bootCount') for item in worker_boots if isinstance(item, dict) and isinstance(item.get('bootCount'), (int, float))]
        if boot_counts:
            boot_count = int(max(boot_counts))
        if current_boot_id is None:
            for item in reversed(worker_boots):
                if isinstance(item, dict) and item.get('bootId'):
                    current_boot_id = item.get('bootId')
                    break
    native = status.get('nativeConnection') if isinstance(status, dict) and isinstance(status.get('nativeConnection'), dict) else {}
    return {
        'current_boot_id': current_boot_id,
        'boot_count': boot_count,
        'worker_boot_count': len(worker_boots),
        'runtime_hint_status': runtime_hint.get('status'),
        'runtime_hint_summary': runtime_hint.get('summary'),
        'persistent_connected': bool(native.get('connected')),
        'oneshot_ok': bool(native.get('lastOneShotProbeOk')),
    }


def _resume_context_bits(probe_json: dict[str, Any] | None) -> dict[str, Any]:
    bridge = probe_json.get('bridge') if isinstance(probe_json, dict) else {}
    contexts = bridge.get('contexts') if isinstance(bridge, dict) and isinstance(bridge.get('contexts'), dict) else {}
    open_contexts = contexts.get('openContexts') if isinstance(contexts, dict) and isinstance(contexts.get('openContexts'), list) else []
    context_types = [context.get('contextType') for context in open_contexts if isinstance(context, dict)]
    return {
        'available': bool(isinstance(contexts, dict) and contexts.get('hasRuntimeGetContexts')),
        'runtime_id': contexts.get('runtimeId') if isinstance(contexts, dict) else None,
        'background_context_seen': 'BACKGROUND' in context_types,
        'offscreen_context_count': sum(1 for value in context_types if value == 'OFFSCREEN_DOCUMENT'),
        'side_panel_context_count': sum(1 for value in context_types if value == 'SIDE_PANEL'),
        'context_type_counts': {value: context_types.count(value) for value in sorted({value for value in context_types if isinstance(value, str)})},
    }


def worker_resume_summary(before_probe_json: dict[str, Any] | None, after_probe_json: dict[str, Any] | None) -> dict[str, Any]:
    before = _resume_probe_bits(before_probe_json)
    after = _resume_probe_bits(after_probe_json)
    before_contexts = _resume_context_bits(before_probe_json)
    after_contexts = _resume_context_bits(after_probe_json)
    boot_changed = bool(before.get('current_boot_id') and after.get('current_boot_id') and before['current_boot_id'] != after['current_boot_id'])
    before_count = before.get('boot_count')
    after_count = after.get('boot_count')
    boot_count_increased = isinstance(before_count, int) and isinstance(after_count, int) and after_count > before_count
    native_recovered = bool(after.get('persistent_connected') or after.get('oneshot_ok'))
    context_evidence_available = bool(before_contexts.get('available') and after_contexts.get('available'))
    runtime_id_stable = bool(before_contexts.get('runtime_id') and after_contexts.get('runtime_id') and before_contexts['runtime_id'] == after_contexts['runtime_id'])
    background_context_recovered = bool(after_contexts.get('background_context_seen'))
    offscreen_context_stable = None
    if context_evidence_available:
        offscreen_context_stable = bool(after_contexts.get('offscreen_context_count', 0) >= before_contexts.get('offscreen_context_count', 0))
    context_proof_ok = True if not context_evidence_available else bool(runtime_id_stable and background_context_recovered)
    ok = bool(boot_changed and boot_count_increased and native_recovered and context_proof_ok)
    proof_grade = 'failed'
    if ok and context_evidence_available:
        proof_grade = 'strict_context_recovery'
    elif ok:
        proof_grade = 'legacy_boot_and_native_only'
    return {
        'before': before,
        'after': after,
        'before_contexts': before_contexts,
        'after_contexts': after_contexts,
        'boot_changed': boot_changed,
        'boot_count_increased': boot_count_increased,
        'native_recovered': native_recovered,
        'context_evidence_available': context_evidence_available,
        'runtime_id_stable': runtime_id_stable if context_evidence_available else None,
        'background_context_recovered': background_context_recovered if context_evidence_available else None,
        'offscreen_context_stable': offscreen_context_stable,
        'proof_grade': proof_grade,
        'ok': ok,
    }


def _base_browser_args(*, chromium: str, extension_dir: Path, profile_dir: Path, start_url: str, remote_debugging_port: int) -> list[str]:
    browser_args = [
        chromium,
        f'--user-data-dir={profile_dir}',
        f'--remote-debugging-port={remote_debugging_port}',
        '--remote-allow-origins=*',
        f'--disable-extensions-except={extension_dir}',
        f'--load-extension={extension_dir}',
        '--no-first-run',
        '--no-default-browser-check',
        '--disable-gpu',
        '--disable-dev-shm-usage',
        '--noerrdialogs',
    ]
    if os.geteuid() == 0:
        browser_args.append('--no-sandbox')
    browser_args.append(start_url)
    return browser_args


def browser_launch_commands(*, chromium: str, extension_dir: Path, profile_dir: Path, start_url: str, remote_debugging_port: int, mode: str) -> list[tuple[str, list[str]]]:
    browser_args = _base_browser_args(
        chromium=chromium,
        extension_dir=extension_dir,
        profile_dir=profile_dir,
        start_url=start_url,
        remote_debugging_port=remote_debugging_port,
    )
    xvfb = shutil.which('xvfb-run') or 'xvfb-run'
    if mode == 'headed':
        return [('headed', browser_args)]
    if mode == 'headless-new':
        return [('headless-new', [*browser_args, '--headless=new'])]
    if mode == 'xvfb':
        return [('xvfb', [xvfb, '-a', *browser_args])]
    if mode == 'auto':
        return [
            ('headless-new', [*browser_args, '--headless=new']),
            ('xvfb', [xvfb, '-a', *browser_args]),
        ]
    raise ValueError(f'unsupported browser mode: {mode}')


def browser_launch_command(*, chromium: str, extension_dir: Path, profile_dir: Path, start_url: str, remote_debugging_port: int, headed: bool, browser_mode: str = 'auto') -> list[str]:
    mode = 'headed' if headed else browser_mode
    return browser_launch_commands(
        chromium=chromium,
        extension_dir=extension_dir,
        profile_dir=profile_dir,
        start_url=start_url,
        remote_debugging_port=remote_debugging_port,
        mode=mode,
    )[0][1]


def probe_cdp(*, port: int, extension_id: str | None, timeout: float) -> dict[str, Any]:
    watch_seconds = min(1.25, max(0.0, timeout))
    attach_seconds = min(1.25, max(0.0, timeout))
    return inspect_cdp(port=port, extension_id=extension_id, timeout=1.0, wait=timeout, watch=watch_seconds, attach=attach_seconds)


def stop_process(proc: subprocess.Popen[str], *, name: str, report: dict[str, Any]) -> None:
    stdout = ''
    stderr = ''
    try:
        if proc.poll() is None:
            proc.terminate()
            try:
                stdout, stderr = proc.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                try:
                    stdout, stderr = proc.communicate(timeout=5)
                except subprocess.TimeoutExpired:
                    stdout = '<process stdout unavailable after forced kill>'
                    stderr = '<process stderr unavailable after forced kill>'
        else:
            try:
                stdout, stderr = proc.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                stdout = '<process stdout unavailable after exit>'
                stderr = '<process stderr unavailable after exit>'
    finally:
        report[f'{name}_returncode'] = proc.returncode
        report[f'{name}_stdout'] = stdout
        report[f'{name}_stderr'] = stderr
        artifact_dir_value = report.get('artifact_dir') if isinstance(report, dict) else None
        if isinstance(artifact_dir_value, str) and artifact_dir_value:
            artifact_dir = Path(artifact_dir_value)
            artifact_dir.mkdir(parents=True, exist_ok=True)
            stdout_path = artifact_dir / f'{name}-stdout.log'
            stderr_path = artifact_dir / f'{name}-stderr.log'
            stdout_path.write_text(stdout, encoding='utf-8')
            stderr_path.write_text(stderr, encoding='utf-8')
            report[f'{name}_stdout_path'] = str(stdout_path)
            report[f'{name}_stderr_path'] = str(stderr_path)


def _remote_debugging_port_from_command(argv: list[str]) -> int:
    for arg in argv:
        if arg.startswith('--remote-debugging-port='):
            return int(arg.split('=', 1)[1])
    raise ValueError('remote debugging port missing from browser command')


def launch_browser_probe(*, launch_cmd: list[str], extension_id: str | None, timeout: float, env: dict[str, str]) -> tuple[subprocess.Popen[str], dict[str, Any]]:
    browser = subprocess.Popen(launch_cmd, cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    deadline = time.time() + timeout
    last_cdp: dict[str, Any] = {
        'port': _remote_debugging_port_from_command(launch_cmd),
        'available': False,
        'browser_version': None,
        'targets': [],
        'target_count': 0,
        'extension_id': extension_id,
        'extension_targets': [],
        'service_worker_seen': False,
        'page_targets': [],
        'extension_pages': [],
    }
    while time.time() < deadline:
        rc = browser.poll()
        if rc is not None:
            last_cdp['last_error'] = f'browser exited before CDP became available (returncode={rc})'
            return browser, last_cdp
        last_cdp = probe_cdp(port=_remote_debugging_port_from_command(launch_cmd), extension_id=extension_id, timeout=1.5)
        if last_cdp.get('available'):
            return browser, last_cdp
        time.sleep(0.4)
    if not last_cdp.get('last_error'):
        last_cdp['last_error'] = f'CDP was not reachable within {timeout} seconds'
    return browser, last_cdp


def wait_for_probe_result(*, port: int, extension_id: str, timeout: float) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    prefix = extension_url_prefix(extension_id)
    deadline = time.time() + timeout
    last_error: str | None = None
    while time.time() < deadline:
        snapshot = inspect_cdp(port=port, extension_id=extension_id, timeout=1.0, wait=1.0)
        target = choose_target(snapshot.get('extension_pages') or [], target_type='page', url_prefix=f'{prefix}probe/index.html')
        if not target and snapshot.get('extension_pages'):
            target = choose_target(snapshot['extension_pages'], target_type='page', url_prefix=prefix)
        if target and target.get('webSocketDebuggerUrl'):
            try:
                evaluation = evaluate_target(
                    str(target['webSocketDebuggerUrl']),
                    "(() => ({ ready: document.body?.dataset?.probeReady ?? null, ok: document.body?.dataset?.probeOk ?? null, summary: document.getElementById('summary')?.textContent ?? '', json: document.getElementById('probe-json')?.textContent ?? '' }))()",
                    timeout=2.5,
                )
                result = (((evaluation.get('result') or {}).get('result') or {}).get('value') or {})
                if result.get('ready') == '1':
                    parsed_json: dict[str, Any] | None = None
                    raw_json = result.get('json')
                    if isinstance(raw_json, str) and raw_json.strip():
                        try:
                            parsed_json = json.loads(raw_json)
                        except json.JSONDecodeError as exc:
                            last_error = f'probe JSON did not parse: {exc}'
                    return target, result, parsed_json or {}
            except Exception as exc:  # noqa: BLE001
                last_error = str(exc)
        time.sleep(0.25)
    raise RuntimeError(f'probe page never reached data-probe-ready=1: {last_error or "no extension probe page target observed"}')


def wait_for_probe_result_playwright(*, port: int, extension_id: str, timeout: float, screenshot_path: Path | None = None) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    report: dict[str, Any] = {
        'available': sync_playwright is not None,
        'import_error': PLAYWRIGHT_IMPORT_ERROR,
        'endpoint': f'http://127.0.0.1:{port}',
        'connected': False,
        'context_count': 0,
        'page_urls': [],
        'service_worker_urls': [],
        'screenshot_path': str(screenshot_path) if screenshot_path else None,
        'console_messages': [],
    }
    if sync_playwright is None:
        raise RuntimeError(f'playwright import unavailable: {PLAYWRIGHT_IMPORT_ERROR}')

    prefix = extension_url_prefix(extension_id)
    playwright = sync_playwright().start()
    browser = None
    try:
        connect_kwargs = connect_over_cdp_kwargs(playwright.chromium, endpoint=report['endpoint'], timeout=timeout)
        report['connect_over_cdp_kwargs'] = dict(connect_kwargs)
        endpoint = connect_kwargs.pop('endpoint_url')
        browser = playwright.chromium.connect_over_cdp(endpoint, **connect_kwargs)
        report['connected'] = True
        contexts = list(browser.contexts)
        report['context_count'] = len(contexts)
        if not contexts:
            raise RuntimeError('Playwright saw no browser contexts over CDP')
        context = contexts[0]
        attach_context_telemetry(context, report=report)
        report['page_urls'] = [page.url for page in context.pages]
        report['service_worker_urls'] = [_safe_attr(worker, 'url') for worker in _service_workers_from_context(context)]
        try:
            _worker, _snapshot, _wait_report = wait_for_healthy_extension_service_worker(
                context,
                expected_extension_id=extension_id,
                timeout=min(timeout, 3.0),
                report=report,
            )
            report['service_worker_initial_snapshot'] = _snapshot
        except Exception as exc:  # noqa: BLE001
            report['service_worker_wait_error'] = str(exc)

        page = None
        deadline = time.time() + timeout
        while time.time() < deadline and page is None:
            for candidate in context.pages:
                if candidate.url.startswith(prefix) and 'probe/index.html' in candidate.url:
                    page = candidate
                    break
            if page is None:
                report['page_urls'] = [candidate.url for candidate in context.pages]
                report['service_worker_urls'] = [_safe_attr(worker, 'url') for worker in _service_workers_from_context(context)]
                time.sleep(0.2)
        if page is None:
            raise RuntimeError(f"Playwright never observed the probe page; saw pages={report['page_urls']}")

        console_messages: list[dict[str, str]] = []

        def on_console(message: Any) -> None:
            console_messages.append({'type': getattr(message, 'type', '<unknown>'), 'text': message.text})

        page.on('console', on_console)
        page.wait_for_selector('body[data-probe-ready="1"]', timeout=max(1, int(timeout * 1000)))
        result = page.evaluate("() => ({ ready: document.body?.dataset?.probeReady ?? null, ok: document.body?.dataset?.probeOk ?? null, summary: document.getElementById('summary')?.textContent ?? '', json: document.getElementById('probe-json')?.textContent ?? '' })")
        if screenshot_path:
            screenshot_path.parent.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(screenshot_path), full_page=True)
        report['page_urls'] = [candidate.url for candidate in context.pages]
        report['service_worker_urls'] = [_safe_attr(worker, 'url') for worker in _service_workers_from_context(context)]
        report['console_messages'] = console_messages
        target = {'type': 'page', 'url': page.url, 'title': page.title()}
        parsed_json: dict[str, Any] = {}
        raw_json = result.get('json') if isinstance(result, dict) else None
        if isinstance(raw_json, str) and raw_json.strip():
            parsed_json = json.loads(raw_json)
        return target, result if isinstance(result, dict) else {}, parsed_json, report
    finally:
        # Intentionally do not stop the Playwright driver here: in this helper we
        # are attached to a live Chromium instance over CDP and stopping the driver
        # can stall or tear down the browser before the CLI/native-host proof runs.
        pass


def launch_playwright_extension_context(*, env: dict[str, str], extension_dir: Path, profile_dir: Path, expected_extension_id: str, timeout: float, trace_path: Path | None = None, browser_install: dict[str, Any] | None = None, launch_plan: dict[str, Any] | None = None) -> tuple[Any, dict[str, Any], Callable[[], None]]:
    browser_install = browser_install or discover_playwright_browser_install(
        env=env,
        playwright_available=sync_playwright is not None,
        import_error=PLAYWRIGHT_IMPORT_ERROR,
    )
    launch_plan = launch_plan or playwright_extension_launch_plan(env=env, browser_install=browser_install)
    report: dict[str, Any] = {
        'available': sync_playwright is not None,
        'import_error': PLAYWRIGHT_IMPORT_ERROR,
        'browser_install': browser_install,
        'launch_plan': launch_plan,
        'launch_strategy': None,
        'launched': False,
        'expected_extension_id': expected_extension_id,
        'service_worker_urls': [],
        'page_urls': [],
        'trace': {
            'requested_path': str(trace_path) if trace_path else None,
            'started': False,
            'saved': False,
            'exists': False,
            'error': None,
            'enabled': False,
        },
        'console_messages': [],
    }
    if sync_playwright is None:
        raise RuntimeError(f'playwright import unavailable: {PLAYWRIGHT_IMPORT_ERROR}')
    if not launch_plan.get('strategy'):
        raise RuntimeError('; '.join(launch_plan.get('notes') or [launch_plan.get('skip_reason') or 'playwright persistent launch is unavailable']))

    launch_args = [
        f'--disable-extensions-except={extension_dir}',
        f'--load-extension={extension_dir}',
        '--disable-gpu',
        '--disable-dev-shm-usage',
        '--noerrdialogs',
    ]
    if os.geteuid() == 0:
        launch_args.append('--no-sandbox')

    launch_kwargs: dict[str, Any] = {
        'user_data_dir': str(profile_dir),
        'headless': True,
        'args': launch_args,
        'env': env,
        'timeout': max(1, int(timeout * 1000)),
    }
    if launch_plan.get('strategy') == 'playwright-channel':
        launch_kwargs['channel'] = str(launch_plan.get('channel') or 'chromium')
        report['launch_strategy'] = 'playwright-channel'
        report['launch_channel'] = launch_kwargs['channel']
        report['bundled_install'] = browser_install.get('bundled_install')
    elif launch_plan.get('strategy') == 'bundled-executable':
        launch_kwargs['executable_path'] = str(browser_install['bundled_executable'])
        report['launch_strategy'] = 'bundled-executable'
        report['bundled_install'] = browser_install.get('bundled_install')
    elif launch_plan.get('strategy') == 'system-executable':
        launch_kwargs['executable_path'] = str(browser_install['system_chromium'])
        report['launch_strategy'] = 'system-executable'
        report['risky_fallback'] = True
    else:
        raise RuntimeError('no Playwright launch strategy is available for persistent launch')

    playwright = sync_playwright().start()
    context = None
    closed = False
    trace_started = False

    def cleanup() -> None:
        nonlocal closed, context, playwright, trace_started
        if closed:
            return
        closed = True
        if context is not None and trace_started and trace_path is not None:
            try:
                trace_path.parent.mkdir(parents=True, exist_ok=True)
                context.tracing.stop(path=str(trace_path))
                report['trace']['saved'] = True
                report['trace']['exists'] = trace_path.exists()
            except Exception as exc:  # noqa: BLE001
                report['trace']['error'] = str(exc)
        if context is not None:
            context.close()
        playwright.stop()

    try:
        context = playwright.chromium.launch_persistent_context(**launch_kwargs)
        attach_context_telemetry(context, report=report)
        report['launched'] = True
        if trace_path is not None:
            trace_path.parent.mkdir(parents=True, exist_ok=True)
            context.tracing.start(screenshots=True, snapshots=True, sources=True)
            trace_started = True
            report['trace']['started'] = True
            report['trace']['enabled'] = True
        service_workers = _service_workers_from_context(context)
        if not service_workers and hasattr(context, 'wait_for_event'):
            try:
                context.wait_for_event('serviceworker', timeout=max(1, int(timeout * 1000)))
            except Exception:
                pass
        service_worker, service_worker_snapshot, _service_worker_wait = wait_for_healthy_extension_service_worker(
            context,
            expected_extension_id=expected_extension_id,
            timeout=timeout,
            report=report,
        )
        report['service_worker_urls'] = [_safe_attr(worker, 'url') for worker in _service_workers_from_context(context)]
        report['service_worker_initial_snapshot'] = service_worker_snapshot
        observed_extension_id = _extension_id_from_worker(service_worker) or ''
        report['observed_extension_id'] = observed_extension_id
        report['extension_id_matches_expected'] = observed_extension_id == expected_extension_id
        report['page_urls'] = [candidate.url for candidate in context.pages]
        return context, report, cleanup
    except Exception:
        cleanup()
        raise


def attach_playwright_extension_context(*, cdp_endpoint: str, expected_extension_id: str, timeout: float, trace_path: Path | None = None) -> tuple[Any, dict[str, Any], Callable[[], None]]:
    report: dict[str, Any] = {'available': sync_playwright is not None, 'import_error': PLAYWRIGHT_IMPORT_ERROR, 'launch_strategy': 'cdp-attach', 'attached_endpoint': cdp_endpoint, 'connected': False, 'context_count': 0, 'expected_extension_id': expected_extension_id, 'service_worker_urls': [], 'page_urls': [], 'trace': {'requested_path': str(trace_path) if trace_path else None, 'started': False, 'saved': False, 'exists': False, 'error': None, 'enabled': False}, 'console_messages': []}
    if sync_playwright is None:
        raise RuntimeError(f'playwright import unavailable: {PLAYWRIGHT_IMPORT_ERROR}')
    playwright = sync_playwright().start()
    context = None
    closed = False
    trace_started = False
    def cleanup() -> None:
        nonlocal closed, trace_started
        if closed:
            return
        closed = True
        if context is not None and trace_started and trace_path is not None:
            try:
                trace_path.parent.mkdir(parents=True, exist_ok=True)
                context.tracing.stop(path=str(trace_path))
                report['trace']['saved'] = True
                report['trace']['exists'] = trace_path.exists()
            except Exception as exc:  # noqa: BLE001
                report['trace']['error'] = str(exc)
        try:
            playwright.stop()
        except Exception:
            pass
    try:
        connect_kwargs = connect_over_cdp_kwargs(playwright.chromium, endpoint=cdp_endpoint, timeout=timeout)
        report['connect_over_cdp_kwargs'] = dict(connect_kwargs)
        endpoint = connect_kwargs.pop('endpoint_url')
        browser = playwright.chromium.connect_over_cdp(endpoint, **connect_kwargs)
        report['connected'] = True
        contexts = list(browser.contexts)
        report['context_count'] = len(contexts)
        if not contexts:
            raise RuntimeError('Playwright saw no browser contexts over CDP')
        context = contexts[0]
        attach_context_telemetry(context, report=report)
        if trace_path is not None:
            trace_path.parent.mkdir(parents=True, exist_ok=True)
            context.tracing.start(screenshots=True, snapshots=True, sources=True)
            trace_started = True
            report['trace']['started'] = True
            report['trace']['enabled'] = True
        service_worker, service_worker_snapshot, _service_worker_wait = wait_for_healthy_extension_service_worker(context, expected_extension_id=expected_extension_id, timeout=timeout, report=report)
        report['service_worker_urls'] = [_safe_attr(worker, 'url') for worker in _service_workers_from_context(context)]
        report['service_worker_initial_snapshot'] = service_worker_snapshot
        observed_extension_id = _extension_id_from_worker(service_worker) or ''
        report['observed_extension_id'] = observed_extension_id
        report['extension_id_matches_expected'] = observed_extension_id == expected_extension_id
        report['page_urls'] = [candidate.url for candidate in context.pages]
        return context, report, cleanup
    except Exception:
        cleanup()
        raise


def launch_playwright_persistent_probe(*, env: dict[str, str], extension_dir: Path, profile_dir: Path, expected_extension_id: str, fixture_url: str, timeout: float, screenshot_path: Path | None = None, trace_path: Path | None = None, browser_install: dict[str, Any] | None = None, launch_plan: dict[str, Any] | None = None) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], Callable[[], None]]:
    context, report, cleanup = launch_playwright_extension_context(
        env=env,
        extension_dir=extension_dir,
        profile_dir=profile_dir,
        expected_extension_id=expected_extension_id,
        timeout=timeout,
        trace_path=trace_path,
        browser_install=browser_install,
        launch_plan=launch_plan,
    )
    try:
        observed_extension_id = str(report.get('observed_extension_id') or expected_extension_id)
        page, result, parsed_json, console_messages = open_probe_page(
            context,
            extension_id=observed_extension_id,
            timeout=timeout,
            fixture_url=fixture_url,
            write_text=DEFAULT_WRITE_TEXT,
            screenshot_path=screenshot_path,
        )
        report['page_urls'] = [candidate.url for candidate in context.pages]
        report['service_worker_urls'] = [_safe_attr(worker, 'url') for worker in _service_workers_from_context(context)]
        report['console_messages'] = console_messages
        target = {'type': 'page', 'url': page.url, 'title': page.title()}
        return target, result, parsed_json, report, cleanup
    except Exception:
        cleanup()
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description='Run an honest best-effort GlassTTY fixture-lab browser smoke and capture diagnostics.')
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--timeout', type=float, default=25.0)
    parser.add_argument('--output', required=True)
    parser.add_argument('--headed', action='store_true')
    parser.add_argument('--browser-mode', choices=['auto', 'headless-new', 'xvfb', 'headed'], default='auto')
    parser.add_argument('--ensure-playwright-channel-ready', choices=['never', 'if-needed', 'always'], default='if-needed')
    args = parser.parse_args()

    browser_mode = 'headed' if args.headed else args.browser_mode
    output_path = Path(args.output).resolve()
    report: dict[str, Any] = {
        'ok': False,
        'timestamp': utc_now(),
        'output_path': str(output_path),
        'fixture_lab_url': f'http://127.0.0.1:{args.port}/',
        'steps': [],
        'events': [],
        'browser_mode_requested': browser_mode,
        'browser_attempts': [],
        'playwright': {'available': sync_playwright is not None, 'import_error': PLAYWRIGHT_IMPORT_ERROR},
        'setup': {'actions': [], 'playwright_channel_policy': args.ensure_playwright_channel_ready, 'replay_script_path': None},
    }

    atexit_state = {'enabled': True}

    def _atexit_checkpoint() -> None:
        if not atexit_state['enabled']:
            return
        try:
            checkpoint_report(report, output_path, phase=str(report.get('phase') or 'exiting'), note='atexit checkpoint', event={'kind': 'atexit'})
        except Exception:
            pass

    atexit.register(_atexit_checkpoint)
    restore_signal_handlers, _signal_handlers = install_termination_checkpoint(report, output_path)
    checkpoint_report(report, output_path, phase='starting', note='initialized smoke report')

    temp_root = Path(tempfile.mkdtemp(prefix='glasstty-e2e-'))
    report['temp_root'] = str(temp_root)
    checkpoint_report(report, output_path, phase='starting', note='temporary workspace created')
    temp_home = temp_root / 'home'
    temp_home.mkdir(parents=True, exist_ok=True)
    env = browser_env(temp_home)
    playwright_dry_run_timeout = max(1.0, min(4.0, args.timeout / 8.0))
    env.setdefault(PLAYWRIGHT_DRY_RUN_TIMEOUT_ENV, f'{playwright_dry_run_timeout:.1f}')
    report['playwright']['dry_run_timeout_seconds'] = float(env.get(PLAYWRIGHT_DRY_RUN_TIMEOUT_ENV) or playwright_dry_run_timeout)
    report['playwright']['browser_install'] = discover_playwright_browser_install(
        env=env,
        playwright_available=sync_playwright is not None,
        import_error=PLAYWRIGHT_IMPORT_ERROR,
        dry_run_timeout=report['playwright']['dry_run_timeout_seconds'],
    )
    report['playwright']['launch_plan'] = playwright_extension_launch_plan(env=env, browser_install=report['playwright']['browser_install'])
    report['playwright']['browser_choice'] = playwright_browser_choice(report['playwright']['browser_install'], launch_plan=report['playwright']['launch_plan'])
    report['browser_env'] = {key: env[key] for key in ('HOME', 'XDG_CONFIG_HOME', 'XDG_CACHE_HOME', 'XDG_RUNTIME_DIR', 'CHROME_CONFIG_HOME', 'GLASSTTY_HOME', 'PLAYWRIGHT_BROWSERS_PATH', PLAYWRIGHT_DRY_RUN_TIMEOUT_ENV) if key in env}
    report['launcher'] = {'euid': os.geteuid(), 'python': sys.executable}
    append_step(report, 'playwright_browser_discovery')
    checkpoint_report(report, output_path, phase='environment_ready', note='browser environment prepared')
    fixture_proc: subprocess.Popen[str] | None = None
    browser: subprocess.Popen[str] | None = None
    active_browser_process: subprocess.Popen[str] | None = None
    active_browser_attempt: dict[str, Any] | None = None
    playwright_cleanup: Callable[[], None] | None = None
    browser_attempt_sequence = 0

    try:
        report['doctor'] = json.loads(run([sys.executable, str(DOCTOR_SCRIPT)], env=env).stdout)
        append_step(report, 'doctor')
        playwright_channel_prepare = append_setup_action(
            report,
            planned_playwright_channel_prepare(report.get('playwright'), policy=args.ensure_playwright_channel_ready),
        )
        report['playwright']['channel_prepare'] = playwright_channel_prepare
        if playwright_channel_prepare.get('will_run'):
            checkpoint_report(report, output_path, phase='playwright_channel_preparing', note='running Playwright channel-ready recovery before smoke')
            prepare_record = run_command_record(
                [sys.executable, str(ROOT / 'scripts' / 'playwright-browsers.py'), 'ensure-channel-ready'],
                env=env,
                timeout=max(60.0, args.timeout * 4),
            )
            playwright_channel_prepare.update(prepare_record)
            playwright_channel_prepare['executed'] = True
            if prepare_record.get('ok'):
                append_step(report, 'playwright_channel_ready_prepared')
                report['playwright']['browser_install'] = discover_playwright_browser_install(
                    env=env,
                    playwright_available=sync_playwright is not None,
                    import_error=PLAYWRIGHT_IMPORT_ERROR,
                    dry_run_timeout=report['playwright']['dry_run_timeout_seconds'],
                )
                report['playwright']['launch_plan'] = playwright_extension_launch_plan(env=env, browser_install=report['playwright']['browser_install'])
                report['playwright']['browser_choice'] = playwright_browser_choice(report['playwright']['browser_install'], launch_plan=report['playwright']['launch_plan'])
                playwright_channel_prepare['channel_ready_after'] = bool((report['playwright']['launch_plan'] or {}).get('channel_ready'))
                playwright_channel_prepare['cache_alignment_status_after'] = (report['playwright']['launch_plan'] or {}).get('cache_alignment_status')
                checkpoint_report(report, output_path, phase='playwright_channel_prepared', note='Playwright channel-ready recovery finished')
            else:
                append_step(report, 'playwright_channel_ready_prepare_failed')
                checkpoint_report(report, output_path, phase='playwright_channel_prepare_failed', note='Playwright channel-ready recovery failed; smoke will continue with the pre-existing browser plan')
        browser_choice = discover_browser_executable(env=env)
        report['browser_choice'] = browser_choice
        checkpoint_report(report, output_path, phase='doctor_complete', note='doctor report captured')
        make_tree_writable(EXTENSION_DIR / 'dist')
        try:
            run(['npm', 'run', 'build'], cwd=EXTENSION_DIR, env=env)
            append_step(report, 'extension_build')
            report['extension_build'] = {'ok': True, 'fallback_used': False}
        except Exception as exc:  # noqa: BLE001
            if extension_dist_ready(EXTENSION_DIR):
                append_step(report, 'extension_build_fallback_ready')
                report['extension_build'] = {'ok': True, 'fallback_used': True, 'warning': str(exc)}
            else:
                raise
        checkpoint_report(report, output_path, phase='extension_ready', note='extension bundle ready for smoke run')
        for helper_script in (WRAPPER_PATH, INSTALL_NATIVE_HOST):
            if helper_script.exists():
                try:
                    helper_script.chmod(0o755)
                except PermissionError:
                    pass
        install_targets = native_host_install_targets(browser_choice, report['playwright'].get('browser_choice') if isinstance(report.get('playwright'), dict) else None)
        native_host_installs: list[dict[str, Any]] = []
        for target_name in install_targets:
            install_argv = [str(INSTALL_NATIVE_HOST), '--target', target_name, '--extension-id', 'auto', '--host-exe', str(WRAPPER_PATH)]
            install_action = append_setup_action(report, {
                'name': f'native_host_install_{target_name}',
                'kind': 'native-host-install',
                'target': target_name,
                'command': shell_join(install_argv),
                'argv': install_argv,
                'will_run': True,
                'executed': False,
                'reason': 'Smoke installs native-host manifests for each required browser-family target before launching the bridge.',
            })
            install_record = run_command_record(install_argv, env=env, timeout=max(30.0, args.timeout * 2))
            install_action.update(install_record)
            install_action['executed'] = True
            if not install_record.get('ok'):
                raise RuntimeError(
                    f"command failed ({install_record['returncode']}): {install_record['command']}\n"
                    f"stdout:\n{install_record['stdout']}\n"
                    f"stderr:\n{install_record['stderr']}"
                )
            native_host_installs.append({
                'target': target_name,
                'command': install_record['command'],
                'stdout': str(install_record.get('stdout') or '').strip(),
                'seconds': install_record.get('seconds'),
            })
            append_step(report, f'native_host_install_{target_name}')
        report['native_host_install_targets'] = install_targets
        report['native_host_install'] = native_host_installs
        write_setup_replay_script(output_path, report)
        checkpoint_report(report, output_path, phase='native_host_ready', note='native host manifests installed for smoke environment')

        fixture_proc = subprocess.Popen(
            [sys.executable, str(FIXTURE_LAB_SCRIPT), '--host', '127.0.0.1', '--port', str(args.port)],
            cwd=ROOT,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        wait_for_http(f'http://127.0.0.1:{args.port}/manifest.json', args.timeout)
        append_step(report, 'fixture_lab_ready')
        checkpoint_report(report, output_path, phase='fixture_lab_ready', note='fixture lab server is serving manifest.json')

        chromium = browser_choice.get('path')
        if not chromium:
            raise RuntimeError('no Chromium-family browser was resolved (checked explicit env, local Chrome for Testing, and PATH)')

        profile_dir = temp_root / 'profile'
        profile_dir.mkdir(parents=True, exist_ok=True)
        extension_id = ((report.get('doctor') or {}).get('native_host') or {}).get('extension_id')
        if not extension_id:
            raise RuntimeError('doctor did not return a deterministic extension id')
        launch_url = probe_url(extension_id, f'http://127.0.0.1:{args.port}/')
        launch_candidates: list[tuple[str, list[str]]] = []
        if browser_mode == 'auto':
            for label in ('headless-new', 'xvfb'):
                launch_candidates.append((
                    label,
                    browser_launch_command(
                        chromium=chromium,
                        extension_dir=EXTENSION_DIR,
                        profile_dir=profile_dir,
                        start_url=launch_url,
                        remote_debugging_port=free_tcp_port(),
                        headed=False,
                        browser_mode=label,
                    ),
                ))
        else:
            launch_candidates.append((
                browser_mode,
                browser_launch_command(
                    chromium=chromium,
                    extension_dir=EXTENSION_DIR,
                    profile_dir=profile_dir,
                    start_url=launch_url,
                    remote_debugging_port=free_tcp_port(),
                    headed=(browser_mode == 'headed'),
                    browser_mode=browser_mode,
                ),
            ))

        report['browser'] = {
            'chromium': chromium,
            'launch_url': launch_url,
            'attempt_artifact_root': str(browser_attempt_artifact_root(output_path)),
            'candidates': [{'mode': label, 'launch_cmd': argv, 'remote_debugging_port': _remote_debugging_port_from_command(argv)} for label, argv in launch_candidates],
        }

        chosen_attempt: dict[str, Any] | None = None
        chosen_cdp: dict[str, Any] | None = None
        target: dict[str, Any]
        dom_probe: dict[str, Any]
        probe_json: dict[str, Any]
        socket_path = Path(env['GLASSTTY_HOME']) / 'run' / 'daemon.sock'
        playwright_screenshot = output_path.with_suffix('.playwright-probe.png')
        playwright_trace = output_path.with_suffix('.playwright-trace.zip')

        try:
            target, dom_probe, probe_json, persistent_report, playwright_cleanup = launch_playwright_persistent_probe(
                env=env,
                extension_dir=EXTENSION_DIR,
                profile_dir=profile_dir,
                expected_extension_id=extension_id,
                fixture_url=f'http://127.0.0.1:{args.port}/',
                timeout=min(args.timeout, 12.0),
                screenshot_path=playwright_screenshot,
                trace_path=playwright_trace,
                browser_install=report['playwright']['browser_install'],
                launch_plan=report['playwright']['launch_plan'],
            )
            report['playwright']['persistent'] = persistent_report
            report['playwright']['persistent']['ok'] = True
            report['browser_mode_selected'] = 'playwright-persistent'
            append_step(report, 'playwright_persistent_launch_selected')
            append_step(report, 'probe_page_ready_playwright_persistent')
            checkpoint_report(report, output_path, phase='probe_ready', note='Playwright persistent probe completed', event={'kind': 'probe', 'mode': 'playwright-persistent'})
        except Exception as exc:  # noqa: BLE001
            report['playwright']['persistent'] = {
                'ok': False,
                'error': str(exc),
                'browser_install': report['playwright']['browser_install'],
                'launch_plan': report['playwright']['launch_plan'],
            }
            for label, launch_cmd in launch_candidates:
                browser_attempt_sequence += 1
                attempt_artifact_dir = browser_attempt_artifact_dir(output_path=output_path, sequence=browser_attempt_sequence, mode=label)
                attempt: dict[str, Any] = {
                    'mode': label,
                    'launch_cmd': launch_cmd,
                    'remote_debugging_port': _remote_debugging_port_from_command(launch_cmd),
                    'artifact_sequence': browser_attempt_sequence,
                    'artifact_dir': str(attempt_artifact_dir),
                    'artifact_snapshot_path': str(attempt_artifact_dir / 'attempt.json'),
                    'browser_path': browser_choice.get('path'),
                    'browser_source': browser_choice.get('source'),
                    'browser_family': browser_choice.get('browser_family'),
                    'browser_version': browser_choice.get('version'),
                    'native_messaging_targets': list(browser_choice.get('native_messaging_targets') or []),
                }
                snapshot_browser_attempt_artifacts(attempt=attempt, artifact_dir=attempt_artifact_dir, profile_dir=profile_dir, env=env, stage='planned')
                active_browser_attempt = attempt
                active_browser_process = None
                mark_browser_attempt_inflight(report, attempt)
                append_step(report, f'chromium_launch_attempted_{label}')
                checkpoint_report(report, output_path, phase='browser_launching', note=f'fallback browser mode launching: {label}', event={'kind': 'browser-launch', 'mode': label})
                candidate_browser, cdp = launch_browser_probe(launch_cmd=launch_cmd, extension_id=extension_id, timeout=min(args.timeout, 8.0), env=env)
                active_browser_process = candidate_browser
                attempt['cdp'] = cdp
                attempt['returncode_early'] = candidate_browser.poll()
                attempt['browser_pid'] = candidate_browser.pid
                snapshot_browser_attempt_artifacts(attempt=attempt, artifact_dir=attempt_artifact_dir, profile_dir=profile_dir, env=env, stage='cdp-probed')
                extension_visible = bool(cdp.get('extension_visible'))
                if cdp.get('available'):
                    append_step(report, f'cdp_available_{label}')
                if cdp.get('extension_pages'):
                    append_step(report, f'extension_page_seen_{label}')
                if cdp.get('service_worker_seen'):
                    append_step(report, f'extension_service_worker_seen_{label}')
                if cdp.get('browser_extension_pages'):
                    append_step(report, f'browser_extension_page_seen_{label}')
                if cdp.get('browser_service_worker_seen'):
                    append_step(report, f'browser_extension_service_worker_seen_{label}')
                if cdp.get('browser_watch_extension_pages'):
                    append_step(report, f'browser_watch_extension_page_seen_{label}')
                if cdp.get('browser_watch_service_worker_seen'):
                    append_step(report, f'browser_watch_extension_service_worker_seen_{label}')
                if cdp.get('browser_attach_extension_pages'):
                    append_step(report, f'browser_attach_extension_page_seen_{label}')
                if cdp.get('browser_attach_service_worker_seen'):
                    append_step(report, f'browser_attach_extension_service_worker_seen_{label}')
                if cdp.get('browser_attach_runtime_id_matches_extension'):
                    append_step(report, f'browser_attach_runtime_id_match_{label}')
                browser_watch = cdp.get('browser_target_watch') if isinstance(cdp, dict) else None
                if isinstance(browser_watch, dict) and browser_watch.get('event_count'):
                    append_step(report, f'browser_target_watch_events_{label}')
                browser_attach = cdp.get('browser_target_attach') if isinstance(cdp, dict) else None
                if isinstance(browser_attach, dict) and browser_attach.get('event_count'):
                    append_step(report, f'browser_target_attach_events_{label}')
                if extension_visible:
                    browser = candidate_browser
                    chosen_attempt = attempt
                    chosen_cdp = cdp
                    report['browser_mode_selected'] = label
                    append_step(report, f'chromium_launch_selected_{label}')
                    finalize_browser_attempt(report, attempt)
                    snapshot_browser_attempt_artifacts(attempt=attempt, artifact_dir=attempt_artifact_dir, profile_dir=profile_dir, env=env, stage='selected')
                    active_browser_attempt = None
                    active_browser_process = None
                    checkpoint_report(report, output_path, phase='browser_selected', note=f'fallback browser mode selected: {label}', event={'kind': 'browser-selection', 'mode': label})
                    break
                finalize_browser_attempt(report, attempt, process=candidate_browser)
                snapshot_browser_attempt_artifacts(attempt=attempt, artifact_dir=attempt_artifact_dir, profile_dir=profile_dir, env=env, stage='finalized')
                active_browser_attempt = None
                active_browser_process = None

            if browser is None or chosen_cdp is None or not extension_id:
                raise RuntimeError('extension page or service worker was not confirmed through Playwright persistent launch or CDP in any browser mode')

            report['cdp'] = chosen_cdp
            report['browser_selected'] = chosen_attempt
            try:
                target, dom_probe, probe_json, playwright_report = wait_for_probe_result_playwright(
                    port=chosen_attempt['remote_debugging_port'],
                    extension_id=extension_id,
                    timeout=args.timeout,
                    screenshot_path=playwright_screenshot,
                )
                report['playwright'].update(playwright_report)
                report['playwright']['ok'] = True
                append_step(report, 'probe_page_ready_playwright')
                checkpoint_report(report, output_path, phase='probe_ready', note='probe page completed through Playwright CDP attach', event={'kind': 'probe', 'mode': 'playwright-cdp'})
            except Exception as exc:  # noqa: BLE001
                report['playwright']['ok'] = False
                report['playwright']['error'] = str(exc)
                target, dom_probe, probe_json = wait_for_probe_result(
                    port=chosen_attempt['remote_debugging_port'],
                    extension_id=extension_id,
                    timeout=args.timeout,
                )
                append_step(report, 'probe_page_ready_cdp')
                checkpoint_report(report, output_path, phase='probe_ready', note='probe page completed through raw CDP fallback', event={'kind': 'probe', 'mode': 'cdp'})

        socket_wait_started = time.time()
        deadline = socket_wait_started + args.timeout
        while time.time() < deadline and not socket_path.exists():
            time.sleep(0.2)
        report['socket_path'] = str(socket_path)
        report['socket_exists_after_launch'] = socket_path.exists()
        report['socket_wait_seconds'] = round(time.time() - socket_wait_started, 3)
        checkpoint_report(report, output_path, phase='bridge_wait_complete', note='socket wait finished', event={'kind': 'socket', 'exists': report['socket_exists_after_launch']})

        report['probe_target'] = target
        report['probe_dom'] = dom_probe
        report['probe_json'] = probe_json
        report['native_bootstrap'] = native_bootstrap_summary(probe_json if isinstance(probe_json, dict) else None)
        report['extension_contexts'] = extension_context_summary(probe_json if isinstance(probe_json, dict) else None, expected_extension_id=extension_id)
        if report['native_bootstrap'].get('oneshot_ok'):
            append_step(report, 'native_oneshot_probe_ok')
        if (report['extension_contexts'] or {}).get('background_context_seen'):
            append_step(report, 'probe_background_context_seen')
        if (report['extension_contexts'] or {}).get('offscreen_context_seen'):
            append_step(report, 'probe_offscreen_context_seen')
        if (report['extension_contexts'] or {}).get('runtime_id_matches_extension'):
            append_step(report, 'probe_runtime_id_matches_extension')

        fixture_payload = probe_json.get('fixture') if isinstance(probe_json, dict) else {}
        expected_prompt = fixture_payload.get('afterWritePrompt') if isinstance(fixture_payload, dict) else None
        latest_expected = fixture_payload.get('latestOutput') if isinstance(fixture_payload, dict) else None
        cli_timeout = min(CLI_TIMEOUT, max(2.0, min(args.timeout / 6.0, 4.0)))
        if not socket_path.exists():
            report['cli_proof'] = {
                'ok': False,
                'skipped': True,
                'timeout': cli_timeout,
                'steps': [],
                'errors': [f'daemon socket did not appear at {socket_path} after browser launch'],
            }
            append_step(report, 'cli_proof_skipped_no_socket')
        else:
            cli_proof = run_cli_proof(
                env=env,
                timeout=cli_timeout,
                expected_prompt=expected_prompt if isinstance(expected_prompt, str) else None,
                latest_expected=latest_expected if isinstance(latest_expected, str) else None,
                fixtures_dir=temp_root / 'cli-fixtures',
            )
            report['cli_proof'] = cli_proof
            append_step(report, 'cli_proof_complete')
        report['ok'] = bool(probe_json.get('ok')) and bool((report['cli_proof'] or {}).get('ok'))
        checkpoint_report(report, output_path, phase='cli_complete', note='CLI proof finished', event={'kind': 'cli-proof', 'ok': report['ok']})
    except Exception as exc:  # noqa: BLE001
        report['error'] = str(exc)
        checkpoint_report(report, output_path, phase='failed', note=str(exc), event={'kind': 'exception', 'error_type': type(exc).__name__})
    finally:
        if active_browser_attempt is not None:
            interruption_reason: str | None = None
            if report.get('terminated') and report.get('terminated_signal') is not None:
                interruption_reason = f"terminated by signal {report.get('terminated_signal')} during browser launch"
            elif report.get('error'):
                interruption_reason = f"aborted during browser launch: {report.get('error')}"
            finalize_browser_attempt(
                report,
                active_browser_attempt,
                process=active_browser_process,
                interrupted=True,
                interruption_reason=interruption_reason,
            )
            artifact_dir_value = active_browser_attempt.get('artifact_dir') if isinstance(active_browser_attempt, dict) else None
            if isinstance(artifact_dir_value, str) and artifact_dir_value:
                snapshot_browser_attempt_artifacts(
                    attempt=active_browser_attempt,
                    artifact_dir=Path(artifact_dir_value),
                    profile_dir=Path(report.get('temp_root') or temp_root) / 'profile',
                    env=env if isinstance(env, dict) else None,
                    stage='interrupted-finalized',
                )
            active_browser_attempt = None
            active_browser_process = None
        if browser is not None:
            stop_process(browser, name='chromium', report=report)
        if playwright_cleanup is not None:
            try:
                playwright_cleanup()
            except Exception as exc:  # noqa: BLE001
                report['playwright_cleanup_error'] = str(exc)
        if fixture_proc is not None:
            stop_process(fixture_proc, name='fixture_lab', report=report)
        report['finished_at'] = utc_now()
        checkpoint_report(report, output_path, phase='finished', note='smoke run finalized')
        restore_signal_handlers()
        atexit_state['enabled'] = False
        print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
