from __future__ import annotations

import json
import os
import socket
import stat
import subprocess
import sys
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
PROFILE_SPEC = importlib.util.spec_from_file_location('glasstty_profile_metadata_testshim', ROOT / 'scripts' / 'profile_metadata.py')
assert PROFILE_SPEC and PROFILE_SPEC.loader
PROFILE_MODULE = importlib.util.module_from_spec(PROFILE_SPEC)
PROFILE_SPEC.loader.exec_module(PROFILE_MODULE)
write_mv3_resume_artifacts = PROFILE_MODULE.write_mv3_resume_artifacts
build_reopen_launch_plan = PROFILE_MODULE.build_reopen_launch_plan



def _make_fake_browser(tmp_path: Path) -> tuple[Path, Path]:
    capture = tmp_path / 'capture.json'
    browser = tmp_path / 'fake-browser.py'
    browser.write_text(
        '#!/usr/bin/env python3\n'
        'import json, os, sys\n'
        'from pathlib import Path\n'
        'Path(os.environ["GLASSTTY_TEST_CAPTURE"]).write_text(json.dumps(sys.argv[1:]), encoding="utf-8")\n',
        encoding='utf-8',
    )
    browser.chmod(browser.stat().st_mode | stat.S_IXUSR)
    return browser, capture


def test_launch_chromium_profile_records_metadata_and_remote_debugging(tmp_path: Path) -> None:
    browser, capture = _make_fake_browser(tmp_path)
    glasstty_home = tmp_path / 'glasstty-home'
    env = dict(os.environ)
    env['GLASSTTY_HOME'] = str(glasstty_home)
    env['CHROMIUM_BIN'] = str(browser)
    env['GLASSTTY_TEST_CAPTURE'] = str(capture)

    subprocess.check_call(
        [
            str(ROOT / 'scripts' / 'launch-chromium-profile.sh'),
            'lab',
            '--remote-debugging-port',
            'auto',
            'chrome://extensions/',
        ],
        env=env,
    )

    argv = json.loads(capture.read_text(encoding='utf-8'))
    profile_dir = glasstty_home / 'profiles' / 'lab'
    assert f'--user-data-dir={profile_dir}' in argv
    assert '--remote-debugging-port=0' in argv
    assert any(arg.startswith('--disable-extensions-except=') for arg in argv)
    assert any(arg.startswith('--load-extension=') for arg in argv)
    assert 'chrome://extensions/' in argv

    metadata = json.loads((profile_dir / 'glasstty-profile.json').read_text(encoding='utf-8'))
    assert metadata['profile_name'] == 'lab'
    assert metadata['extension_loaded'] is True
    assert metadata['start_url'] == 'chrome://extensions/'
    assert metadata['browser']['path'] == str(browser)
    assert metadata['remote_debugging']['requested'] is True
    assert metadata['remote_debugging']['mode'] == 'ephemeral'
    assert metadata['remote_debugging']['port'] == '0'
    assert metadata['native_host_audit_path'].endswith('glasstty-native-host.json')

    native_host_audit = json.loads((profile_dir / 'glasstty-native-host.json').read_text(encoding='utf-8'))
    assert native_host_audit['browser_bin'] == str(browser)
    assert native_host_audit['recommended_target_status']['primary_target'] == 'chromium'


def test_glasstty_profile_info_reports_launch_and_devtools_state(tmp_path: Path) -> None:
    glasstty_home = tmp_path / 'glasstty-home'
    env = dict(os.environ)
    env['GLASSTTY_HOME'] = str(glasstty_home)
    profile_dir = glasstty_home / 'profiles' / 'main'
    subprocess.check_call(
        [
            sys.executable,
            str(ROOT / 'scripts' / 'profile-report.py'),
            'record-launch',
            '--profile-dir',
            str(profile_dir),
            '--profile-name',
            'main',
            '--chromium-bin',
            '/usr/bin/chromium',
            '--extension-loaded',
            '--extension-dir',
            str(ROOT / 'extension'),
            '--remote-debugging-mode',
            'fixed',
            '--remote-debugging-port',
            '9222',
            '--arg',
            'http://127.0.0.1:8765/',
        ],
        env=env,
    )
    (profile_dir / 'DevToolsActivePort').write_text('9222\n/devtools/browser/abc\n', encoding='utf-8')

    output = subprocess.check_output(
        [str(ROOT / 'scripts' / 'glasstty-profile.sh'), 'info', 'main', '--pretty'],
        env=env,
        text=True,
    )
    info = json.loads(output)
    assert info['name'] == 'main'
    assert info['metadata_exists'] is True
    assert info['native_host_audit_exists'] is False
    assert info['last_launch']['remote_debugging']['requested'] is True
    assert info['last_launch']['remote_debugging']['port'] == '9222'
    assert info['devtools_active_port']['port'] == '9222'
    assert info['devtools_active_port']['browser_websocket_path'] == '/devtools/browser/abc'
    assert info['cdp_endpoint_hint']['ok'] is True
    assert info['cdp_endpoint_hint']['preferred_endpoint'] == 'http://127.0.0.1:9222'
    assert info['mv3_resume_summary_exists'] is False




