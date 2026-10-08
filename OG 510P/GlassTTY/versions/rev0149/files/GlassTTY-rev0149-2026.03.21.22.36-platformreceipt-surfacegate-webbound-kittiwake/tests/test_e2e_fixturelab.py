from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / 'scripts' / 'e2e_fixturelab.py'
SPEC = importlib.util.spec_from_file_location('glasstty_e2e_fixturelab_testshim', MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)
browser_env = MODULE.browser_env
browser_launch_command = MODULE.browser_launch_command
discover_playwright_browser_install = MODULE.discover_playwright_browser_install
discover_browser_executable = MODULE.discover_browser_executable
existing_playwright_browsers_path = MODULE.existing_playwright_browsers_path
launch_playwright_persistent_probe = MODULE.launch_playwright_persistent_probe
attach_playwright_extension_context = MODULE.attach_playwright_extension_context
playwright_extension_launch_plan = MODULE.playwright_extension_launch_plan
extension_dist_ready = MODULE.extension_dist_ready
probe_url = MODULE.probe_url
open_probe_page = MODULE.open_probe_page
stop_extension_service_worker_playwright = MODULE.stop_extension_service_worker_playwright
worker_resume_summary = MODULE.worker_resume_summary
run_cli_step = MODULE.run_cli_step
native_bootstrap_summary = MODULE.native_bootstrap_summary
extension_context_summary = MODULE.extension_context_summary
native_host_install_targets = MODULE.native_host_install_targets
wait_for_probe_result_playwright = MODULE.wait_for_probe_result_playwright
wait_for_healthy_extension_service_worker = MODULE.wait_for_healthy_extension_service_worker
write_json_atomic = MODULE.write_json_atomic
checkpoint_report = MODULE.checkpoint_report
append_step = MODULE.append_step
planned_playwright_channel_prepare = MODULE.planned_playwright_channel_prepare
build_setup_replay_script = MODULE.build_setup_replay_script
write_setup_replay_script = MODULE.write_setup_replay_script
build_setup_ledger = MODULE.build_setup_ledger
write_setup_ledger = MODULE.write_setup_ledger
write_setup_summary = MODULE.write_setup_summary
mark_browser_attempt_inflight = MODULE.mark_browser_attempt_inflight
clear_browser_attempt_inflight = MODULE.clear_browser_attempt_inflight
finalize_browser_attempt = MODULE.finalize_browser_attempt
browser_attempt_artifact_root = MODULE.browser_attempt_artifact_root
browser_attempt_artifact_dir = MODULE.browser_attempt_artifact_dir
snapshot_browser_attempt_artifacts = MODULE.snapshot_browser_attempt_artifacts
diagnose_browser_attempt_snapshot = MODULE.diagnose_browser_attempt_snapshot
install_termination_checkpoint = MODULE.install_termination_checkpoint


def test_write_json_atomic_replaces_existing_payload(tmp_path: Path) -> None:
    output = tmp_path / 'report.json'
    output.write_text('{"stale": true}\n', encoding='utf-8')

    write_json_atomic(output, {'ok': True, 'phase': 'finished'})

    assert json.loads(output.read_text(encoding='utf-8')) == {'ok': True, 'phase': 'finished'}
    assert not (tmp_path / '.report.json.tmp').exists()


def test_checkpoint_report_records_sequence_and_events(tmp_path: Path) -> None:
    output = tmp_path / 'report.json'
    report = {'ok': False, 'steps': []}

    checkpoint_report(report, output, phase='starting', note='boot')
    append_step(report, 'doctor')
    checkpoint_report(report, output, phase='doctor_complete', event={'kind': 'doctor'})

    saved = json.loads(output.read_text(encoding='utf-8'))
    assert saved['phase'] == 'doctor_complete'
    assert saved['checkpoint']['sequence'] == 2
    assert saved['events'][0]['note'] == 'boot'
    assert saved['events'][1]['kind'] == 'doctor'
    assert saved['steps'] == ['doctor']


def test_checkpoint_report_persists_setup_artifact_paths(tmp_path: Path) -> None:
    output = tmp_path / 'e2e-fixturelab.json'
    report = {
        'timestamp': '2026-03-19T00:25:00Z',
        'setup': {
            'actions': [
                {
                    'name': 'playwright_channel_ready',
                    'command': 'python scripts/playwright-browsers.py ensure-channel-ready',
                    'executed': False,
                    'reason': 'preflight suggestion',
                },
            ],
        },
    }

    checkpoint_report(report, output, phase='starting', note='boot')
    saved = json.loads(output.read_text(encoding='utf-8'))

    assert saved['setup']['replay_script_path'].endswith('.setup-replay.sh')
    assert saved['setup']['ledger_path'].endswith('.setup-ledger.json')
    assert saved['setup']['summary_path'].endswith('.setup-summary.md')
    assert output.with_suffix('.setup-replay.sh').exists()
    assert output.with_suffix('.setup-ledger.json').exists()
    assert output.with_suffix('.setup-summary.md').exists()


def test_planned_playwright_channel_prepare_runs_when_cache_drifted() -> None:
    action = planned_playwright_channel_prepare({
        'available': True,
        'launch_plan': {
            'channel_ready': False,
            'cache_alignment_status': 'cache-install-name-drift',
            'cache_alignment_reason': 'cached browser does not match expected package',
            'recommended_channel_ready_command': 'python scripts/playwright-browsers.py ensure-channel-ready',
        },
    }, policy='if-needed')

    assert action['will_run'] is True
    assert action['skipped'] is False
    assert action['command'] == 'python scripts/playwright-browsers.py ensure-channel-ready'
    assert action['cache_alignment_status_before'] == 'cache-install-name-drift'



def test_planned_playwright_channel_prepare_skips_when_already_ready() -> None:
    action = planned_playwright_channel_prepare({
        'available': True,
        'launch_plan': {
            'channel_ready': True,
            'cache_alignment_status': 'aligned',
            'recommended_channel_ready_command': 'python scripts/playwright-browsers.py ensure-channel-ready',
        },
    }, policy='if-needed')

    assert action['will_run'] is False
    assert action['skipped'] is True
    assert action['reason'] == 'Playwright cache is already channel-ready'



def test_write_setup_replay_script_includes_commands_and_comments(tmp_path: Path) -> None:
    report = {
        'setup': {
            'actions': [
                {
                    'name': 'playwright_channel_ready',
                    'command': 'python scripts/playwright-browsers.py ensure-channel-ready',
                    'executed': False,
                    'will_run': False,
                    'reason': 'Playwright cache is already channel-ready',
                },
                {
                    'name': 'native_host_install_chromium',
                    'command': './scripts/install-native-host.sh --target chromium --extension-id auto --host-exe ./scripts/native-host-wrapper.sh',
                    'executed': True,
                    'ok': True,
                    'reason': 'Smoke installs native-host manifests before launch.',
                },
            ],
        },
    }

    script_path = write_setup_replay_script(tmp_path / 'e2e-fixturelab.json', report)
    body = script_path.read_text(encoding='utf-8')

    assert 'python scripts/playwright-browsers.py ensure-channel-ready' in body
    assert '# python scripts/playwright-browsers.py ensure-channel-ready' in body
    assert './scripts/install-native-host.sh --target chromium --extension-id auto --host-exe ./scripts/native-host-wrapper.sh' in body
    assert report['setup']['replay_script_path'] == str(script_path)
    assert script_path.stat().st_mode & 0o111


