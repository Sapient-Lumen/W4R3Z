from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CAPTURE_SPEC = importlib.util.spec_from_file_location('e2e_fixturelab_capture_module', ROOT / 'scripts' / 'e2e_fixturelab_capture.py')
assert CAPTURE_SPEC and CAPTURE_SPEC.loader
CAPTURE_MODULE = importlib.util.module_from_spec(CAPTURE_SPEC)
CAPTURE_SPEC.loader.exec_module(CAPTURE_MODULE)

DOCTOR_SPEC = importlib.util.spec_from_file_location('doctor_module_for_fixture_capture', ROOT / 'scripts' / 'doctor.py')
assert DOCTOR_SPEC and DOCTOR_SPEC.loader
DOCTOR_MODULE = importlib.util.module_from_spec(DOCTOR_SPEC)
DOCTOR_SPEC.loader.exec_module(DOCTOR_MODULE)

build_capture_bundle = CAPTURE_MODULE.build_capture_bundle
summarize_fixturelab_report = CAPTURE_MODULE.summarize_fixturelab_report
summarize_capture_history = CAPTURE_MODULE.summarize_capture_history
analyze_hints = DOCTOR_MODULE.analyze_hints


def _write_report(path: Path, *, ok: bool, phase: str, timestamp: str, browser_mode_selected: str = 'playwright-persistent', trace_saved: bool = True) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    report = {
        'ok': ok,
        'timestamp': timestamp,
        'finished_at': timestamp,
        'phase': phase,
        'output_path': str(path),
        'browser_mode_requested': 'auto',
        'browser_mode_selected': browser_mode_selected,
        'socket_exists_after_launch': True,
        'native_bootstrap': {'oneshot_ok': True},
        'extension_contexts': {'runtime_id_matches_extension': True, 'background_context_seen': True, 'offscreen_context_seen': False},
        'probe_json': {'ok': ok, 'receivers': [{'id': 'recv-1'}]},
        'cli_proof': {'ok': ok, 'skipped': False},
        'doctor': {'hints': ['h1', 'h2']},
        'setup': {
            'replay_script_path': str(path.with_suffix('.setup-replay.sh')),
            'ledger_path': str(path.with_suffix('.setup-ledger.json')),
            'summary_path': str(path.with_suffix('.setup-summary.md')),
            'environment_fingerprint': {
                'default_browser': {'browser_family': 'chrome-for-testing'},
                'playwright_browser': {'browser_family': 'chromium'},
                'playwright_channel_ready': False,
                'playwright_cache_alignment_status': 'cache-install-name-drift',
                'native_host_install_targets': ['chromium', 'chrome-for-testing'],
            },
            'recommended_next_action': {
                'summary': 'Repair or inspect Playwright cache alignment before rerunning fixture-lab smoke.',
                'command': 'python scripts/playwright-browsers.py ensure-channel-ready',
            },
            'actions': [
                {'name': 'playwright_channel_ready', 'executed': False},
                {'name': 'native_host_install_chromium', 'executed': True, 'ok': True},
            ],
        },
        'playwright': {
            'available': True,
            'persistent': {
                'launch_strategy': 'bundled-executable',
                'launch_plan': {'strategy': 'bundled-executable', 'risky_fallback': False},
                'service_worker_urls': ['chrome-extension://abc123/sw.js'],
                'trace': {
                    'requested_path': str(path.with_suffix('.playwright-trace.zip')),
                    'saved': trace_saved,
                    'exists': trace_saved,
                },
            },
        },
        'cdp': {'extension_visible': True, 'service_worker_seen': True, 'browser_service_worker_seen': True},
    }
    path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    path.with_suffix('.playwright-probe.png').write_bytes(b'png')
    path.with_suffix('.playwright-trace.zip').write_bytes(b'zip')
    path.with_suffix('.setup-replay.sh').write_text('#!/usr/bin/env bash\n', encoding='utf-8')
    path.with_suffix('.setup-ledger.json').write_text(json.dumps({'counts': {'total': 2, 'executed': 1, 'failed': 0}, 'actions': [{'name': 'native_host_install_chromium', 'executed': True, 'ok': True}]}, indent=2) + '\n', encoding='utf-8')
    path.with_suffix('.setup-summary.md').write_text('# setup summary\n', encoding='utf-8')
    attempt_dir = path.with_name(f'{path.stem}.browser-attempts') / '01-headless-new'
    (attempt_dir / 'profile-artifacts').mkdir(parents=True, exist_ok=True)
    (attempt_dir / 'profile-artifacts' / 'DevToolsActivePort').write_text('9222\n/devtools/browser/test\n', encoding='utf-8')
    (attempt_dir / 'attempt.json').write_text(json.dumps({
        'stage': 'finalized',
        'devtools_active_port': {'exists': True, 'port': '9222'},
        'attempt': {'mode': browser_mode_selected, 'interrupted': not ok},
        'diagnosis': {
            'category': 'profile-lock-or-stale-profile' if not ok else 'extension-visible',
            'summary': 'Profile-lock artifacts were present during browser startup.' if not ok else 'CDP saw extension targets during browser launch.',
            'confidence': 'high',
            'signature_tags': ['profile-lock'] if not ok else [],
            'hints': ['Use a fresh non-default user-data-dir before retrying.'] if not ok else [],
            'signals': {'profile_lock_artifact_count': 1 if not ok else 0},
        },
    }, indent=2) + '\n', encoding='utf-8')
    return path