def test_build_reopen_launch_plan_preserves_saved_launch_recipe(tmp_path: Path) -> None:
    profile_dir = tmp_path / 'profiles' / 'lab'
    profile_dir.mkdir(parents=True, exist_ok=True)
    (profile_dir / 'glasstty-profile.json').write_text(
        json.dumps(
            {
                'profile_name': 'lab',
                'chromium_bin': '/opt/chrome/chrome',
                'extension_loaded': False,
                'extra_args': ['chrome://extensions/', '--headless=new'],
                'remote_debugging': {'requested': True, 'mode': 'ephemeral', 'port': '0'},
            }
        ),
        encoding='utf-8',
    )
    plan = build_reopen_launch_plan(profile_dir, append_args=['https://example.test/'])
    assert plan['ok'] is True
    assert plan['env_overrides']['CHROMIUM_BIN'] == '/opt/chrome/chrome'
    assert plan['argv'] == [
        './scripts/launch-chromium-profile.sh',
        'lab',
        '--skip-extension',
        '--remote-debugging-port',
        'auto',
        'chrome://extensions/',
        '--headless=new',
        'https://example.test/',
    ]
    assert 'CHROMIUM_BIN=' in plan['shell_command']


def test_build_reopen_launch_plan_marks_missing_saved_browser_and_portable_fallback(tmp_path: Path, monkeypatch) -> None:
    profile_dir = tmp_path / 'profiles' / 'portable'
    profile_dir.mkdir(parents=True, exist_ok=True)
    missing_browser = tmp_path / 'missing-browser'
    discovered_browser = tmp_path / 'chromium'
    discovered_browser.write_text('', encoding='utf-8')
    discovered_browser.chmod(discovered_browser.stat().st_mode | stat.S_IXUSR)
    monkeypatch.setenv('PATH', str(tmp_path))
    (profile_dir / 'glasstty-profile.json').write_text(
        json.dumps(
            {
                'profile_name': 'portable',
                'chromium_bin': str(missing_browser),
                'extension_loaded': True,
                'extra_args': ['chrome://extensions/'],
                'remote_debugging': {'requested': False, 'mode': None, 'port': None},
            }
        ),
        encoding='utf-8',
    )

    strict_plan = build_reopen_launch_plan(profile_dir)
    assert strict_plan['ok'] is True
    assert strict_plan['launchable_now'] is False
    assert 'saved browser path is missing' in strict_plan['error']
    assert strict_plan['portable_reopen_command'].endswith('--allow-discovered-browser-fallback')

    portable_plan = build_reopen_launch_plan(profile_dir, allow_discovered_browser_fallback=True)
    assert portable_plan['ok'] is True
    assert portable_plan['launchable_now'] is True
    assert portable_plan['used_discovered_browser_fallback'] is True
    assert portable_plan['effective_browser']['path'] == str(discovered_browser)
    assert portable_plan['env_overrides']['CHROMIUM_BIN'] == str(discovered_browser)


def test_glasstty_profile_reopen_can_fallback_to_discovered_browser(tmp_path: Path) -> None:
    browser, capture = _make_fake_browser(tmp_path)
    glasstty_home = tmp_path / 'glasstty-home'
    env = dict(os.environ)
    env['GLASSTTY_HOME'] = str(glasstty_home)
    env['GLASSTTY_TEST_CAPTURE'] = str(capture)
    env['PATH'] = f"{tmp_path}:{os.environ.get('PATH', '')}"

    profile_dir = glasstty_home / 'profiles' / 'portable'
    subprocess.check_call(
        [
            sys.executable,
            str(ROOT / 'scripts' / 'profile-report.py'),
            'record-launch',
            '--profile-dir',
            str(profile_dir),
            '--profile-name',
            'portable',
            '--chromium-bin',
            str(tmp_path / 'missing-browser'),
            '--arg',
            'chrome://extensions/',
        ],
        env=env,
    )
    browser.rename(tmp_path / 'chromium')
    subprocess.check_call([str(ROOT / 'scripts' / 'glasstty-profile.sh'), 'reopen', 'portable', '--allow-discovered-browser-fallback'], env=env)
    argv = json.loads(capture.read_text(encoding='utf-8'))
    assert f'--user-data-dir={profile_dir}' in argv
    assert 'chrome://extensions/' in argv