def test_write_setup_ledger_and_summary_capture_output_tails(tmp_path: Path) -> None:
    output_path = tmp_path / 'e2e-fixturelab.json'
    report = {
        'timestamp': '2026-03-19T00:03:00Z',
        'phase': 'native_host_ready',
        'browser_mode_requested': 'auto',
        'browser_env': {
            'PLAYWRIGHT_BROWSERS_PATH': str(tmp_path / 'pw-cache'),
            'GLASSTTY_HOME': str(tmp_path / 'glass-home'),
            'CHROME_CONFIG_HOME': str(tmp_path / 'chrome-config'),
        },
        'browser_choice': {
            'browser_family': 'chrome-for-testing',
            'version': '146.0.0.0',
            'source': 'chrome-for-testing',
            'path': '/tmp/cft/chrome',
            'native_messaging_targets': ['chrome-for-testing'],
        },
        'playwright': {
            'available': True,
            'browser_choice': {
                'browser_family': 'chromium',
                'source': 'playwright-cache',
                'path': '/tmp/pw/chromium',
                'native_messaging_targets': ['chromium'],
            },
            'launch_plan': {
                'strategy': 'bundled-executable',
                'channel_ready': False,
                'cache_alignment_status': 'cache-install-name-drift',
                'cache_alignment_reason': 'cached browser does not match expected package',
                'recommended_channel_ready_command': 'python scripts/playwright-browsers.py ensure-channel-ready',
            },
        },
        'setup': {
            'playwright_channel_policy': 'if-needed',
            'actions': [
                {
                    'name': 'playwright_channel_ready',
                    'kind': 'playwright-channel-ready',
                    'command': 'python scripts/playwright-browsers.py ensure-channel-ready',
                    'executed': True,
                    'ok': False,
                    'returncode': 2,
                    'reason': 'cache drift forced a repair attempt',
                    'stdout': 'before\nafter\n',
                    'stderr': '\n'.join(f'line-{index}' for index in range(30)),
                    'channel_ready_before': False,
                    'cache_alignment_status_before': 'cache-install-name-drift',
                    'cache_alignment_reason_before': 'cached browser does not match expected package',
                },
            ],
        },
    }

    replay_path = write_setup_replay_script(output_path, report)
    ledger_path = write_setup_ledger(output_path, report)
    summary_path = write_setup_summary(output_path, report)
    ledger = json.loads(ledger_path.read_text(encoding='utf-8'))
    summary_md = summary_path.read_text(encoding='utf-8')

    assert replay_path.exists()
    assert ledger['counts']['failed'] == 1
    assert ledger['failed_action_names'] == ['playwright_channel_ready']
    assert ledger['recommended_replay_command'].endswith('.setup-replay.sh')
    assert ledger['recommended_next_action']['command'] == 'python scripts/playwright-browsers.py ensure-channel-ready'
    assert ledger['environment_fingerprint']['playwright_cache_alignment_status'] == 'cache-install-name-drift'
    assert ledger['environment_fingerprint']['native_host_install_targets'] == ['chromium', 'chrome-for-testing']
    assert ledger['actions'][0]['environment_fingerprint']['playwright_cache_alignment_status_before'] == 'cache-install-name-drift'
    assert 'stdout_tail' in ledger['actions'][0]
    assert 'stderr_tail' in ledger['actions'][0]
    assert '[… trimmed …]' in ledger['actions'][0]['stderr_tail']
    assert report['setup']['ledger_path'] == str(ledger_path)
    assert report['setup']['summary_path'] == str(summary_path)
    assert report['setup']['recommended_next_action']['command'] == 'python scripts/playwright-browsers.py ensure-channel-ready'
    assert 'failed_setup_action_count: 1' in summary_md
    assert '## Environment fingerprint' in summary_md
    assert '## Recommended next action' in summary_md
    assert 'playwright_channel_ready' in summary_md


def test_finalize_browser_attempt_records_interrupted_launch() -> None:
    report = {'browser_attempts': []}
    attempt = {'mode': 'headless-new', 'remote_debugging_port': 9222}

    mark_browser_attempt_inflight(report, attempt)
    assert report['browser_attempt_inflight']['mode'] == 'headless-new'

    finalized = finalize_browser_attempt(
        report,
        attempt,
        interrupted=True,
        interruption_reason='terminated by signal 15 during browser launch',
    )

    assert finalized is attempt
    assert report['browser_attempts'] == [attempt]
    assert attempt['interrupted'] is True
    assert attempt['interruption_reason'] == 'terminated by signal 15 during browser launch'
    assert 'browser_attempt_inflight' not in report

    clear_browser_attempt_inflight(report)
    assert 'browser_attempt_inflight' not in report


def test_browser_attempt_artifacts_snapshot_copies_profile_state(tmp_path: Path) -> None:
    report_path = tmp_path / 'validation' / 'latest' / 'e2e-fixturelab.json'
    artifact_root = browser_attempt_artifact_root(report_path)
    artifact_dir = browser_attempt_artifact_dir(output_path=report_path, sequence=1, mode='headless-new')
    assert artifact_dir.parent == artifact_root

    profile_dir = tmp_path / 'profile'
    (profile_dir / 'Default').mkdir(parents=True)
    (profile_dir / 'DevToolsActivePort').write_text('9222\n/devtools/browser/test\n', encoding='utf-8')
    (profile_dir / 'Local State').write_text('{\"profile\": true}\n', encoding='utf-8')
    (profile_dir / 'Default' / 'Preferences').write_text('{\"extensions\": {}}\n', encoding='utf-8')

    chrome_config = tmp_path / 'chrome-config'
    (chrome_config / 'Crash Reports').mkdir(parents=True)
    (chrome_config / 'chrome_debug.log').write_text('startup failed\n', encoding='utf-8')
    attempt = {'mode': 'headless-new', 'artifact_dir': str(artifact_dir), 'browser_pid': 1234}

    snapshot = snapshot_browser_attempt_artifacts(
        attempt=attempt,
        artifact_dir=artifact_dir,
        profile_dir=profile_dir,
        env={'CHROME_CONFIG_HOME': str(chrome_config)},
        stage='cdp-probed',
    )

    assert snapshot['stage'] == 'cdp-probed'
    assert snapshot['devtools_active_port']['exists'] is True
    assert (artifact_dir / 'attempt.json').exists()
    assert (artifact_dir / 'profile-artifacts' / 'DevToolsActivePort').exists()
    assert (artifact_dir / 'profile-artifacts' / 'Local State').exists()
    assert (artifact_dir / 'profile-artifacts' / 'Default' / 'Preferences').exists()
    assert (artifact_dir / 'browser-config' / 'chrome_debug.log').exists()
    assert snapshot['diagnosis']['category'] == 'devtools-file-present-cdp-unreachable'


def test_diagnose_browser_attempt_snapshot_flags_profile_lock(tmp_path: Path) -> None:
    artifact_dir = tmp_path / 'attempt-artifacts'
    (artifact_dir / 'browser-config').mkdir(parents=True)
    (artifact_dir / 'browser-config' / 'chrome_debug.log').write_text('ProcessSingleton: profile appears to be in use\n', encoding='utf-8')
    diagnosis = diagnose_browser_attempt_snapshot({
        'artifact_dir': str(artifact_dir),
        'attempt': {'mode': 'headed', 'returncode_early': 21},
        'devtools_active_port': {'exists': False},
        'copied_artifacts': [
            {'label': 'singleton_lock', 'exists': True},
            {'label': 'singleton_socket', 'exists': False},
            {'label': 'singleton_cookie', 'exists': False},
        ],
        'crash_reports': {'entry_count': 0},
    })

    assert diagnosis['category'] == 'profile-lock-or-stale-profile'
    assert 'profile-lock' in diagnosis['signature_tags']
    assert diagnosis['signals']['profile_lock_artifact_count'] == 1
    assert any('fresh non-default user-data-dir' in hint for hint in diagnosis['hints'])