def test_e2e_fixturelab_capture_writes_bundle_and_history_diff(tmp_path: Path) -> None:
    report_path = _write_report(tmp_path / 'validation' / 'latest' / 'e2e-fixturelab.json', ok=False, phase='failed', timestamp='2026-03-17T23:40:00Z')
    output_dir = tmp_path / 'capture-one'
    history_file = tmp_path / 'e2e-fixturelab-captures.json'

    first = build_capture_bundle(report_path=report_path, output_dir=output_dir, history_file=history_file)
    assert (output_dir / 'bundle-summary.json').exists()
    assert (output_dir / 'e2e-fixturelab-report.json').exists()
    assert (output_dir / 'smoke-summary.json').exists()
    assert (output_dir / 'smoke-history.json').exists()
    assert (output_dir / 'smoke-diff.json').exists()
    assert (output_dir / 'doctor.json').exists()
    assert (output_dir / 'probe-json.json').exists()
    assert (output_dir / 'cli-proof.json').exists()
    assert first['capture_history']['capture_count_after_write'] == 1
    assert first['comparison_to_previous_capture']['has_previous_capture'] is False
    copied = {item['kind'] for item in first['copied_artifacts'] if item.get('copied')}
    assert 'sibling:playwright-probe.png' in copied
    assert 'sibling:playwright-trace.zip' in copied
    assert 'sibling:setup-replay.sh' in copied
    assert 'sibling:setup-ledger.json' in copied
    assert 'sibling:setup-summary.md' in copied
    assert 'sibling-dir:browser-attempts' in copied
    assert (output_dir / 'artifacts' / 'e2e-fixturelab.browser-attempts' / '01-headless-new' / 'attempt.json').exists()

    _write_report(report_path, ok=True, phase='finished', timestamp='2026-03-17T23:41:00Z', browser_mode_selected='playwright-cdp', trace_saved=False)
    second_dir = tmp_path / 'capture-two'
    second = build_capture_bundle(report_path=report_path, output_dir=second_dir, history_file=history_file)
    diff = json.loads((second_dir / 'smoke-diff.json').read_text(encoding='utf-8'))
    summary_md = (second_dir / 'SUMMARY.md').read_text(encoding='utf-8')
    history = summarize_capture_history(history_file)

    assert second['capture_history']['capture_count_after_write'] == 2
    assert second['smoke_summary']['browser_attempt_artifact_root_exists'] is True
    assert second['smoke_summary']['browser_attempt_artifact_dir_count'] == 1
    assert second['smoke_summary']['setup_action_count'] == 2
    assert second['smoke_summary']['executed_setup_action_count'] == 1
    assert second['smoke_summary']['setup_replay_script_exists'] is True
    assert second['smoke_summary']['setup_ledger_exists'] is True
    assert second['smoke_summary']['setup_summary_exists'] is True
    assert second['smoke_summary']['failed_setup_action_count'] == 0
    assert second['smoke_summary']['setup_recommended_next_command'] == 'python scripts/playwright-browsers.py ensure-channel-ready'
    assert second['smoke_summary']['setup_environment_browser_family'] == 'chrome-for-testing'
    assert second['smoke_summary']['setup_environment_playwright_browser_family'] == 'chromium'
    assert second['smoke_summary']['setup_environment_cache_alignment_status'] == 'cache-install-name-drift'
    assert second['smoke_summary']['latest_browser_attempt_diagnosis']['category'] == 'extension-visible'
    assert second['smoke_summary']['profile_lock_browser_attempt_count'] == 0
    assert diff['has_previous_capture'] is True
    assert diff['ok_changed'] is True
    assert diff['phase_changed'] is True
    assert diff['browser_mode_selected_changed'] is True
    assert history['capture_count'] == 2
    assert history['latest_capture']['report_timestamp'] == '2026-03-17T23:41:00Z'
    assert 'python scripts/e2e-fixturelab-capture.py history --pretty' in summary_md