def test_glasstty_profile_reopen_missing_browser_reports_portable_followup(tmp_path: Path) -> None:
    glasstty_home = tmp_path / 'glasstty-home'
    env = dict(os.environ)
    env['GLASSTTY_HOME'] = str(glasstty_home)

    profile_dir = glasstty_home / 'profiles' / 'portable'
    subprocess.check_call(
        [
            sys.executable,
            str(ROOT / 'scripts' / 'profile-report.py'),
            'record-launch',
            '--profile-dir',
            str(profile_dir),
            '--profile-name',
            'portable',
            '--chromium-bin',
            str(tmp_path / 'missing-browser'),
            '--arg',
            'chrome://extensions/',
        ],
        env=env,
    )

    result = subprocess.run([str(ROOT / 'scripts' / 'glasstty-profile.sh'), 'reopen', 'portable'], env=env, capture_output=True, text=True)
    assert result.returncode != 0
    assert '--allow-discovered-browser-fallback' in result.stderr



def test_glasstty_profile_reopen_replays_saved_launch_metadata(tmp_path: Path) -> None:
    browser, capture = _make_fake_browser(tmp_path)
    glasstty_home = tmp_path / 'glasstty-home'
    env = dict(os.environ)
    env['GLASSTTY_HOME'] = str(glasstty_home)
    env['GLASSTTY_TEST_CAPTURE'] = str(capture)

    profile_dir = glasstty_home / 'profiles' / 'lab'
    subprocess.check_call(
        [
            sys.executable,
            str(ROOT / 'scripts' / 'profile-report.py'),
            'record-launch',
            '--profile-dir',
            str(profile_dir),
            '--profile-name',
            'lab',
            '--chromium-bin',
            str(browser),
            '--arg',
            'chrome://extensions/',
        ],
        env=env,
    )

    subprocess.check_call([str(ROOT / 'scripts' / 'glasstty-profile.sh'), 'reopen', 'lab', '--remote-debugging-port', 'auto'], env=env)
    argv = json.loads(capture.read_text(encoding='utf-8'))
    assert f'--user-data-dir={profile_dir}' in argv
    assert '--remote-debugging-port=0' in argv
    assert 'chrome://extensions/' in argv


def test_doctor_script_reports_profile_launch_metadata(tmp_path: Path) -> None:
    glasstty_home = tmp_path / 'glasstty-home'
    env = dict(os.environ)
    env['GLASSTTY_HOME'] = str(glasstty_home)
    profile_dir = glasstty_home / 'profiles' / 'debug'
    subprocess.check_call(
        [
            sys.executable,
            str(ROOT / 'scripts' / 'profile-report.py'),
            'record-launch',
            '--profile-dir',
            str(profile_dir),
            '--profile-name',
            'debug',
            '--chromium-bin',
            '/usr/bin/chromium',
            '--remote-debugging-mode',
            'fixed',
            '--remote-debugging-port',
            '9333',
            '--arg',
            'chrome://extensions/',
        ],
        env=env,
    )
    (profile_dir / 'DevToolsActivePort').write_text('9333\n/devtools/browser/xyz\n', encoding='utf-8')

    output = subprocess.check_output([sys.executable, str(ROOT / 'scripts' / 'doctor.py')], text=True, env=env)
    data = json.loads(output)
    profiles = data['profiles']['profiles']
    assert len(profiles) == 1
    assert profiles[0]['name'] == 'debug'
    assert profiles[0]['last_launch']['remote_debugging']['requested'] is True
    assert profiles[0]['devtools_active_port']['port'] == '9333'
    assert not any('No saved GlassTTY profile launch has requested remote debugging yet' in hint for hint in data['hints'])


def test_doctor_hints_when_saved_profile_browser_is_missing(tmp_path: Path) -> None:
    glasstty_home = tmp_path / 'glasstty-home'
    env = dict(os.environ)
    env['GLASSTTY_HOME'] = str(glasstty_home)
    env['PATH'] = f"{tmp_path}:{os.environ.get('PATH', '')}"
    discovered_browser = tmp_path / 'chromium'
    discovered_browser.write_text('', encoding='utf-8')
    discovered_browser.chmod(discovered_browser.stat().st_mode | stat.S_IXUSR)
    profile_dir = glasstty_home / 'profiles' / 'portable'
    subprocess.check_call(
        [
            sys.executable,
            str(ROOT / 'scripts' / 'profile-report.py'),
            'record-launch',
            '--profile-dir',
            str(profile_dir),
            '--profile-name',
            'portable',
            '--chromium-bin',
            str(tmp_path / 'missing-browser'),
            '--arg',
            'chrome://extensions/',
        ],
        env=env,
    )

    output = subprocess.check_output([sys.executable, str(ROOT / 'scripts' / 'doctor.py')], text=True, env=env)
    data = json.loads(output)
    assert any('saved browser path' in hint and 'allow-discovered-browser-fallback' in hint for hint in data['hints'])