def test_install_termination_checkpoint_writes_report_on_signal(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    output = tmp_path / 'report.json'
    report = {'ok': False}
    handlers: dict[int, object] = {}
    restored: dict[int, object] = {}

    def fake_getsignal(signum: int):
        return f'previous-{signum}'

    def fake_signal(signum: int, handler):
        restored[signum] = handler
        handlers[signum] = handler

    monkeypatch.setattr(install_termination_checkpoint.__globals__['signal'], 'getsignal', fake_getsignal)
    monkeypatch.setattr(install_termination_checkpoint.__globals__['signal'], 'signal', fake_signal)

    restore, previous = install_termination_checkpoint(report, output)
    assert previous
    signum = next(iter(previous.keys()))

    with pytest.raises(SystemExit) as excinfo:
        handlers[signum](signum, None)
    assert excinfo.value.code == 128 + signum

    saved = json.loads(output.read_text(encoding='utf-8'))
    assert saved['terminated'] is True
    assert saved['terminated_signal'] == signum
    assert saved['phase'] == 'terminated'

    restore()
    assert restored[signum] == f'previous-{signum}'


def test_browser_launch_command_adds_root_no_sandbox(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(browser_launch_command.__globals__['os'], 'geteuid', lambda: 0)
    cmd = browser_launch_command(
        chromium='/usr/bin/chromium',
        extension_dir=tmp_path / 'extension',
        profile_dir=tmp_path / 'profile',
        start_url='http://127.0.0.1:8765/',
        remote_debugging_port=9222,
        headed=False,
    )
    joined = ' '.join(cmd)
    assert '--no-sandbox' in joined
    assert '--remote-debugging-port=9222' in joined
    assert '--load-extension=' in joined
    assert '--remote-allow-origins=*' in joined
    assert '--disable-gpu' in joined
    assert '--disable-dev-shm-usage' in joined
    assert '--noerrdialogs' in joined
    assert '--headless=new' in joined


def test_probe_url_points_at_probe_page() -> None:
    url = probe_url('abc123', 'http://127.0.0.1:8765/')
    assert url.startswith('chrome-extension://abc123/probe/index.html?')
    assert 'fixture=http%3A%2F%2F127.0.0.1%3A8765%2F' in url


def test_wait_for_healthy_extension_service_worker_recovers_from_stale_worker(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeWorker:
        def __init__(self, url: str, *, runtime: dict[str, object] | None = None, error: str | None = None) -> None:
            self.url = url
            self.runtime = runtime or {'origin': 'chrome-extension://abc123'}
            self.error = error

        def evaluate(self, _expr: str) -> dict[str, object]:
            if self.error:
                raise RuntimeError(self.error)
            return self.runtime

    class FakeContext:
        def __init__(self) -> None:
            self.calls = 0
            self.stale = FakeWorker('chrome-extension://abc123/dist/background/main.js', error='Execution context was destroyed')
            self.fresh = FakeWorker('chrome-extension://abc123/dist/background/main.js', runtime={'origin': 'chrome-extension://abc123', 'scope': 'chrome-extension://abc123/'})

        @property
        def service_workers(self):
            self.calls += 1
            if self.calls == 1:
                return [self.stale]
            return [self.stale, self.fresh]

    monkeypatch.setattr(wait_for_healthy_extension_service_worker.__globals__['time'], 'sleep', lambda _seconds: None)

    report: dict[str, object] = {}
    worker, snapshot, wait_report = wait_for_healthy_extension_service_worker(
        FakeContext(),
        expected_extension_id='abc123',
        timeout=0.5,
        report=report,
        poll_interval=0.01,
    )

    assert worker.url.endswith('background/main.js')
    assert snapshot['runtime']['origin'] == 'chrome-extension://abc123'
    assert wait_report['healthy'] is True
    assert wait_report['attempts'] >= 2
    assert wait_report['stale_snapshots'][0]['evaluate_error'] == 'Execution context was destroyed'
    assert report['service_worker_wait']['selected_worker_url'].endswith('background/main.js')


def test_browser_env_sets_writable_xdg_dirs(tmp_path: Path) -> None:
    env = browser_env(tmp_path / 'home')
    assert env['HOME'] == str(tmp_path / 'home')
    assert env['XDG_CONFIG_HOME'].startswith(str(tmp_path / 'home'))
    assert env['XDG_CACHE_HOME'].startswith(str(tmp_path / 'home'))
    assert env['XDG_RUNTIME_DIR'].startswith(str(tmp_path / 'home'))
    assert env['CHROME_CONFIG_HOME'].startswith(env['XDG_CONFIG_HOME'])
    assert (Path(env['CHROME_CONFIG_HOME']) / 'Crash Reports').is_dir()


def test_browser_env_reuses_shared_playwright_cache(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    shared = tmp_path / 'pw-browsers'
    shared.mkdir()
    monkeypatch.setitem(browser_env.__globals__['os'].environ, 'PLAYWRIGHT_BROWSERS_PATH', '')
    monkeypatch.setitem(existing_playwright_browsers_path.__globals__['os'].environ, 'PLAYWRIGHT_BROWSERS_PATH', '')
    monkeypatch.setitem(browser_env.__globals__, 'existing_playwright_browsers_path', lambda **kwargs: shared)
    env = browser_env(tmp_path / 'home')
    assert env['PLAYWRIGHT_BROWSERS_PATH'] == str(shared)


def test_discover_playwright_browser_install_prefers_bundled_cache(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    bundle = tmp_path / 'chromium-1208' / 'chrome-linux64'
    bundle.mkdir(parents=True)
    browser = bundle / 'chrome'
    browser.write_text('', encoding='utf-8')
    monkeypatch.setitem(discover_playwright_browser_install.__globals__['os'].environ, 'PLAYWRIGHT_BROWSERS_PATH', str(tmp_path))
    install = discover_playwright_browser_install(playwright_available=True, import_error=None)
    assert install['bundled_executable_exists'] is True
    assert install['bundled_executable'] == str(browser)
    assert install['launch_strategy'] == 'bundled-executable'


def test_playwright_extension_launch_plan_prefers_channel_when_cache_matches_expected_package() -> None:
    plan = playwright_extension_launch_plan(
        env={},
        browser_install={
            'available': True,
            'import_error': None,
            'bundled_executable_exists': True,
            'bundled_executable': '/cache/chromium-1208/chrome-linux64/chrome',
            'bundled_install': {
                'source': 'chrome-for-testing-import',
                'package_name': 'chromium',
                'install_name': 'chromium-1208',
            },
            'expected_browser_package': {'package_name': 'chromium', 'install_name': 'chromium-1208'},
            'system_chromium': '/usr/bin/chromium',
        },
    )
    assert plan['strategy'] == 'playwright-channel'
    assert plan['channel'] == 'chromium'
    assert plan['supported'] is True
    assert plan['risky_fallback'] is False


def test_playwright_extension_launch_plan_falls_back_to_bundled_executable_when_cache_name_drifts() -> None:
    plan = playwright_extension_launch_plan(
        env={},
        browser_install={
            'available': True,
            'import_error': None,
            'bundled_executable_exists': True,
            'bundled_executable': '/cache/chromium-cft-145/chrome-linux64/chrome',
            'bundled_install': {
                'source': 'chrome-for-testing-import',
                'package_name': 'chromium',
                'install_name': 'chromium-cft-145.0.7632.6',
            },
            'expected_browser_package': {'package_name': 'chromium', 'install_name': 'chromium-1208'},
            'system_chromium': '/usr/bin/chromium',
        },
    )
    assert plan['strategy'] == 'bundled-executable'
    assert plan['supported'] is True
    assert plan['risky_fallback'] is False
    assert plan['channel_ready'] is False
    assert plan['cache_alignment_status'] == 'cache-install-name-drift'
    assert plan['recommended_channel_ready_command'] == 'python scripts/playwright-browsers.py ensure-channel-ready'



def test_playwright_extension_launch_plan_prefers_repair_then_sync_command_when_cache_repair_exists() -> None:
    plan = playwright_extension_launch_plan(
        env={},
        browser_install={
            'available': True,
            'import_error': None,
            'bundled_executable_exists': True,
            'bundled_executable': '/cache/chromium-cft-145/chrome-linux64/chrome',
            'bundled_install': {
                'source': 'archive-import',
                'package_name': 'chromium',
                'install_name': 'chromium-cft-145.0.7632.6',
            },
            'expected_browser_package': {'package_name': 'chromium', 'install_name': 'chromium-1208'},
        },
        repair_plan={
            'counts': {'repairable_shadow_installs': 1},
            'recommended_apply_command': 'python scripts/playwright-browsers.py repair --apply',
        },
    )
    assert plan['recommended_repair_then_sync_command'] == 'python scripts/playwright-browsers.py repair --apply && python scripts/playwright-browsers.py sync --package chromium'
    assert plan['recommended_ensure_channel_ready_command'] == 'python scripts/playwright-browsers.py ensure-channel-ready'
    assert plan['recommended_channel_ready_command'] == 'python scripts/playwright-browsers.py ensure-channel-ready'
    assert any('Channel-ready cache alignment command' in note for note in plan['notes'])


def test_playwright_extension_launch_plan_skips_system_fallback_by_default() -> None:
    plan = playwright_extension_launch_plan(
        env={},
        browser_install={
            'available': True,
            'import_error': None,
            'bundled_executable_exists': False,
            'system_chromium': '/usr/bin/chromium',
        },
    )
    assert plan['strategy'] is None
    assert plan['skip_reason'] == 'missing-bundled-chromium'
    assert plan['supported'] is False


def test_playwright_extension_launch_plan_allows_system_fallback_when_opted_in() -> None:
    plan = playwright_extension_launch_plan(
        env={'GLASSTTY_PLAYWRIGHT_ALLOW_SYSTEM_EXECUTABLE': '1'},
        browser_install={
            'available': True,
            'import_error': None,
            'bundled_executable_exists': False,
            'system_chromium': '/usr/bin/chromium',
        },
    )
    assert plan['strategy'] == 'system-executable'
    assert plan['risky_fallback'] is True
    assert plan['supported'] is False


def test_native_bootstrap_summary_detects_oneshot_success() -> None:
    summary = native_bootstrap_summary({
        'bridge': {
            'status': {
                'nativeConnection': {
                    'connected': False,
                    'lastOneShotProbeOk': True,
                    'lastOneShotProbeHost': 'com.glasstty.bridge',
                    'lastOneShotProbeSocketPath': '/tmp/daemon.sock',
                }
            }
        }
    })
    assert summary['available'] is True
    assert summary['connected'] is False
    assert summary['oneshot_ok'] is True
    assert summary['native_host'] == 'com.glasstty.bridge'
    assert summary['socket_path'] == '/tmp/daemon.sock'


def test_native_bootstrap_summary_handles_missing_native_connection() -> None:
    summary = native_bootstrap_summary({'bridge': {'status': {}}})
    assert summary['available'] is False
    assert summary['oneshot_ok'] is False


def test_extension_dist_ready_checks_probe_bundle(tmp_path: Path) -> None:
    extension_dir = tmp_path / 'extension'
    (extension_dir / 'dist' / 'background').mkdir(parents=True)
    (extension_dir / 'dist' / 'content').mkdir(parents=True)
    (extension_dir / 'dist' / 'probe').mkdir(parents=True)
    (extension_dir / 'dist' / 'offscreen').mkdir(parents=True)
    (extension_dir / 'probe').mkdir(parents=True)
    (extension_dir / 'offscreen').mkdir(parents=True)
    assert extension_dist_ready(extension_dir) is False
    for rel in (
        'manifest.json',
        'probe/index.html',
        'offscreen/index.html',
        'dist/background/main.js',
        'dist/content/main.js',
        'dist/probe/main.js',
        'dist/offscreen/main.js',
    ):
        (extension_dir / rel).write_text('// ok\n', encoding='utf-8')
    assert extension_dist_ready(extension_dir) is True


def test_launch_playwright_persistent_probe_uses_bundled_executable(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    trace_path = tmp_path / 'trace.zip'

    class FakeTracing:
        def __init__(self) -> None:
            self.started = None
            self.stopped = None

        def start(self, **kwargs) -> None:
            self.started = kwargs

        def stop(self, path: str) -> None:
            self.stopped = path
            Path(path).write_bytes(b'zip')

    class FakePage:
        url = 'chrome-extension://abc123/probe/index.html?run=1'

        def on(self, event: str, handler) -> None:
            assert event == 'console'

        def goto(self, url: str, wait_until: str, timeout: int) -> None:
            assert url.startswith('chrome-extension://abc123/probe/index.html')

        def wait_for_selector(self, selector: str, timeout: int) -> None:
            assert 'data-probe-ready' in selector

        def evaluate(self, _expr: str) -> dict[str, str]:
            return {'ready': '1', 'ok': '1', 'summary': 'ok', 'json': '{"ok": true}'}

        def title(self) -> str:
            return 'GlassTTY Probe'

    class FakeWorker:
        def __init__(self, url: str) -> None:
            self.url = url

    class FakeContext:
        def __init__(self) -> None:
            self.pages = []
            self.service_workers = [FakeWorker('chrome-extension://abc123/dist/background/main.js')]
            self.tracing = FakeTracing()

        def new_page(self) -> FakePage:
            page = FakePage()
            self.pages.append(page)
            return page

        def close(self) -> None:
            return None

    class FakeChromium:
        def __init__(self) -> None:
            self.kwargs = None

        def launch_persistent_context(self, **kwargs):
            self.kwargs = kwargs
            return FakeContext()

    class FakePlaywrightRuntime:
        def __init__(self) -> None:
            self.chromium = FakeChromium()

        def stop(self) -> None:
            return None

    class FakeSyncPlaywright:
        def __init__(self) -> None:
            self.runtime = FakePlaywrightRuntime()

        def start(self) -> FakePlaywrightRuntime:
            return self.runtime

    fake_sync = FakeSyncPlaywright()
    bundled = tmp_path / 'pw' / 'chromium-cft-145.0.7632.6' / 'chrome-linux64' / 'chrome'
    bundled.parent.mkdir(parents=True)
    bundled.write_text('', encoding='utf-8')
    monkeypatch.setitem(launch_playwright_persistent_probe.__globals__, 'sync_playwright', lambda: fake_sync)
    monkeypatch.setitem(launch_playwright_persistent_probe.__globals__, 'PLAYWRIGHT_IMPORT_ERROR', None)
    monkeypatch.setitem(launch_playwright_persistent_probe.__globals__, 'discover_playwright_browser_install', lambda **kwargs: {
        'available': True,
        'import_error': None,
        'bundled_executable_exists': True,
        'bundled_executable': str(bundled),
        'bundled_install': {'source': 'archive-import', 'package_name': 'chromium', 'install_name': 'chromium-1208'},
        'expected_browser_package': {'package_name': 'chromium', 'install_name': 'chromium-1208'},
        'system_chromium': '/usr/bin/chromium',
    })
    monkeypatch.setattr(launch_playwright_persistent_probe.__globals__['os'], 'geteuid', lambda: 0)

    target, dom_probe, probe_json, report, cleanup = launch_playwright_persistent_probe(
        env={},
        extension_dir=tmp_path / 'extension',
        profile_dir=tmp_path / 'profile',
        expected_extension_id='abc123',
        fixture_url='http://127.0.0.1:8765/',
        timeout=1.0,
        trace_path=trace_path,
    )
    assert target['url'].startswith('chrome-extension://abc123/probe/index.html')
    assert dom_probe['ok'] == '1'
    assert probe_json['ok'] is True
    assert report['launch_strategy'] == 'playwright-channel'
    assert report['launch_channel'] == 'chromium'
    assert report['trace']['started'] is True
    assert report['trace']['requested_path'] == str(trace_path)
    assert fake_sync.runtime.chromium.kwargs['channel'] == 'chromium'
    assert 'executable_path' not in fake_sync.runtime.chromium.kwargs
    cleanup()
    assert trace_path.exists()
    assert report['trace']['saved'] is True
    assert report['trace']['exists'] is True


def test_launch_playwright_persistent_probe_uses_system_chromium_fallback_when_opted_in(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    screenshot = tmp_path / 'probe-persistent.png'
    trace_path = tmp_path / 'trace.zip'

    class FakeTracing:
        def __init__(self) -> None:
            self.started = None
            self.stopped = None

        def start(self, **kwargs) -> None:
            self.started = kwargs

        def stop(self, path: str) -> None:
            self.stopped = path
            Path(path).write_bytes(b'zip')

    class FakeMessage:
        def __init__(self, text: str) -> None:
            self.text = text
            self.type = 'log'

    class FakePage:
        def __init__(self) -> None:
            self.url = 'chrome-extension://abc123/probe/index.html?run=1'
            self._console = None

        def on(self, event: str, handler) -> None:
            assert event == 'console'
            self._console = handler

        def goto(self, url: str, wait_until: str, timeout: int) -> None:
            assert url.startswith('chrome-extension://abc123/probe/index.html')
            assert wait_until == 'load'
            assert timeout >= 1000

        def wait_for_selector(self, selector: str, timeout: int) -> None:
            assert 'data-probe-ready' in selector
            assert timeout >= 1000
            if self._console:
                self._console(FakeMessage('probe ready'))

        def evaluate(self, _expr: str) -> dict[str, str]:
            return {'ready': '1', 'ok': '1', 'summary': 'ok', 'json': '{"ok": true}'}

        def screenshot(self, path: str, full_page: bool) -> None:
            assert full_page is True
            Path(path).write_bytes(b'png')

        def title(self) -> str:
            return 'GlassTTY Probe'

    class FakeWorker:
        def __init__(self, url: str) -> None:
            self.url = url

    class FakeContext:
        def __init__(self) -> None:
            self.pages = []
            self.service_workers = [FakeWorker('chrome-extension://abc123/dist/background/main.js')]
            self.tracing = FakeTracing()

        def new_page(self) -> FakePage:
            page = FakePage()
            self.pages.append(page)
            return page

        def close(self) -> None:
            return None

    class FakeChromium:
        def __init__(self) -> None:
            self.kwargs = None

        def launch_persistent_context(self, **kwargs):
            self.kwargs = kwargs
            return FakeContext()

    class FakePlaywright:
        def __init__(self) -> None:
            self.chromium = FakeChromium()
            self.stopped = False

        def stop(self) -> None:
            self.stopped = True

    class FakeSyncPlaywright:
        def __init__(self) -> None:
            self.instance = FakePlaywright()

        def start(self) -> FakePlaywright:
            return self.instance

    fake_sync = FakeSyncPlaywright()
    monkeypatch.setitem(launch_playwright_persistent_probe.__globals__, 'sync_playwright', lambda: fake_sync)
    monkeypatch.setitem(launch_playwright_persistent_probe.__globals__, 'PLAYWRIGHT_IMPORT_ERROR', None)
    monkeypatch.setitem(launch_playwright_persistent_probe.__globals__, 'discover_playwright_browser_install', lambda **kwargs: {'available': True, 'import_error': None, 'bundled_executable_exists': False, 'system_chromium': '/usr/bin/chromium'})
    monkeypatch.setattr(launch_playwright_persistent_probe.__globals__['os'], 'geteuid', lambda: 0)

    target, dom_probe, probe_json, report, cleanup = launch_playwright_persistent_probe(
        env={'PLAYWRIGHT_BROWSERS_PATH': '/tmp/pw', 'GLASSTTY_PLAYWRIGHT_ALLOW_SYSTEM_EXECUTABLE': '1'},
        extension_dir=tmp_path / 'extension',
        profile_dir=tmp_path / 'profile',
        expected_extension_id='abc123',
        fixture_url='http://127.0.0.1:8765/',
        timeout=1.0,
        screenshot_path=screenshot,
        trace_path=trace_path,
    )

    assert report['launch_strategy'] == 'system-executable'
    assert report['trace']['started'] is True
    assert fake_sync.instance.chromium.kwargs['executable_path'] == '/usr/bin/chromium'
    assert '--no-sandbox' in fake_sync.instance.chromium.kwargs['args']
    assert target['url'].startswith('chrome-extension://abc123/probe/index.html')
    assert dom_probe['ready'] == '1'
    assert probe_json['ok'] is True
    assert report['extension_id_matches_expected'] is True
    assert screenshot.exists()
    cleanup()
    assert trace_path.exists()
    assert report['trace']['saved'] is True
    assert report['trace']['exists'] is True
    assert fake_sync.instance.stopped is True


def test_launch_playwright_persistent_probe_uses_bundled_executable_when_cache_name_drifts(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    class FakeTracing:
        def __init__(self) -> None:
            self.started = None
            self.stopped = None

        def start(self, **kwargs) -> None:
            self.started = kwargs

        def stop(self, path: str) -> None:
            self.stopped = path
            Path(path).write_bytes(b'zip')

    class FakePage:
        url = 'chrome-extension://abc123/probe/index.html?run=1'

        def on(self, event: str, handler) -> None:
            assert event == 'console'

        def goto(self, url: str, wait_until: str, timeout: int) -> None:
            assert url.startswith('chrome-extension://abc123/probe/index.html')
            assert wait_until == 'load'
            assert timeout >= 1000

        def wait_for_selector(self, selector: str, timeout: int) -> None:
            assert 'data-probe-ready' in selector
            assert timeout >= 1000

        def evaluate(self, _expr: str) -> dict[str, str]:
            return {'ready': '1', 'ok': '1', 'summary': 'ok', 'json': '{"ok": true}'}

        def title(self) -> str:
            return 'GlassTTY Probe'

    class FakeServiceWorker:
        url = 'chrome-extension://abc123/background.js'

    class FakeContext:
        def __init__(self) -> None:
            self.service_workers = [FakeServiceWorker()]
            self.pages = []
            self.tracing = FakeTracing()

        def new_page(self) -> FakePage:
            page = FakePage()
            self.pages.append(page)
            return page

        def close(self) -> None:
            return None

    class FakeChromium:
        def __init__(self) -> None:
            self.kwargs = None

        def launch_persistent_context(self, **kwargs):
            self.kwargs = kwargs
            return FakeContext()

    class FakePlaywrightRuntime:
        def __init__(self) -> None:
            self.chromium = FakeChromium()

        def stop(self) -> None:
            return None

    class FakeSyncPlaywright:
        def __init__(self) -> None:
            self.runtime = FakePlaywrightRuntime()

        def start(self) -> FakePlaywrightRuntime:
            return self.runtime

    fake_sync = FakeSyncPlaywright()
    bundled = tmp_path / 'pw' / 'chromium-cft-145.0.7632.6' / 'chrome-linux64' / 'chrome'
    bundled.parent.mkdir(parents=True)
    bundled.write_text('', encoding='utf-8')
    monkeypatch.setitem(launch_playwright_persistent_probe.__globals__, 'sync_playwright', lambda: fake_sync)
    monkeypatch.setitem(launch_playwright_persistent_probe.__globals__, 'PLAYWRIGHT_IMPORT_ERROR', None)
    monkeypatch.setitem(launch_playwright_persistent_probe.__globals__, 'discover_playwright_browser_install', lambda **kwargs: {
        'available': True,
        'import_error': None,
        'bundled_executable_exists': True,
        'bundled_executable': str(bundled),
        'bundled_install': {'source': 'archive-import', 'package_name': 'chromium', 'install_name': 'chromium-cft-145.0.7632.6'},
        'expected_browser_package': {'package_name': 'chromium', 'install_name': 'chromium-1208'},
        'system_chromium': '/usr/bin/chromium',
    })
    monkeypatch.setattr(launch_playwright_persistent_probe.__globals__['os'], 'geteuid', lambda: 0)

    target, dom_probe, probe_json, report, cleanup = launch_playwright_persistent_probe(
        env={},
        extension_dir=tmp_path / 'extension',
        profile_dir=tmp_path / 'profile',
        expected_extension_id='abc123',
        fixture_url='http://127.0.0.1:8765/',
        timeout=1.0,
        trace_path=tmp_path / 'trace.zip',
    )

    assert target['url'].startswith('chrome-extension://abc123/probe/index.html')
    assert dom_probe['ready'] == '1'
    assert probe_json['ok'] is True
    assert report['launch_strategy'] == 'bundled-executable'
    assert fake_sync.runtime.chromium.kwargs['executable_path'] == str(bundled)
    assert 'channel' not in fake_sync.runtime.chromium.kwargs
    cleanup()


def test_launch_playwright_persistent_probe_skips_system_fallback_by_default(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setitem(launch_playwright_persistent_probe.__globals__, 'sync_playwright', object())
    monkeypatch.setitem(launch_playwright_persistent_probe.__globals__, 'PLAYWRIGHT_IMPORT_ERROR', None)
    monkeypatch.setitem(launch_playwright_persistent_probe.__globals__, 'discover_playwright_browser_install', lambda **kwargs: {'available': True, 'import_error': None, 'bundled_executable_exists': False, 'system_chromium': '/usr/bin/chromium'})
    with pytest.raises(RuntimeError) as excinfo:
        launch_playwright_persistent_probe(
            env={'PLAYWRIGHT_BROWSERS_PATH': '/tmp/pw'},
            extension_dir=tmp_path / 'extension',
            profile_dir=tmp_path / 'profile',
            expected_extension_id='abc123',
            fixture_url='http://127.0.0.1:8765/',
            timeout=1.0,
        )
    assert 'skipping the Playwright persistent lane by default' in str(excinfo.value)


def test_wait_for_probe_result_playwright_parses_probe_json(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    screenshot = tmp_path / 'probe.png'

    class FakeMessage:
        def __init__(self, text: str) -> None:
            self.text = text
            self.type = 'log'

    class FakePage:
        def __init__(self) -> None:
            self.url = 'chrome-extension://abc123/probe/index.html?run=1'
            self._console = None

        def on(self, event: str, handler) -> None:
            assert event == 'console'
            self._console = handler

        def wait_for_selector(self, selector: str, timeout: int) -> None:
            assert 'data-probe-ready' in selector
            assert timeout >= 1000
            if self._console:
                self._console(FakeMessage('probe ready'))

        def evaluate(self, _expr: str) -> dict[str, str]:
            return {'ready': '1', 'ok': '1', 'summary': 'ok', 'json': '{"ok": true, "fixture": {"latestOutput": "hello"}}'}

        def screenshot(self, path: str, full_page: bool) -> None:
            assert full_page is True
            Path(path).write_bytes(b'png')

        def title(self) -> str:
            return 'GlassTTY Probe'

    class FakeWorker:
        def __init__(self, url: str) -> None:
            self.url = url

    class FakeContext:
        def __init__(self) -> None:
            self.pages = [FakePage()]
            self.service_workers = [FakeWorker('chrome-extension://abc123/dist/background/main.js')]

    class FakeBrowser:
        def __init__(self) -> None:
            self.contexts = [FakeContext()]

    class FakeChromium:
        def connect_over_cdp(self, endpoint: str, timeout: int, is_local: bool):
            assert endpoint == 'http://127.0.0.1:9222'
            assert timeout >= 1000
            assert is_local is True
            return FakeBrowser()

    class FakePlaywright:
        def __init__(self) -> None:
            self.chromium = FakeChromium()

        def stop(self) -> None:
            return None

    class FakeSyncPlaywright:
        def start(self) -> FakePlaywright:
            return FakePlaywright()

    monkeypatch.setitem(wait_for_probe_result_playwright.__globals__, 'sync_playwright', lambda: FakeSyncPlaywright())
    monkeypatch.setitem(wait_for_probe_result_playwright.__globals__, 'PLAYWRIGHT_IMPORT_ERROR', None)

    target, dom_probe, probe_json, report = wait_for_probe_result_playwright(
        port=9222,
        extension_id='abc123',
        timeout=1.0,
        screenshot_path=screenshot,
    )

    assert target['url'].startswith('chrome-extension://abc123/probe/index.html')
    assert dom_probe['ready'] == '1'
    assert probe_json['ok'] is True
    assert report['connected'] is True
    assert report['service_worker_urls'] == ['chrome-extension://abc123/dist/background/main.js']
    assert report['connect_over_cdp_kwargs']['is_local'] is True
    assert screenshot.exists()


def test_launch_playwright_persistent_probe_records_service_worker_telemetry(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    class FakeMessage:
        def __init__(self, text: str, message_type: str = 'log') -> None:
            self.text = text
            self.type = message_type

    class FakeResponse:
        def __init__(self, status: int) -> None:
            self.status = status

    class FakeRequest:
        def __init__(self, worker, url: str, *, method: str = 'GET', resource_type: str = 'fetch', failure: str | None = None, status: int | None = None) -> None:
            self.url = url
            self.method = method
            self.resource_type = resource_type
            self.is_navigation_request = False
            self.service_worker = worker
            self.failure = failure
            self._response = FakeResponse(status) if status is not None else None

        def response(self):
            return self._response

    class FakeWorker:
        def __init__(self, url: str) -> None:
            self.url = url
            self.handlers: dict[str, object] = {}

        def on(self, event: str, handler) -> None:
            self.handlers[event] = handler

        def emit(self, event: str, payload=None) -> None:
            handler = self.handlers.get(event)
            if handler:
                if payload is None:
                    handler(self)
                else:
                    handler(payload)

        def evaluate(self, _expr: str) -> dict[str, object]:
            return {'scope': 'chrome-extension://abc123/', 'hasClientsMatchAll': True}

    class FakeTracing:
        def start(self, **kwargs) -> None:
            return None

        def stop(self, path: str) -> None:
            Path(path).write_bytes(b'zip')

    class FakePage:
        def __init__(self, context, worker) -> None:
            self.url = 'chrome-extension://abc123/probe/index.html?run=1'
            self._console = None
            self.context = context
            self.worker = worker

        def on(self, event: str, handler) -> None:
            assert event == 'console'
            self._console = handler

        def goto(self, url: str, wait_until: str, timeout: int) -> None:
            assert url.startswith('chrome-extension://abc123/probe/index.html')
            assert wait_until == 'load'
            assert timeout >= 1000

        def wait_for_selector(self, selector: str, timeout: int) -> None:
            assert 'data-probe-ready' in selector
            assert timeout >= 1000
            self.context.emit('request', FakeRequest(self.worker, 'https://example.test/sw.js', status=200))
            self.context.emit('requestfailed', FakeRequest(self.worker, 'https://example.test/sw-fail.js', failure='net::ERR_FAILED'))
            self.context.emit('console', FakeMessage('context log'))
            self.context.emit('weberror', RuntimeError('context exploded'))
            self.worker.emit('console', FakeMessage('worker log'))
            self.worker.emit('close')
            if self._console:
                self._console(FakeMessage('probe ready'))

        def evaluate(self, _expr: str) -> dict[str, str]:
            return {'ready': '1', 'ok': '1', 'summary': 'ok', 'json': '{"ok": true}'}

        def title(self) -> str:
            return 'GlassTTY Probe'

    class FakeContext:
        def __init__(self) -> None:
            self.worker = FakeWorker('chrome-extension://abc123/dist/background/main.js')
            self.pages = []
            self.service_workers = [self.worker]
            self.tracing = FakeTracing()
            self.handlers: dict[str, list[object]] = {}

        def on(self, event: str, handler) -> None:
            self.handlers.setdefault(event, []).append(handler)

        def emit(self, event: str, payload) -> None:
            for handler in self.handlers.get(event, []):
                handler(payload)

        def new_page(self) -> FakePage:
            page = FakePage(self, self.worker)
            self.pages.append(page)
            return page

        def close(self) -> None:
            return None

    class FakeChromium:
        def launch_persistent_context(self, **kwargs):
            return FakeContext()

    class FakePlaywright:
        def __init__(self) -> None:
            self.chromium = FakeChromium()

        def stop(self) -> None:
            return None

    class FakeSyncPlaywright:
        def start(self) -> FakePlaywright:
            return FakePlaywright()

    monkeypatch.setitem(launch_playwright_persistent_probe.__globals__, 'sync_playwright', lambda: FakeSyncPlaywright())
    monkeypatch.setitem(launch_playwright_persistent_probe.__globals__, 'PLAYWRIGHT_IMPORT_ERROR', None)
    monkeypatch.setitem(launch_playwright_persistent_probe.__globals__, 'discover_playwright_browser_install', lambda **kwargs: {'available': True, 'import_error': None, 'bundled_executable_exists': False, 'system_chromium': '/usr/bin/chromium'})
    monkeypatch.setattr(launch_playwright_persistent_probe.__globals__['os'], 'geteuid', lambda: 0)

    _target, _dom_probe, _probe_json, report, cleanup = launch_playwright_persistent_probe(
        env={'GLASSTTY_PLAYWRIGHT_ALLOW_SYSTEM_EXECUTABLE': '1'},
        extension_dir=tmp_path / 'extension',
        profile_dir=tmp_path / 'profile',
        expected_extension_id='abc123',
        fixture_url='http://127.0.0.1:8765/',
        timeout=1.0,
        trace_path=tmp_path / 'trace.zip',
    )
    cleanup()

    assert report['service_worker_snapshots'][0]['url'].endswith('background/main.js')
    assert report['service_worker_initial_snapshot']['url'].endswith('background/main.js')
    assert report['service_worker_wait']['healthy'] is True
    assert report['service_worker_events'][0]['event'] == 'seen'
    assert any(item['event'] == 'close' for item in report['service_worker_events'])
    assert report['service_worker_console_messages'][0]['text'] == 'worker log'
    assert report['context_console_messages'][0]['text'] == 'context log'
    assert report['context_weberrors'][0]['message'] == 'context exploded'
    assert report['service_worker_requests'][0]['service_worker_url'].endswith('background/main.js')
    assert report['service_worker_request_failures'][0]['failure'] == 'net::ERR_FAILED'


def test_wait_for_probe_result_playwright_records_service_worker_context_telemetry(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    class FakeMessage:
        def __init__(self, text: str, message_type: str = 'log') -> None:
            self.text = text
            self.type = message_type

    class FakeWorker:
        def __init__(self, url: str) -> None:
            self.url = url
            self.handlers: dict[str, object] = {}

        def on(self, event: str, handler) -> None:
            self.handlers[event] = handler

        def emit(self, event: str, payload=None) -> None:
            handler = self.handlers.get(event)
            if handler:
                if payload is None:
                    handler(self)
                else:
                    handler(payload)

        def evaluate(self, _expr: str) -> dict[str, object]:
            return {'origin': 'chrome-extension://abc123'}

    class FakeRequest:
        def __init__(self, worker) -> None:
            self.url = 'https://example.test/from-sw'
            self.method = 'GET'
            self.resource_type = 'fetch'
            self.is_navigation_request = False
            self.service_worker = worker
            self.failure = None

        def response(self):
            return None

    class FakePage:
        def __init__(self, context, worker) -> None:
            self.url = 'chrome-extension://abc123/probe/index.html?run=1'
            self._console = None
            self.context = context
            self.worker = worker

        def on(self, event: str, handler) -> None:
            assert event == 'console'
            self._console = handler

        def wait_for_selector(self, selector: str, timeout: int) -> None:
            assert 'data-probe-ready' in selector
            assert timeout >= 1000
            self.worker.emit('console', FakeMessage('worker hello'))
            self.context.emit('requestfinished', FakeRequest(self.worker))
            if self._console:
                self._console(FakeMessage('probe ready'))

        def evaluate(self, _expr: str) -> dict[str, str]:
            return {'ready': '1', 'ok': '1', 'summary': 'ok', 'json': '{"ok": true}'}

        def screenshot(self, path: str, full_page: bool) -> None:
            Path(path).write_bytes(b'png')

        def title(self) -> str:
            return 'GlassTTY Probe'

    class FakeContext:
        def __init__(self) -> None:
            self.worker = FakeWorker('chrome-extension://abc123/dist/background/main.js')
            self.pages = [FakePage(self, self.worker)]
            self.service_workers = [self.worker]
            self.handlers: dict[str, list[object]] = {}

        def on(self, event: str, handler) -> None:
            self.handlers.setdefault(event, []).append(handler)

        def emit(self, event: str, payload) -> None:
            for handler in self.handlers.get(event, []):
                handler(payload)

    class FakeBrowser:
        def __init__(self) -> None:
            self.contexts = [FakeContext()]

    class FakeChromium:
        def connect_over_cdp(self, endpoint: str, timeout: int, is_local: bool):
            assert endpoint == 'http://127.0.0.1:9222'
            assert timeout >= 1000
            assert is_local is True
            return FakeBrowser()

    class FakePlaywright:
        def __init__(self) -> None:
            self.chromium = FakeChromium()

        def stop(self) -> None:
            return None

    class FakeSyncPlaywright:
        def start(self) -> FakePlaywright:
            return FakePlaywright()

    monkeypatch.setitem(wait_for_probe_result_playwright.__globals__, 'sync_playwright', lambda: FakeSyncPlaywright())
    monkeypatch.setitem(wait_for_probe_result_playwright.__globals__, 'PLAYWRIGHT_IMPORT_ERROR', None)

    _target, _dom_probe, _probe_json, report = wait_for_probe_result_playwright(
        port=9222,
        extension_id='abc123',
        timeout=1.0,
        screenshot_path=tmp_path / 'probe.png',
    )

    assert report['service_worker_snapshots'][0]['runtime']['origin'] == 'chrome-extension://abc123'
    assert report['service_worker_initial_snapshot']['runtime']['origin'] == 'chrome-extension://abc123'
    assert report['service_worker_wait']['healthy'] is True
    assert report['service_worker_console_messages'][0]['text'] == 'worker hello'
    assert report['service_worker_requests'][0]['event'] == 'requestfinished'


@pytest.mark.skipif(os.environ.get('GLASSTTY_RUN_E2E') != '1', reason='set GLASSTTY_RUN_E2E=1 to run the real browser/native-host fixture-lab smoke')
def test_fixturelab_e2e_smoke(tmp_path: Path) -> None:
    output = tmp_path / 'e2e-report.json'
    subprocess.check_call(
        [sys.executable, str(ROOT / 'scripts' / 'e2e-fixturelab.py'), '--output', str(output), '--timeout', '25'],
        cwd=ROOT,
        env={**os.environ, 'PYTHONPATH': str(ROOT / 'daemon' / 'src') + (os.pathsep + os.environ['PYTHONPATH'] if os.environ.get('PYTHONPATH') else '')},
    )
    assert output.exists()


def test_run_cli_step_retries_until_success(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = {'count': 0}

    class Result:
        def __init__(self, returncode: int, stdout: str = '', stderr: str = '') -> None:
            self.returncode = returncode
            self.stdout = stdout
            self.stderr = stderr

    def fake_run(argv, cwd=None, env=None, capture_output=None, text=None, timeout=None, check=None):
        calls['count'] += 1
        if calls['count'] == 1:
            return Result(1, stdout='', stderr='first failure')
        return Result(0, stdout='{"ok": true}', stderr='')

    monkeypatch.setattr(run_cli_step.__globals__['subprocess'], 'run', fake_run)
    monkeypatch.setattr(run_cli_step.__globals__['time'], 'sleep', lambda _seconds: None)

    step = run_cli_step('demo', ['python', '-m', 'glassttyd.cli', 'ping'], env={}, timeout=1.0, retries=2)

    assert step['ok'] is True
    assert calls['count'] == 2
    assert step['stdout_json'] == {'ok': True}
    assert len(step['attempts']) == 2


def test_discover_browser_executable_prefers_local_cft(tmp_path: Path) -> None:
    browser = tmp_path / 'browsers' / 'chrome-for-testing' / '136.0.7103.92' / 'chrome-linux64' / 'chrome'
    browser.parent.mkdir(parents=True)
    browser.write_text('', encoding='utf-8')
    choice = discover_browser_executable(env={'GLASSTTY_HOME': str(tmp_path)})
    assert choice['source'] == 'chrome-for-testing'
    assert choice['path'] == str(browser)


def test_native_host_install_targets_follow_browser_choice() -> None:
    assert native_host_install_targets({'native_messaging_targets': ['chrome']}) == ['chrome']
    assert native_host_install_targets({'native_messaging_targets': ['chrome', 'chrome-for-testing']}) == ['chrome', 'chrome-for-testing']
    assert native_host_install_targets({'native_messaging_targets': ['chrome']}, {'native_messaging_targets': ['chromium']}) == ['chromium', 'chrome']
    assert native_host_install_targets({}, {'native_messaging_targets': ['chromium']}) == ['chromium']
    assert native_host_install_targets({}) == ['chromium']


def test_wait_for_probe_result_playwright_omits_is_local_when_not_supported(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeContext:
        def __init__(self) -> None:
            self.pages = []
            self.service_workers = []

    class FakeBrowser:
        def __init__(self) -> None:
            self.contexts = [FakeContext()]

    class FakeChromium:
        def __init__(self) -> None:
            self.called = None

        def connect_over_cdp(self, endpoint: str, timeout: int):
            self.called = {'endpoint': endpoint, 'timeout': timeout}
            return FakeBrowser()

    class FakePlaywright:
        def __init__(self) -> None:
            self.chromium = FakeChromium()

        def stop(self) -> None:
            return None

    class FakeSyncPlaywright:
        def __init__(self) -> None:
            self.instance = FakePlaywright()

        def start(self) -> FakePlaywright:
            return self.instance

    fake_sync = FakeSyncPlaywright()
    monkeypatch.setitem(wait_for_probe_result_playwright.__globals__, 'sync_playwright', lambda: fake_sync)
    monkeypatch.setitem(wait_for_probe_result_playwright.__globals__, 'PLAYWRIGHT_IMPORT_ERROR', None)

    with pytest.raises(RuntimeError):
        wait_for_probe_result_playwright(port=9222, extension_id='abc123', timeout=0.1)

    assert fake_sync.instance.chromium.called == {'endpoint': 'http://127.0.0.1:9222', 'timeout': 100}


def test_extension_context_summary_reports_background_context() -> None:
    summary = extension_context_summary(
        {
            'bridge': {
                'contexts': {
                    'runtimeId': 'abc123',
                    'hasRuntimeGetContexts': True,
                    'openContexts': [
                        {'contextId': 'ctx-bg', 'contextType': 'BACKGROUND', 'tabId': -1, 'windowId': -1, 'frameId': -1},
                        {'contextId': 'ctx-offscreen', 'contextType': 'OFFSCREEN_DOCUMENT', 'documentUrl': 'chrome-extension://abc123/offscreen/index.html'},
                        {'contextId': 'ctx-probe', 'contextType': 'TAB', 'tabId': 5, 'windowId': 3, 'frameId': 0, 'documentUrl': 'chrome-extension://abc123/probe/index.html'},
                    ],
                },
            },
        },
        expected_extension_id='abc123',
    )
    assert summary['available'] is True
    assert summary['runtime_id'] == 'abc123'
    assert summary['runtime_id_matches_extension'] is True
    assert summary['background_context_seen'] is True
    assert summary['background_context_count'] == 1
    assert summary['offscreen_context_count'] == 1
    assert summary['offscreen_context_seen'] is True
    assert 'BACKGROUND' in summary['context_types']
    assert 'OFFSCREEN_DOCUMENT' in summary['context_types']
    assert summary['tab_context_count'] == 1


def test_probe_url_can_skip_fixture_flow() -> None:
    url = probe_url('abc123')
    assert url == 'chrome-extension://abc123/probe/index.html?run=1&write=hello+from+GlassTTY+e2e+smoke'


def test_open_probe_page_uses_optional_fixture_flow(tmp_path: Path) -> None:
    class FakeMessage:
        def __init__(self, text: str, message_type: str = 'log') -> None:
            self.text = text
            self.type = message_type

    class FakePage:
        def __init__(self) -> None:
            self.url = 'chrome-extension://abc123/probe/index.html?run=1&write=hello'
            self.events: dict[str, object] = {}
            self.goto_calls: list[dict[str, object]] = []
            self.selector_calls: list[dict[str, object]] = []
            self.screenshots: list[str] = []

        def on(self, event: str, handler) -> None:
            self.events[event] = handler

        def goto(self, url: str, wait_until: str, timeout: int) -> None:
            self.goto_calls.append({'url': url, 'wait_until': wait_until, 'timeout': timeout})
            handler = self.events.get('console')
            if callable(handler):
                handler(FakeMessage('probe booted'))

        def wait_for_selector(self, selector: str, timeout: int) -> None:
            self.selector_calls.append({'selector': selector, 'timeout': timeout})

        def evaluate(self, _script: str):
            return {
                'ready': '1',
                'ok': '1',
                'summary': 'ok',
                'json': json.dumps({'bridge': {'status': {'nativeConnection': {'connected': True}}}}),
            }

        def screenshot(self, path: str, full_page: bool) -> None:
            Path(path).write_text('fake screenshot', encoding='utf-8')
            self.screenshots.append(path)

    class FakeContext:
        def __init__(self) -> None:
            self.page = FakePage()

        def new_page(self) -> FakePage:
            return self.page

    context = FakeContext()
    screenshot = tmp_path / 'probe.png'
    opened_page, dom_result, parsed_json, console_messages = open_probe_page(
        context,
        extension_id='abc123',
        timeout=0.5,
        fixture_url=None,
        write_text='hello',
        screenshot_path=screenshot,
    )
    assert opened_page is context.page
    assert context.page.goto_calls[0]['url'] == 'chrome-extension://abc123/probe/index.html?run=1&write=hello'
    assert dom_result['ok'] == '1'
    assert parsed_json['bridge']['status']['nativeConnection']['connected'] is True
    assert console_messages == [{'type': 'log', 'text': 'probe booted'}]
    assert screenshot.exists()


def test_stop_extension_service_worker_playwright_closes_matching_target() -> None:
    calls: list[tuple[str, dict[str, object] | None]] = []

    class FakeSession:
        def send(self, method: str, params: dict[str, object] | None = None):
            calls.append((method, params))
            if method == 'Target.getTargets':
                return {
                    'targetInfos': [
                        {'targetId': 'worker-1', 'type': 'service_worker', 'url': 'chrome-extension://abc123/background/main.js'},
                        {'targetId': 'page-1', 'type': 'page', 'url': 'chrome-extension://abc123/probe/index.html'},
                    ],
                }
            if method == 'Target.closeTarget':
                return {'success': True}
            raise AssertionError(method)

        def detach(self) -> None:
            return None

    class FakeBrowser:
        def new_browser_cdp_session(self) -> FakeSession:
            return FakeSession()

    browser = FakeBrowser()
    report = stop_extension_service_worker_playwright(browser, extension_id='abc123', timeout=0.5)
    assert report['closed'] is True
    assert report['closed_target_id'] == 'worker-1'
    assert calls[0][0] == 'Target.getTargets'
    assert calls[1] == ('Target.closeTarget', {'targetId': 'worker-1'})


def test_worker_resume_summary_detects_boot_change_and_recovery() -> None:
    before = {
        'bridge': {
            'status': {
                'nativeConnection': {'connected': False, 'lastOneShotProbeOk': False},
                'persistentDiagnostics': {
                    'currentBootId': 'boot-1',
                    'workerBoots': [{'bootId': 'boot-1', 'bootCount': 1}],
                    'runtimeHint': {'status': 'restart_pending'},
                },
            },
        },
    }
    after = {
        'bridge': {
            'status': {
                'nativeConnection': {'connected': True, 'lastOneShotProbeOk': True},
                'persistentDiagnostics': {
                    'currentBootId': 'boot-2',
                    'workerBoots': [{'bootId': 'boot-1', 'bootCount': 1}, {'bootId': 'boot-2', 'bootCount': 2}],
                    'runtimeHint': {'status': 'current_boot_connected'},
                },
            },
        },
    }
    summary = worker_resume_summary(before, after)
    assert summary['boot_changed'] is True
    assert summary['boot_count_increased'] is True
    assert summary['native_recovered'] is True
    assert summary['ok'] is True


def test_attach_playwright_extension_context_uses_cdp_endpoint(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    class FakeWorker:
        def __init__(self, url: str) -> None:
            self.url = url
        def evaluate(self, _expr: str) -> dict[str, object]:
            return {'scope': 'chrome-extension://abc123/', 'hasClientsMatchAll': True}
        def on(self, _event: str, _handler) -> None:
            return None

    class FakeTracing:
        def start(self, **kwargs) -> None:
            return None
        def stop(self, path: str) -> None:
            Path(path).write_bytes(b'zip')

    class FakeContext:
        def __init__(self) -> None:
            self.service_workers = [FakeWorker('chrome-extension://abc123/dist/background/main.js')]
            self.pages = []
            self.tracing = FakeTracing()
            self.handlers = {}
        def on(self, event: str, handler) -> None:
            self.handlers[event] = handler

    class FakeBrowser:
        def __init__(self) -> None:
            self.contexts = [FakeContext()]

    calls: list[tuple[str, object]] = []

    class FakeChromium:
        def connect_over_cdp(self, endpoint, timeout: int, is_local: bool | None = None):
            calls.append((endpoint, {'timeout': timeout, 'is_local': is_local}))
            return FakeBrowser()

    class FakePlaywright:
        def __init__(self) -> None:
            self.chromium = FakeChromium()
        def stop(self) -> None:
            return None

    class FakeSyncPlaywright:
        def start(self) -> FakePlaywright:
            return FakePlaywright()

    monkeypatch.setitem(attach_playwright_extension_context.__globals__, 'sync_playwright', lambda: FakeSyncPlaywright())
    monkeypatch.setitem(attach_playwright_extension_context.__globals__, 'PLAYWRIGHT_IMPORT_ERROR', None)

    _context, report, cleanup = attach_playwright_extension_context(cdp_endpoint='http://127.0.0.1:9222', expected_extension_id='abc123', timeout=1.0, trace_path=tmp_path / 'trace.zip')
    assert report['launch_strategy'] == 'cdp-attach'
    assert report['connected'] is True
    assert report['observed_extension_id'] == 'abc123'
    assert report['extension_id_matches_expected'] is True
    assert calls[0][0] == 'http://127.0.0.1:9222'
    cleanup()


def test_worker_resume_summary_detects_boot_change_context_recovery_and_native_recovery() -> None:
    before = {'bridge': {'status': {'nativeConnection': {'connected': False, 'lastOneShotProbeOk': False}, 'persistentDiagnostics': {'currentBootId': 'boot-1', 'workerBoots': [{'bootId': 'boot-1', 'bootCount': 1}], 'runtimeHint': {'status': 'restart_pending'}}}, 'contexts': {'runtimeId': 'abc123', 'hasRuntimeGetContexts': True, 'openContexts': [{'contextType': 'BACKGROUND'}, {'contextType': 'OFFSCREEN_DOCUMENT'}]}}}
    after = {'bridge': {'status': {'nativeConnection': {'connected': True, 'lastOneShotProbeOk': True}, 'persistentDiagnostics': {'currentBootId': 'boot-2', 'workerBoots': [{'bootId': 'boot-1', 'bootCount': 1}, {'bootId': 'boot-2', 'bootCount': 2}], 'runtimeHint': {'status': 'current_boot_connected'}}}, 'contexts': {'runtimeId': 'abc123', 'hasRuntimeGetContexts': True, 'openContexts': [{'contextType': 'BACKGROUND'}, {'contextType': 'OFFSCREEN_DOCUMENT'}, {'contextType': 'SIDE_PANEL'}]}}}
    summary = worker_resume_summary(before, after)
    assert summary['context_evidence_available'] is True
    assert summary['runtime_id_stable'] is True
    assert summary['background_context_recovered'] is True
    assert summary['proof_grade'] == 'strict_context_recovery'
    assert summary['ok'] is True


def test_worker_resume_summary_allows_legacy_ok_when_contexts_are_missing() -> None:
    before = {'bridge': {'status': {'nativeConnection': {'connected': False, 'lastOneShotProbeOk': False}, 'persistentDiagnostics': {'currentBootId': 'boot-1', 'workerBoots': [{'bootId': 'boot-1', 'bootCount': 1}]}}}}
    after = {'bridge': {'status': {'nativeConnection': {'connected': True, 'lastOneShotProbeOk': True}, 'persistentDiagnostics': {'currentBootId': 'boot-2', 'workerBoots': [{'bootId': 'boot-1', 'bootCount': 1}, {'bootId': 'boot-2', 'bootCount': 2}]}}}}
    summary = worker_resume_summary(before, after)
    assert summary['context_evidence_available'] is False
    assert summary['proof_grade'] == 'legacy_boot_and_native_only'
    assert summary['ok'] is True