def test_doctor_hints_fixturelab_report_needs_capture() -> None:
    fixture_lab = {
        'latest_smoke_report': {'exists': True, 'summary': summarize_fixturelab_report({'ok': False, 'timestamp': '2026-03-17T23:42:00Z', 'phase': 'failed', 'socket_exists_after_launch': False, 'native_bootstrap': {'oneshot_ok': False}, 'extension_contexts': {}, 'probe_json': {'ok': False}, 'cli_proof': {'ok': False, 'skipped': True}, 'playwright': {'available': True}, 'cdp': {}}, report_path=Path('validation/latest/e2e-fixturelab.json'))},
        'smoke_capture_history': {'capture_count': 0, 'latest_capture': None},
        'commands': {'capture_latest': 'python scripts/e2e-fixturelab-capture.py --report validation/latest/e2e-fixturelab.json --output-dir validation/latest/e2e-fixturelab-capture', 'capture_history': 'python scripts/e2e-fixturelab-capture.py history --pretty'},
    }
    hints = analyze_hints({'has_key': True}, {'extension_id': 'abc123', 'targets': {}, 'recommended_targets': ['chromium'], 'runtime': {}, 'last_oversized_host_message': {}}, {'exists': False}, {'profiles': [], 'triage': {}, 'fleet_capture_history': {}}, [], {'available': True, 'extension_launch_plan': {}, 'cache_audit': {}, 'repair_plan': {}}, {}, fixture_lab, {}, {})
    assert any('freeze it with `python scripts/e2e-fixturelab-capture.py --report validation/latest/e2e-fixturelab.json --output-dir validation/latest/e2e-fixturelab-capture`' in hint for hint in hints)


def test_doctor_hints_fixturelab_capture_history_exists() -> None:
    fixture_lab = {
        'latest_smoke_report': {'exists': True, 'summary': {'report_path': 'validation/latest/e2e-fixturelab.json', 'report_timestamp': '2026-03-17T23:42:00Z'}},
        'smoke_capture_history': {'capture_count': 2, 'latest_capture': {'report_timestamp': '2026-03-17T23:42:00Z'}},
        'commands': {'capture_latest': 'python scripts/e2e-fixturelab-capture.py --report validation/latest/e2e-fixturelab.json --output-dir validation/latest/e2e-fixturelab-capture', 'capture_history': 'python scripts/e2e-fixturelab-capture.py history --pretty'},
    }
    hints = analyze_hints({'has_key': True}, {'extension_id': 'abc123', 'targets': {}, 'recommended_targets': ['chromium'], 'runtime': {}, 'last_oversized_host_message': {}}, {'exists': False}, {'profiles': [], 'triage': {}, 'fleet_capture_history': {}}, [], {'available': True, 'extension_launch_plan': {}, 'cache_audit': {}, 'repair_plan': {}}, {}, fixture_lab, {}, {})
    assert any('Fixture-lab smoke capture history already has 2 saved bundle(s)' in hint and 'python scripts/e2e-fixturelab-capture.py history --pretty' in hint for hint in hints)