def test_profile_info_reports_saved_mv3_resume_summary(tmp_path: Path) -> None:
    glasstty_home = tmp_path / 'glasstty-home'
    env = dict(os.environ)
    env['GLASSTTY_HOME'] = str(glasstty_home)
    profile_dir = glasstty_home / 'profiles' / 'lab'
    subprocess.check_call([sys.executable, str(ROOT / 'scripts' / 'profile-report.py'), 'record-launch', '--profile-dir', str(profile_dir), '--profile-name', 'lab', '--chromium-bin', '/usr/bin/chromium', '--remote-debugging-mode', 'fixed', '--remote-debugging-port', '9444'], env=env)
    (profile_dir / 'DevToolsActivePort').write_text('9444\n/devtools/browser/lab\n', encoding='utf-8')
    persisted = write_mv3_resume_artifacts(profile_dir, {'ok': True, 'phase': 'completed', 'output_path': str(tmp_path / 'resume.json'), 'resume_proof': {'proof_grade': 'strict_context_recovery', 'boot_changed': True, 'boot_count_increased': True, 'native_recovered': True, 'context_evidence_available': True}})
    assert Path(persisted['report_path']).exists()
    info = json.loads(subprocess.check_output([str(ROOT / 'scripts' / 'glasstty-profile.sh'), 'info', 'lab', '--pretty'], env=env, text=True))
    assert info['mv3_resume_report_exists'] is True
    assert info['mv3_resume_summary_exists'] is True
    assert info['mv3_resume_summary']['proof_grade'] == 'strict_context_recovery'
    assert info['cdp_endpoint_hint']['preferred_endpoint'] == 'http://127.0.0.1:9444'


def test_mv3_worker_resume_help_mentions_profile_attach() -> None:
    output = subprocess.check_output([sys.executable, str(ROOT / 'scripts' / 'mv3-worker-resume.py'), '--help'], text=True)
    assert '--profile' in output
    assert '--profile-dir' in output
    assert 'DevToolsActivePort' in output


def test_profile_info_reports_attach_ready_resume_proof_command(tmp_path: Path) -> None:
    glasstty_home = tmp_path / 'glasstty-home'
    env = dict(os.environ)
    env['GLASSTTY_HOME'] = str(glasstty_home)
    profile_dir = glasstty_home / 'profiles' / 'lab'
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind(('127.0.0.1', 0))
    listener.listen(1)
    port = listener.getsockname()[1]
    try:
        subprocess.check_call([sys.executable, str(ROOT / 'scripts' / 'profile-report.py'), 'record-launch', '--profile-dir', str(profile_dir), '--profile-name', 'lab', '--chromium-bin', '/usr/bin/chromium', '--remote-debugging-mode', 'fixed', '--remote-debugging-port', str(port)], env=env)
        (profile_dir / 'DevToolsActivePort').write_text(f'{port}\n/devtools/browser/lab-ready\n', encoding='utf-8')
        info = json.loads(subprocess.check_output([str(ROOT / 'scripts' / 'glasstty-profile.sh'), 'info', 'lab', '--pretty'], env=env, text=True))
    finally:
        listener.close()
    assert info['cdp_endpoint_hint']['ok'] is True
    assert info['cdp_endpoint_hint']['attach_ready'] is True
    assert info['cdp_endpoint_hint']['tcp_probe']['ok'] is True
    assert info['commands']['capture'] == './scripts/glasstty-profile.sh capture lab --output-dir validation/latest/profile-capture-lab'
    assert info['commands']['resume_proof'] == './scripts/glasstty-profile.sh resume-proof lab --output validation/latest/mv3-worker-resume-lab.json --timeout 25'
    assert info['cdp_endpoint_hint']['commands']['capture'].startswith('./scripts/glasstty-profile.sh capture lab ')
    assert info['cdp_endpoint_hint']['commands']['resume_proof_direct'].startswith('python scripts/mv3-worker-resume.py --profile lab ')


def test_profile_info_marks_stale_devtools_port_when_not_listening(tmp_path: Path) -> None:
    glasstty_home = tmp_path / 'glasstty-home'
    env = dict(os.environ)
    env['GLASSTTY_HOME'] = str(glasstty_home)
    profile_dir = glasstty_home / 'profiles' / 'stale'
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('127.0.0.1', 0))
    port = sock.getsockname()[1]
    sock.close()
    subprocess.check_call([sys.executable, str(ROOT / 'scripts' / 'profile-report.py'), 'record-launch', '--profile-dir', str(profile_dir), '--profile-name', 'stale', '--chromium-bin', '/usr/bin/chromium', '--remote-debugging-mode', 'fixed', '--remote-debugging-port', str(port)], env=env)
    (profile_dir / 'DevToolsActivePort').write_text(f'{port}\n/devtools/browser/stale\n', encoding='utf-8')
    info = json.loads(subprocess.check_output([str(ROOT / 'scripts' / 'glasstty-profile.sh'), 'info', 'stale', '--pretty'], env=env, text=True))
    assert info['cdp_endpoint_hint']['ok'] is True
    assert info['cdp_endpoint_hint']['attach_ready'] is False
    assert info['cdp_endpoint_hint']['tcp_probe']['attempted'] is True
    assert info['cdp_endpoint_hint']['tcp_probe']['ok'] is False
    assert 'stale' in info['cdp_endpoint_hint']['attach_warning'].lower()
    assert info['cdp_endpoint_hint']['reopen_debug_command'].startswith('CHROMIUM_BIN=/usr/bin/chromium ./scripts/launch-chromium-profile.sh stale --skip-extension --remote-debugging-port auto')
    assert info['commands']['reopen_debug'].startswith('CHROMIUM_BIN=/usr/bin/chromium ./scripts/launch-chromium-profile.sh stale --skip-extension --remote-debugging-port auto')


def test_profile_capture_writes_durable_bundle(tmp_path: Path) -> None:
    glasstty_home = tmp_path / 'glasstty-home'
    env = dict(os.environ)
    env['GLASSTTY_HOME'] = str(glasstty_home)
    profile_dir = glasstty_home / 'profiles' / 'lab'
    subprocess.check_call([
        sys.executable,
        str(ROOT / 'scripts' / 'profile-report.py'),
        'record-launch',
        '--profile-dir',
        str(profile_dir),
        '--profile-name',
        'lab',
        '--chromium-bin',
        '/usr/bin/chromium',
        '--remote-debugging-mode',
        'fixed',
        '--remote-debugging-port',
        '9555',
        '--arg',
        'chrome://extensions/',
    ], env=env)
    (profile_dir / 'glasstty-native-host.json').write_text(json.dumps({'ok': True, 'browser_bin': '/usr/bin/chromium'}), encoding='utf-8')
    (profile_dir / 'DevToolsActivePort').write_text('9555\n/devtools/browser/lab\n', encoding='utf-8')
    write_mv3_resume_artifacts(profile_dir, {
        'ok': True,
        'phase': 'completed',
        'output_path': str(tmp_path / 'resume.json'),
        'resume_proof': {
            'proof_grade': 'strict_context_recovery',
            'boot_changed': True,
            'boot_count_increased': True,
            'native_recovered': True,
            'context_evidence_available': True,
        },
    })

    output_dir = tmp_path / 'capture-out'
    bundle = json.loads(subprocess.check_output([
        str(ROOT / 'scripts' / 'glasstty-profile.sh'),
        'capture',
        'lab',
        '--output-dir',
        str(output_dir),
    ], env=env, text=True))

    assert bundle['profile']['name'] == 'lab'
    assert bundle['paths']['bundle_summary'].endswith('bundle-summary.json')
    assert (output_dir / 'profile-info.json').exists()
    assert (output_dir / 'doctor.json').exists()
    assert (output_dir / 'native-host-current-browser.json').exists()
    assert (output_dir / 'native-host-saved-browser.json').exists()
    assert (output_dir / 'native-host-effective-browser.json').exists()
    assert (output_dir / 'SUMMARY.md').exists()
    assert (output_dir / 'capture-history.json').exists()
    assert (output_dir / 'capture-diff.json').exists()
    assert (output_dir / 'profile-artifacts' / 'glasstty-profile.json').exists()
    assert (output_dir / 'profile-artifacts' / 'glasstty-native-host.json').exists()
    assert (output_dir / 'profile-artifacts' / 'DevToolsActivePort').exists()
    assert (output_dir / 'profile-artifacts' / 'glasstty-mv3-worker-resume.json').exists()
    assert (output_dir / 'profile-artifacts' / 'glasstty-mv3-worker-resume-summary.json').exists()
    summary_md = (output_dir / 'SUMMARY.md').read_text(encoding='utf-8')
    assert './scripts/glasstty-profile.sh resume-proof lab' in summary_md
    assert './scripts/glasstty-profile.sh capture lab --output-dir validation/latest/profile-capture-lab' in summary_md
    assert './scripts/glasstty-profile.sh captures lab --pretty' in summary_md
    assert 'native-host-saved-browser.json' in summary_md
    assert 'capture-history.json' in summary_md
    copied = {item['name']: item for item in bundle['copied_profile_artifacts']}
    assert copied['glasstty-profile.json']['copied'] is True
    assert copied['glasstty-native-host.json']['copied'] is True
    assert copied['glasstty-mv3-worker-resume-summary.json']['copied'] is True