def test_summarize_fixturelab_report_tracks_interrupted_browser_attempts() -> None:
    summary = summarize_fixturelab_report({
        'ok': False,
        'timestamp': '2026-03-18T19:35:24Z',
        'finished_at': '2026-03-18T19:35:53Z',
        'phase': 'finished',
        'terminated': True,
        'terminated_signal': 15,
        'browser_attempts': [
            {
                'mode': 'headless-new',
                'remote_debugging_port': 45491,
                'interrupted': True,
                'interruption_reason': 'terminated by signal 15 during browser launch',
            }
        ],
        'playwright': {'available': True},
        'native_bootstrap': {'oneshot_ok': False},
        'extension_contexts': {},
        'probe_json': {'ok': False},
        'cli_proof': {'ok': False, 'skipped': True},
        'cdp': {},
    }, report_path=Path('validation/latest/e2e-fixturelab.json'))

    assert summary['terminated'] is True
    assert summary['terminated_signal'] == 15
    assert summary['browser_attempt_count'] == 1
    assert summary['interrupted_browser_attempt_count'] == 1
    assert summary['last_browser_attempt_mode'] == 'headless-new'
    assert summary['last_browser_attempt_interrupted'] is True
    assert summary['latest_browser_attempt_diagnosis'] is None


def test_doctor_hints_fixturelab_latest_diagnosis() -> None:
    fixture_lab = {
        'latest_smoke_report': {'exists': True, 'summary': {'report_path': 'validation/latest/e2e-fixturelab.json', 'report_timestamp': '2026-03-18T00:00:00Z', 'latest_browser_attempt_diagnosis': {'category': 'browser-exited-before-cdp', 'summary': 'Browser exited before CDP became available.', 'hints': ['Check the saved browser stderr/stdout logs first.']}}},
        'smoke_capture_history': {'capture_count': 0, 'latest_capture': None},
        'commands': {'capture_latest': 'python scripts/e2e-fixturelab-capture.py --report validation/latest/e2e-fixturelab.json --output-dir validation/latest/e2e-fixturelab-capture', 'capture_history': 'python scripts/e2e-fixturelab-capture.py history --pretty'},
    }
    hints = analyze_hints({'has_key': True}, {'extension_id': 'abc123', 'targets': {}, 'recommended_targets': ['chromium'], 'runtime': {}, 'last_oversized_host_message': {}}, {'exists': False}, {'profiles': [], 'triage': {}, 'fleet_capture_history': {}}, [], {'available': True, 'extension_launch_plan': {}, 'cache_audit': {}, 'repair_plan': {}}, {}, fixture_lab, {}, {})
    assert any('Latest fixture-lab browser attempt diagnosis: Browser exited before CDP became available.' in hint for hint in hints)


def test_doctor_hints_fixturelab_setup_failures() -> None:
    fixture_lab = {
        'latest_smoke_report': {'exists': True, 'summary': {'report_path': 'validation/latest/e2e-fixturelab.json', 'report_timestamp': '2026-03-18T00:00:00Z', 'failed_setup_action_count': 1, 'failed_setup_action_names': ['playwright_channel_ready'], 'setup_summary_path': 'validation/latest/e2e-fixturelab.setup-summary.md', 'setup_ledger_path': 'validation/latest/e2e-fixturelab.setup-ledger.json', 'setup_recommended_next_summary': 'Repair or inspect Playwright cache alignment before rerunning fixture-lab smoke.', 'setup_recommended_next_command': 'python scripts/playwright-browsers.py ensure-channel-ready'}},
        'smoke_capture_history': {'capture_count': 0, 'latest_capture': None},
        'commands': {'capture_latest': 'python scripts/e2e-fixturelab-capture.py --report validation/latest/e2e-fixturelab.json --output-dir validation/latest/e2e-fixturelab-capture', 'capture_history': 'python scripts/e2e-fixturelab-capture.py history --pretty'},
    }
    hints = analyze_hints({'has_key': True}, {'extension_id': 'abc123', 'targets': {}, 'recommended_targets': ['chromium'], 'runtime': {}, 'last_oversized_host_message': {}}, {'exists': False}, {'profiles': [], 'triage': {}, 'fleet_capture_history': {}}, [], {'available': True, 'extension_launch_plan': {}, 'cache_audit': {}, 'repair_plan': {}}, {}, fixture_lab, {}, {})
    assert any('Latest fixture-lab smoke run had 1 failed setup action(s): playwright_channel_ready.' in hint and 'setup-summary.md' in hint and 'setup-ledger.json' in hint and 'python scripts/playwright-browsers.py ensure-channel-ready' in hint for hint in hints)