def test_profile_capture_updates_profile_local_history_and_diff(tmp_path: Path) -> None:
    glasstty_home = tmp_path / 'glasstty-home'
    env = dict(os.environ)
    env['GLASSTTY_HOME'] = str(glasstty_home)
    profile_dir = glasstty_home / 'profiles' / 'ledger'
    subprocess.check_call([
        sys.executable,
        str(ROOT / 'scripts' / 'profile-report.py'),
        'record-launch',
        '--profile-dir',
        str(profile_dir),
        '--profile-name',
        'ledger',
        '--chromium-bin',
        '/usr/bin/chromium',
        '--remote-debugging-mode',
        'fixed',
        '--remote-debugging-port',
        '9666',
        '--arg',
        'chrome://extensions/',
    ], env=env)
    (profile_dir / 'DevToolsActivePort').write_text('9666\n/devtools/browser/one\n', encoding='utf-8')

    first_dir = tmp_path / 'capture-one'
    first = json.loads(subprocess.check_output([
        str(ROOT / 'scripts' / 'glasstty-profile.sh'),
        'capture',
        'ledger',
        '--output-dir',
        str(first_dir),
    ], env=env, text=True))
    history_path = profile_dir / 'glasstty-profile-captures.json'
    history = json.loads(history_path.read_text(encoding='utf-8'))
    assert history['capture_count'] == 1
    assert first['comparison_to_previous_capture']['has_previous_capture'] is False

    (profile_dir / 'DevToolsActivePort').write_text('9777\n/devtools/browser/two\n', encoding='utf-8')
    write_mv3_resume_artifacts(profile_dir, {
        'ok': True,
        'phase': 'completed',
        'output_path': str(tmp_path / 'resume-ledger.json'),
        'resume_proof': {
            'proof_grade': 'strict_context_recovery',
            'boot_changed': True,
            'boot_count_increased': True,
            'native_recovered': True,
            'context_evidence_available': True,
        },
    })

    second_dir = tmp_path / 'capture-two'
    second = json.loads(subprocess.check_output([
        str(ROOT / 'scripts' / 'glasstty-profile.sh'),
        'capture',
        'ledger',
        '--output-dir',
        str(second_dir),
    ], env=env, text=True))
    history = json.loads(history_path.read_text(encoding='utf-8'))
    diff = json.loads((second_dir / 'capture-diff.json').read_text(encoding='utf-8'))
    assert history['capture_count'] == 2
    assert second['capture_history']['capture_count_after_write'] == 2
    assert second['comparison_to_previous_capture']['has_previous_capture'] is True
    assert diff['cdp_endpoint_changed'] is True
    assert diff['resume_proof_grade_changed'] is True
    assert 'cdp_endpoint' in diff['changed_fields']
    assert history['entries'][-1]['output_dir'] == str(second_dir)


def test_profile_info_reports_capture_history_summary_and_command(tmp_path: Path) -> None:
    glasstty_home = tmp_path / 'glasstty-home'
    env = dict(os.environ)
    env['GLASSTTY_HOME'] = str(glasstty_home)
    profile_dir = glasstty_home / 'profiles' / 'history'
    subprocess.check_call([
        sys.executable,
        str(ROOT / 'scripts' / 'profile-report.py'),
        'record-launch',
        '--profile-dir',
        str(profile_dir),
        '--profile-name',
        'history',
        '--chromium-bin',
        '/usr/bin/chromium',
        '--arg',
        'chrome://extensions/',
    ], env=env)

    subprocess.check_call([
        str(ROOT / 'scripts' / 'glasstty-profile.sh'),
        'capture',
        'history',
        '--output-dir',
        str(tmp_path / 'capture-history'),
    ], env=env)

    info = json.loads(subprocess.check_output([str(ROOT / 'scripts' / 'glasstty-profile.sh'), 'info', 'history', '--pretty'], env=env, text=True))
    captures = json.loads(subprocess.check_output([str(ROOT / 'scripts' / 'glasstty-profile.sh'), 'captures', 'history', '--pretty'], env=env, text=True))
    assert info['capture_history_exists'] is True
    assert info['capture_history']['capture_count'] == 1
    assert info['commands']['captures'] == './scripts/glasstty-profile.sh captures history --pretty'
    assert captures['capture_count'] == 1
    assert captures['latest_capture']['profile_name'] == 'history'


def test_profile_triage_prefers_attach_ready_profile(tmp_path: Path) -> None:
    glasstty_home = tmp_path / 'glasstty-home'
    env = dict(os.environ)
    env['GLASSTTY_HOME'] = str(glasstty_home)

    attach_dir = glasstty_home / 'profiles' / 'attach'
    reopen_dir = glasstty_home / 'profiles' / 'reopen'

    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind(('127.0.0.1', 0))
    listener.listen(1)
    port = listener.getsockname()[1]
    try:
        subprocess.check_call([
            sys.executable, str(ROOT / 'scripts' / 'profile-report.py'), 'record-launch', '--profile-dir', str(attach_dir), '--profile-name', 'attach', '--chromium-bin', '/usr/bin/chromium', '--remote-debugging-mode', 'fixed', '--remote-debugging-port', str(port), '--arg', 'chrome://extensions/',
        ], env=env)
        (attach_dir / 'DevToolsActivePort').write_text(f'{port}\n/devtools/browser/attach\n', encoding='utf-8')
        write_mv3_resume_artifacts(attach_dir, {'ok': True, 'phase': 'completed', 'output_path': str(tmp_path / 'resume-attach.json'), 'resume_proof': {'proof_grade': 'strict_context_recovery', 'boot_changed': True, 'boot_count_increased': True, 'native_recovered': True, 'context_evidence_available': True}})
        subprocess.check_call([
            sys.executable, str(ROOT / 'scripts' / 'profile-report.py'), 'record-launch', '--profile-dir', str(reopen_dir), '--profile-name', 'reopen', '--chromium-bin', '/usr/bin/chromium', '--arg', 'chrome://extensions/',
        ], env=env)
        triage = json.loads(subprocess.check_output([str(ROOT / 'scripts' / 'glasstty-profile.sh'), 'triage', '--pretty'], env=env, text=True))
    finally:
        listener.close()

    assert triage['best_profile']['name'] == 'attach'
    assert triage['best_profile']['tier'] == 'attach-ready'
    assert triage['best_profile']['next_command'] == './scripts/glasstty-profile.sh resume-proof attach --output validation/latest/mv3-worker-resume-attach.json --timeout 25'
    assert triage['ranked_profiles'][0]['score'] > triage['ranked_profiles'][1]['score']


def test_profile_triage_prefers_portable_reopen_when_saved_browser_is_missing(tmp_path: Path) -> None:
    glasstty_home = tmp_path / 'glasstty-home'
    env = dict(os.environ)
    env['GLASSTTY_HOME'] = str(glasstty_home)
    env['PATH'] = f"{tmp_path}:{os.environ.get('PATH', '')}"

    discovered_browser = tmp_path / 'chromium'
    discovered_browser.write_text('', encoding='utf-8')
    discovered_browser.chmod(discovered_browser.stat().st_mode | stat.S_IXUSR)

    profile_dir = glasstty_home / 'profiles' / 'portable'
    subprocess.check_call([
        sys.executable, str(ROOT / 'scripts' / 'profile-report.py'), 'record-launch', '--profile-dir', str(profile_dir), '--profile-name', 'portable', '--chromium-bin', str(tmp_path / 'missing-browser'), '--arg', 'chrome://extensions/',
    ], env=env)

    triage = json.loads(subprocess.check_output([str(ROOT / 'scripts' / 'glasstty-profile.sh'), 'triage', '--pretty'], env=env, text=True))
    best = triage['best_profile']
    assert best['name'] == 'portable'
    assert best['tier'] == 'portable-reopen'
    assert best['portable_reopen_launchable'] is True
    assert best['used_discovered_browser_fallback'] is True
    assert '--allow-discovered-browser-fallback --remote-debugging-port auto' in best['next_command']


def test_doctor_reports_profile_triage_recommendation(tmp_path: Path) -> None:
    glasstty_home = tmp_path / 'glasstty-home'
    env = dict(os.environ)
    env['GLASSTTY_HOME'] = str(glasstty_home)
    profile_dir = glasstty_home / 'profiles' / 'lab'

    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind(('127.0.0.1', 0))
    listener.listen(1)
    port = listener.getsockname()[1]
    try:
        subprocess.check_call([
            sys.executable, str(ROOT / 'scripts' / 'profile-report.py'), 'record-launch', '--profile-dir', str(profile_dir), '--profile-name', 'lab', '--chromium-bin', '/usr/bin/chromium', '--remote-debugging-mode', 'fixed', '--remote-debugging-port', str(port), '--arg', 'chrome://extensions/',
        ], env=env)
        (profile_dir / 'DevToolsActivePort').write_text(f'{port}\n/devtools/browser/lab\n', encoding='utf-8')
        data = json.loads(subprocess.check_output([sys.executable, str(ROOT / 'scripts' / 'doctor.py')], text=True, env=env))
    finally:
        listener.close()

    best = data['profiles']['triage']['best_profile']
    assert best['name'] == 'lab'
    assert best['tier'] == 'attach-ready'
    assert any("Managed profile triage currently prefers 'lab'" in hint and './scripts/glasstty-profile.sh resume-proof lab' in hint for hint in data['hints'])


def test_fleet_capture_writes_bundle_and_history_diff(tmp_path: Path) -> None:
    glasstty_home = tmp_path / 'glasstty-home'
    env = dict(os.environ)
    env['GLASSTTY_HOME'] = str(glasstty_home)

    alpha_dir = glasstty_home / 'profiles' / 'alpha'
    subprocess.check_call([
        sys.executable, str(ROOT / 'scripts' / 'profile-report.py'), 'record-launch',
        '--profile-dir', str(alpha_dir), '--profile-name', 'alpha', '--chromium-bin', '/usr/bin/chromium', '--arg', 'chrome://extensions/',
    ], env=env)

    first_dir = tmp_path / 'fleet-one'
    subprocess.check_call([
        str(ROOT / 'scripts' / 'glasstty-profile.sh'), 'fleet-capture', '--output-dir', str(first_dir)
    ], env=env)
    first_bundle = json.loads((first_dir / 'bundle-summary.json').read_text(encoding='utf-8'))
    assert (first_dir / 'fleet-triage.json').exists()
    assert (first_dir / 'profiles.json').exists()
    assert (first_dir / 'fleet-history.json').exists()
    assert (first_dir / 'fleet-diff.json').exists()
    assert first_bundle['fleet_capture_history']['capture_count_after_write'] == 1
    assert first_bundle['comparison_to_previous_capture']['has_previous_capture'] is False

    beta_dir = glasstty_home / 'profiles' / 'beta'
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind(('127.0.0.1', 0))
    listener.listen(1)
    port = listener.getsockname()[1]
    try:
        subprocess.check_call([
            sys.executable, str(ROOT / 'scripts' / 'profile-report.py'), 'record-launch',
            '--profile-dir', str(beta_dir), '--profile-name', 'beta', '--chromium-bin', '/usr/bin/chromium',
            '--remote-debugging-mode', 'fixed', '--remote-debugging-port', str(port), '--arg', 'chrome://extensions/',
        ], env=env)
        (beta_dir / 'DevToolsActivePort').write_text(f'{port}\n/devtools/browser/beta\n', encoding='utf-8')
        second_dir = tmp_path / 'fleet-two'
        subprocess.check_call([
            str(ROOT / 'scripts' / 'glasstty-profile.sh'), 'fleet-capture', '--output-dir', str(second_dir)
        ], env=env)
    finally:
        listener.close()

    second_bundle = json.loads((second_dir / 'bundle-summary.json').read_text(encoding='utf-8'))
    diff = json.loads((second_dir / 'fleet-diff.json').read_text(encoding='utf-8'))
    history = json.loads(subprocess.check_output([
        str(ROOT / 'scripts' / 'glasstty-profile.sh'), 'fleet-captures', '--pretty'
    ], env=env, text=True))
    summary_md = (second_dir / 'SUMMARY.md').read_text(encoding='utf-8')

    assert second_bundle['fleet_capture_history']['capture_count_after_write'] == 2
    assert diff['has_previous_capture'] is True
    assert diff['best_profile_name_changed'] is True
    assert diff['added_profiles'] == ['beta']
    assert history['capture_count'] == 2
    assert history['latest_capture']['best_profile_name'] == 'beta'
    assert './scripts/glasstty-profile.sh fleet-capture --output-dir validation/latest/profile-fleet-capture' in summary_md
    assert './scripts/glasstty-profile.sh fleet-captures --pretty' in summary_md



def test_doctor_reports_existing_fleet_capture_ledger(tmp_path: Path) -> None:
    glasstty_home = tmp_path / 'glasstty-home'
    env = dict(os.environ)
    env['GLASSTTY_HOME'] = str(glasstty_home)
    profile_dir = glasstty_home / 'profiles' / 'lab'

    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind(('127.0.0.1', 0))
    listener.listen(1)
    port = listener.getsockname()[1]
    try:
        subprocess.check_call([
            sys.executable, str(ROOT / 'scripts' / 'profile-report.py'), 'record-launch',
            '--profile-dir', str(profile_dir), '--profile-name', 'lab', '--chromium-bin', '/usr/bin/chromium',
            '--remote-debugging-mode', 'fixed', '--remote-debugging-port', str(port), '--arg', 'chrome://extensions/',
        ], env=env)
        (profile_dir / 'DevToolsActivePort').write_text(f'{port}\n/devtools/browser/lab\n', encoding='utf-8')
        subprocess.check_call([
            str(ROOT / 'scripts' / 'glasstty-profile.sh'), 'fleet-capture', '--output-dir', str(tmp_path / 'fleet-history')
        ], env=env)
        data = json.loads(subprocess.check_output([sys.executable, str(ROOT / 'scripts' / 'doctor.py')], text=True, env=env))
    finally:
        listener.close()

    assert data['profiles']['fleet_capture_history']['capture_count'] == 1
    assert any('fleet-level managed-profile snapshot ledger already exists' in hint and './scripts/glasstty-profile.sh fleet-captures --pretty' in hint for hint in data['hints'])
