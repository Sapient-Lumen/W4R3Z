from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
import zipfile
from pathlib import Path

from glassttyd.cli import fixture_path_from_response, build_parser

ROOT = Path(__file__).resolve().parents[1]


def _make_fake_playwright_module(base: Path) -> Path:
    pkg = base / 'playwright'
    driver_pkg = pkg / 'driver' / 'package'
    driver_pkg.mkdir(parents=True, exist_ok=True)
    (pkg / '__init__.py').write_text('__all__ = []\n', encoding='utf-8')
    (driver_pkg / 'package.json').write_text(json.dumps({'name': 'playwright-test-driver', 'version': '1.53.0'}) + '\n', encoding='utf-8')
    (driver_pkg / 'browsers.json').write_text(json.dumps({
        'comment': 'test package',
        'browsers': [
            {'name': 'chromium', 'revision': '1208', 'browserVersion': '145.0.7632.6', 'installByDefault': True, 'title': 'Chrome for Testing'},
            {'name': 'chromium-headless-shell', 'revision': '1208', 'browserVersion': '145.0.7632.6', 'installByDefault': False, 'title': 'Chrome Headless Shell'},
        ],
    }, indent=2) + '\n', encoding='utf-8')
    (pkg / '__main__.py').write_text('import os, sys\nfrom pathlib import Path\n\nROOT = Path(os.environ.get("PLAYWRIGHT_BROWSERS_PATH", str(Path.home() / ".cache" / "ms-playwright"))).expanduser()\nDRIVER = Path(__file__).resolve().parent / "driver" / "package"\n\nif sys.argv[1:4] == ["install", "--dry-run", "chromium"]:\n    print("Chrome for Testing 145.0.7632.6 (playwright chromium v1208)")\n    print(f"  Install location:    {ROOT / \'chromium-1208\'}")\n    print("  Download url:        https://cdn.playwright.dev/chrome-for-testing-public/145.0.7632.6/linux64/chrome-linux64.zip")\n    raise SystemExit(0)\n\nif sys.argv[1:3] == ["install", "--list"]:\n    print("Playwright version: 1.53.0")\n    print("  Browsers:")\n    if ROOT.exists():\n        for item in sorted(ROOT.iterdir()):\n            if item.is_dir() and item.name.startswith(("chromium-", "chromium-cft-", "chromium_headless_shell-")):\n                print(f"    {item}")\n    print("  References:")\n    print(f"    {DRIVER}")\n    raise SystemExit(0)\n\nraise SystemExit(2)\n', encoding='utf-8')
    return base


def _write_saved_resume_summary(profile_dir: Path, *, proof_grade: str = 'strict_context_recovery') -> None:
    (profile_dir / 'glasstty-mv3-worker-resume-summary.json').write_text(json.dumps({
        'captured_at': '2026-03-17T19:00:00Z',
        'profile': str(profile_dir),
        'report_path': str(profile_dir / 'glasstty-mv3-worker-resume.json'),
        'ok': True,
        'phase': 'completed',
        'proof_grade': proof_grade,
        'boot_changed': True,
        'boot_count_increased': True,
        'native_recovered': True,
        'context_evidence_available': True,
    }), encoding='utf-8')


def test_extension_id_script_outputs_expected_length() -> None:
    output = subprocess.check_output([sys.executable, str(ROOT / 'scripts' / 'extension-id.py'), str(ROOT / 'extension' / 'manifest.json')], text=True).strip()
    assert len(output) == 32
    assert output.isalpha() and output.islower()


def test_fixture_path_from_response_uses_adapter_and_title(tmp_path: Path) -> None:
    message = {
        'message': {
            'payload': {
                'adapter': 'claude',
                'title': 'Hello / World',
            }
        }
    }
    target = fixture_path_from_response(message, tmp_path)
    assert target.parent == tmp_path
    assert 'claude' in target.name
    assert 'hello---world' in target.name


def test_contexts_parser_accepts_wait_timeout_and_offscreen() -> None:
    parser = build_parser()
    args = parser.parse_args(['contexts', '--wait', '--timeout', '3.0', '--ensure-offscreen'])
    assert args.command == 'contexts'
    assert args.wait is True
    assert args.timeout == 3.0
    assert args.ensure_offscreen is True


def test_capture_fixture_parser_accepts_output_dir_and_timeout() -> None:
    parser = build_parser()
    args = parser.parse_args(['capture-fixture', '--output-dir', '/tmp/x', '--timeout', '2.5', '--tab-id', '7'])
    assert args.command == 'capture-fixture'
    assert args.output_dir == '/tmp/x'
    assert args.timeout == 2.5
    assert args.tab_id == 7


def test_fixture_lab_serves_page() -> None:
    with tempfile.TemporaryDirectory() as _tmp:
        proc = subprocess.Popen([sys.executable, str(ROOT / 'scripts' / 'fixture-lab.py'), '--host', '127.0.0.1', '--port', '8767'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            deadline = time.time() + 10
            while time.time() < deadline:
                try:
                    with urllib.request.urlopen('http://127.0.0.1:8767/', timeout=1) as response:
                        body = response.read().decode('utf-8')
                    assert 'GlassTTY Fixture Lab' in body
                    assert 'data-glasstty-role="prompt"' in body
                    break
                except Exception:
                    time.sleep(0.1)
            else:
                raise AssertionError('fixture lab did not start')
        finally:
            proc.terminate()
            proc.wait(timeout=5)




def test_doctor_and_native_host_report_surface_latest_overflow_summary(tmp_path: Path) -> None:
    home = tmp_path / 'glasstty-home'
    fixtures = home / 'state' / 'fixtures'
    fixtures.mkdir(parents=True, exist_ok=True)
    artifact = fixtures / 'oversized-host-outbound-bridge-offscreen-fixture-req.json'
    artifact.write_text(json.dumps({
        'kind': 'oversized-host-outbound',
        'captured_at': '2026-03-17T10:00:00Z',
        'message': {'type': 'bridge.offscreen_fixture', 'request_id': 'req-overflow', 'payload': {'blob': 'x' * 2048}},
    }), encoding='utf-8')
    (fixtures / 'oversized-host-outbound-bridge-offscreen-fixture-older.json').write_text(json.dumps({
        'kind': 'oversized-host-outbound',
        'captured_at': '2026-03-17T09:59:00Z',
        'message': {'type': 'bridge.offscreen_fixture', 'request_id': 'req-overflow-older', 'payload': {'blob': 'y' * 1024}},
    }), encoding='utf-8')
    (fixtures / 'oversized-host-outbound-bridge-offscreen-fixture-oldest.json').write_text(json.dumps({
        'kind': 'oversized-host-outbound',
        'captured_at': '2026-03-17T09:58:00Z',
        'message': {'type': 'bridge.offscreen_fixture', 'request_id': 'req-overflow-oldest', 'payload': {'blob': 'z' * 1024}},
    }), encoding='utf-8')
    (fixtures / 'oversized-host-outbound-bridge-offscreen-fixture-ancient.json').write_text(json.dumps({
        'kind': 'oversized-host-outbound',
        'captured_at': '2026-03-17T09:57:00Z',
        'message': {'type': 'bridge.offscreen_fixture', 'request_id': 'req-overflow-ancient', 'payload': {'blob': 'q' * 1024}},
    }), encoding='utf-8')
    latest = home / 'state' / 'latest' / 'oversized-host-outbound.json'
    latest.parent.mkdir(parents=True, exist_ok=True)
    latest.write_text(json.dumps({
        'artifact_path': str(artifact),
        'original_type': 'bridge.offscreen_fixture',
        'size_bytes': 1049000,
        'limit_bytes': 1048576,
        'captured_at': '2026-03-17T10:00:00Z',
    }), encoding='utf-8')
    runtime = home / 'run' / 'daemon-broker-owner.json'
    runtime.parent.mkdir(parents=True, exist_ok=True)
    runtime.write_text(json.dumps({
        'native_host': 'com.glasstty.bridge',
        'socket_path': str(home / 'run' / 'daemon.sock'),
        'lock_path': str(home / 'run' / 'daemon-broker.lock'),
        'metadata_path': str(runtime),
        'host_identity': {'pid': 4242, 'boot_id': 'boot-owner', 'started_at': '2026-03-17T10:01:00Z'},
    }), encoding='utf-8')
    env = dict(os.environ)
    env['GLASSTTY_HOME'] = str(home)

    doctor = json.loads(subprocess.check_output([sys.executable, str(ROOT / 'scripts' / 'doctor.py')], text=True, env=env))
    assert doctor['native_host']['last_oversized_host_message']['latest_exists'] is True
    assert doctor['native_host']['last_oversized_host_message']['artifact_exists'] is True
    assert any('overflow-report' in hint for hint in doctor['hints'])
    assert any('overflow-prune' in hint for hint in doctor['hints'])
    assert any('secondary host processes' in hint for hint in doctor['hints'])
    assert doctor['native_host']['last_oversized_host_message']['inventory']['artifact_count'] == 4
    assert doctor['native_host']['runtime']['owner_metadata']['host_identity']['boot_id'] == 'boot-owner'

    report = json.loads(subprocess.check_output([sys.executable, str(ROOT / 'scripts' / 'native-host-report.py')], text=True, env=env))
    assert report['last_oversized_host_message']['latest_exists'] is True
    assert report['last_oversized_host_message']['artifact_exists'] is True
    assert report['last_oversized_host_message']['inventory']['artifact_count'] == 4
    assert report['runtime']['owner_metadata']['host_identity']['pid'] == 4242



def test_doctor_hints_playwright_channel_alignment_when_cache_name_drifts(tmp_path: Path) -> None:
    archive = tmp_path / 'chrome-linux64.zip'
    with zipfile.ZipFile(archive, 'w') as zf:
        zf.writestr('chrome-linux64/chrome', '#!/bin/sh\necho chromium\n')
    cache_root = tmp_path / 'pw'
    subprocess.check_call([
        sys.executable,
        str(ROOT / 'scripts' / 'playwright-browsers.py'),
        'import-archive',
        '--archive',
        str(archive),
        '--root',
        str(cache_root),
        '--install-name',
        'chromium-cft-145.0.7632.6',
        '--version',
        '145.0.7632.6',
    ])
    fake_site = _make_fake_playwright_module(tmp_path / 'fake-site')
    env = dict(os.environ)
    env['PLAYWRIGHT_BROWSERS_PATH'] = str(cache_root)
    env['PYTHONPATH'] = str(fake_site) + (os.pathsep + env['PYTHONPATH'] if env.get('PYTHONPATH') else '')
    doctor = json.loads(subprocess.check_output([sys.executable, str(ROOT / 'scripts' / 'doctor.py')], text=True, env=env))
    launch_plan = doctor['playwright']['extension_launch_plan']
    assert launch_plan['cache_alignment_status'] == 'cache-install-name-drift'
    assert 'ensure-channel-ready' in (launch_plan['recommended_channel_ready_command'] or '')
    assert any('ensure-channel-ready' in hint for hint in doctor['hints'])

def test_doctor_script_reports_manifest_and_wrapper() -> None:
    output = subprocess.check_output([sys.executable, str(ROOT / 'scripts' / 'doctor.py')], text=True)
    data = json.loads(output)
    assert data['project'] == 'GlassTTY'
    assert data['manifest']['has_key'] is True
    assert data['native_host']['wrapper']['exists'] is True
    assert 'playwright' in data
    assert isinstance(data['playwright']['available'], bool)
    assert 'repair_plan' in data['playwright']
    assert 'chrome_for_testing' in data
    assert isinstance(data['chrome_for_testing']['platform'], str)
    assert isinstance(data['hints'], list)
    assert isinstance(data['native_host']['recommended_targets'], list)
    assert isinstance(data['native_host']['suggested_install_commands'], list)
    assert isinstance(data['native_host']['targets'], dict)
    assert 'chromium' in data['native_host']['targets']
    assert 'manifest_parse_ok' in data['native_host']['targets']['chromium']



def test_doctor_surfaces_attach_ready_profile_and_saved_resume_evidence(tmp_path: Path) -> None:
    home = tmp_path / 'glasstty-home'
    profile_dir = home / 'profiles' / 'lab'
    env = dict(os.environ)
    env['GLASSTTY_HOME'] = str(home)
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind(('127.0.0.1', 0))
    listener.listen(1)
    port = listener.getsockname()[1]
    try:
        subprocess.check_call([sys.executable, str(ROOT / 'scripts' / 'profile-report.py'), 'record-launch', '--profile-dir', str(profile_dir), '--profile-name', 'lab', '--chromium-bin', '/usr/bin/chromium', '--remote-debugging-mode', 'fixed', '--remote-debugging-port', str(port)], env=env)
        (profile_dir / 'DevToolsActivePort').write_text(f'{port}\n/devtools/browser/lab\n', encoding='utf-8')
        _write_saved_resume_summary(profile_dir)
        doctor = json.loads(subprocess.check_output([sys.executable, str(ROOT / 'scripts' / 'doctor.py')], text=True, env=env))
    finally:
        listener.close()
    assert any('attach-ready for MV3 restart proof' in hint for hint in doctor['hints'])
    assert any('resume-proof lab' in hint for hint in doctor['hints'])
    assert any('capture lab --output-dir validation/latest/profile-capture-lab' in hint for hint in doctor['hints'])
    assert any('strict_context_recovery' in hint for hint in doctor['hints'])



def test_doctor_stale_profile_hint_recommends_reopen_debug(tmp_path: Path) -> None:
    home = tmp_path / 'glasstty-home'
    profile_dir = home / 'profiles' / 'stale'
    env = dict(os.environ)
    env['GLASSTTY_HOME'] = str(home)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('127.0.0.1', 0))
    port = sock.getsockname()[1]
    sock.close()
    subprocess.check_call([sys.executable, str(ROOT / 'scripts' / 'profile-report.py'), 'record-launch', '--profile-dir', str(profile_dir), '--profile-name', 'stale', '--chromium-bin', '/usr/bin/chromium', '--remote-debugging-mode', 'fixed', '--remote-debugging-port', str(port), '--arg', 'chrome://extensions/'], env=env)
    (profile_dir / 'DevToolsActivePort').write_text(f'{port}\n/devtools/browser/stale\n', encoding='utf-8')
    doctor = json.loads(subprocess.check_output([sys.executable, str(ROOT / 'scripts' / 'doctor.py')], text=True, env=env))
    assert any('Replay that profile with' in hint for hint in doctor['hints'])
    assert any('reopen_debug' not in hint and 'launch-chromium-profile.sh stale --skip-extension --remote-debugging-port auto chrome://extensions/' in hint for hint in doctor['hints'])


def test_fixture_lab_manifest_lists_pages() -> None:
    with tempfile.TemporaryDirectory() as _tmp:
        proc = subprocess.Popen([sys.executable, str(ROOT / 'scripts' / 'fixture-lab.py'), '--host', '127.0.0.1', '--port', '8768'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            deadline = time.time() + 10
            while time.time() < deadline:
                try:
                    with urllib.request.urlopen('http://127.0.0.1:8768/manifest.json', timeout=1) as response:
                        body = json.loads(response.read().decode('utf-8'))
                    assert '/' in body['pages']
                    assert '/thread' in body['pages']
                    break
                except Exception:
                    time.sleep(0.1)
            else:
                raise AssertionError('fixture lab manifest did not start')
        finally:
            proc.terminate()
            proc.wait(timeout=5)


def test_index_fixtures_script_summarizes_saved_fixture(tmp_path: Path) -> None:
    fixture = tmp_path / 'sample.json'
    fixture.write_text(json.dumps({'message': {'payload': {'adapter': 'claude', 'title': 'Sample Thread', 'url': 'https://claude.ai/chat/abc', 'prompt': 'hello', 'latest_output': 'world', 'selection': '', 'candidates': {'inputs': [{'selector_hint': 'textarea', 'label_text': 'Message', 'description_text': 'Type your prompt', 'fieldset_legend': 'Composer'}], 'outputs': [{'selector_hint': 'article'}]}, 'metadata': {'top_submit_label': 'Send', 'top_submit_action': 'https://claude.ai/submit', 'semantic_outline': {'form_actions': ['https://claude.ai/submit'], 'prompt_descriptions': ['Type your prompt'], 'fieldset_legends': ['Composer'], 'control_kinds': ['textbox'], 'link_hosts': ['claude.ai']}}}}}), encoding='utf-8')
    output = subprocess.check_output([sys.executable, str(ROOT / 'scripts' / 'index-fixtures.py'), str(tmp_path)], text=True)
    data = json.loads(output)
    assert data['count'] == 1
    assert data['by_adapter']['claude'] == 1
    assert data['fixtures'][0]['top_input_hint'] == 'textarea'
    assert data['fixtures'][0]['top_input_label'] == 'Message'
    assert data['fixtures'][0]['top_input_action'] == 'fill'
    assert data['fixtures'][0]['top_input_locator_hints'][0].endswith('.getByRole("textbox", { name: "Message" })') or data['fixtures'][0]['top_input_locator_hints'][0] == 'page.getByRole("textbox", { name: "Message" })'
    assert data['fixtures'][0]['top_input_description'] == 'Type your prompt'
    assert data['fixtures'][0]['top_fieldset_legend'] == 'Composer'
    assert data['fixtures'][0]['top_submit_label'] == 'Send'
    assert data['fixtures'][0]['top_submit_locator_hints'][0] == 'page.getByRole("button", { name: "Send" })'
    assert data['fixtures'][0]['top_submit_action'] == 'https://claude.ai/submit'
    assert data['fixtures'][0]['first_form_action'] == 'https://claude.ai/submit'
    assert data['fixtures'][0]['control_kinds'] == ['textbox']
    assert data['fixtures'][0]['native_message_status'] == 'ok'
    assert data['fixtures'][0]['native_message_payload_bytes'] > 0
    assert data['fixtures'][0]['native_message_envelope_bytes'] > data['fixtures'][0]['native_message_payload_bytes']


def test_cli_doctor_command_runs_with_pythonpath() -> None:
    env = dict(os.environ)
    env['PYTHONPATH'] = str(ROOT / 'daemon' / 'src') + (os.pathsep + env['PYTHONPATH'] if env.get('PYTHONPATH') else '')
    output = subprocess.check_output([sys.executable, '-m', 'glassttyd.cli', 'doctor'], text=True, env=env)
    data = json.loads(output)
    assert data['project'] == 'GlassTTY'


def test_index_fixtures_script_surfaces_accessible_names_and_choice_topology(tmp_path: Path) -> None:
    fixture = tmp_path / 'select-sample.json'
    fixture.write_text(json.dumps({'message': {'payload': {'adapter': 'offscreen-html', 'title': 'Settings', 'url': 'https://example.test/settings', 'prompt': '', 'latest_output': '', 'selection': '', 'candidates': {'inputs': [{'selector_hint': 'select#tone', 'label_text': 'Tone', 'accessible_name': 'Preferred tone', 'description_text': 'Choose one', 'form_name': 'Preferences', 'option_count': 3, 'option_labels': ['Friendly', 'Neutral', 'Formal'], 'selected_options': ['Neutral'], 'control_kind': 'combobox'}], 'outputs': []}, 'metadata': {'top_submit_label': 'Save settings', 'top_submit_action': 'https://example.test/settings/save', 'semantic_outline': {'accessible_names': ['Preferred tone'], 'form_names': ['Preferences'], 'option_labels': ['Friendly', 'Neutral', 'Formal'], 'form_actions': ['https://example.test/settings/save'], 'control_kinds': ['combobox'], 'link_hosts': ['example.test']}}}}}), encoding='utf-8')
    output = subprocess.check_output([sys.executable, str(ROOT / 'scripts' / 'index-fixtures.py'), str(tmp_path)], text=True)
    data = json.loads(output)
    assert data['fixtures'][0]['top_input_accessible_name'] == 'Preferred tone'
    assert data['fixtures'][0]['top_input_action'] == 'select_option'
    assert data['fixtures'][0]['top_input_locator_hints'][0] == 'page.getByRole("combobox", { name: "Preferred tone" })'
    assert data['fixtures'][0]['top_form_name'] == 'Preferences'
    assert data['fixtures'][0]['top_option_count'] == 3
    assert data['fixtures'][0]['top_selected_option'] == 'Neutral'
    assert data['fixtures'][0]['option_labels'] == ['Friendly', 'Neutral', 'Formal']


def test_index_fixtures_script_surfaces_control_state_and_constraints(tmp_path: Path) -> None:
    fixture = tmp_path / 'stateful-sample.json'
    fixture.write_text(json.dumps({'message': {'payload': {'adapter': 'offscreen-html', 'title': 'Signup', 'url': 'https://example.test/signup', 'prompt': '', 'latest_output': '', 'selection': '', 'candidates': {'inputs': [{'selector_hint': 'input[type="email"][name="email"]', 'label_text': 'Email address', 'accessible_name': 'Work email', 'choice_group': 'account', 'autocomplete': 'section-user1 email', 'input_mode': 'email', 'constraint_hints': ['pattern:.+@example\\.com', 'maxlength:80'], 'constraint_flags': ['typeMismatch'], 'required': True, 'invalid': True, 'checked_state': 'unchecked', 'disabled': False, 'readonly': False, 'multiple': False, 'selected_count': 0, 'control_kind': 'input:email'}], 'outputs': []}, 'metadata': {'top_submit_label': 'Create account', 'top_submit_action': 'https://example.test/signup/create', 'semantic_outline': {'accessible_names': ['Work email'], 'form_names': ['Signup'], 'control_kinds': ['input:email'], 'choice_groups': ['account'], 'autocomplete_tokens': ['section-user1 email'], 'state_flags': ['required', 'invalid', 'checked:unchecked'], 'constraint_hints': ['pattern:.+@example\\.com', 'maxlength:80'], 'link_hosts': ['example.test']}}}}}), encoding='utf-8')
    output = subprocess.check_output([sys.executable, str(ROOT / 'scripts' / 'index-fixtures.py'), str(tmp_path)], text=True)
    data = json.loads(output)
    item = data['fixtures'][0]
    assert item['top_choice_group'] == 'account'
    assert item['top_input_action'] == 'fill'
    assert item['top_input_locator_hints'][0] == 'page.getByRole("textbox", { name: "Work email" })'
    assert item['top_autocomplete'] == 'section-user1 email'
    assert item['top_input_mode'] == 'email'
    assert item['top_checked_state'] == 'unchecked'
    assert item['top_constraint_flags'] == ['typeMismatch']
    assert item['constraint_hints'] == ['pattern:.+@example\\.com', 'maxlength:80']
    assert item['state_flags'] == ['required', 'invalid', 'checked:unchecked']


def test_native_message_budget_script_reports_fixture_envelope(tmp_path: Path) -> None:
    fixture = tmp_path / 'sample.json'
    fixture.write_text(json.dumps({'message': {'payload': {'adapter': 'claude', 'title': 'Budget Sample', 'url': 'https://claude.ai/chat/abc', 'prompt': 'hello', 'latest_output': 'world', 'selection': '', 'candidates': {'inputs': [{'selector_hint': 'textarea'}], 'outputs': [{'selector_hint': 'article'}]}}}}), encoding='utf-8')
    output = subprocess.check_output([sys.executable, str(ROOT / 'scripts' / 'native-message-budget.py'), str(fixture)], text=True)
    data = json.loads(output)
    assert data['count'] == 1
    report = data['reports'][0]
    assert report['fixture_payload']['host_to_extension']['fits'] is True
    assert report['fixture_payload']['envelope_bytes'] > report['fixture_payload']['payload_bytes']


def test_fixture_lab_manifest_lists_scoped_pages() -> None:
    with tempfile.TemporaryDirectory() as _tmp:
        proc = subprocess.Popen([sys.executable, str(ROOT / 'scripts' / 'fixture-lab.py'), '--host', '127.0.0.1', '--port', '8769'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            deadline = time.time() + 10
            while time.time() < deadline:
                try:
                    with urllib.request.urlopen('http://127.0.0.1:8769/manifest.json', timeout=1) as response:
                        body = json.loads(response.read().decode('utf-8'))
                    assert '/dialog-form' in body['pages']
                    assert '/iframe-shell' in body['pages']
                    assert '/iframe-compose' in body['pages']
                    assert '/iframe-split-shell' in body['pages']
                    assert '/iframe-split-compose' in body['pages']
                    assert '/iframe-nested-middle' in body['pages']
                    assert '/iframe-nested-shell' in body['pages']
                    assert '/iframe-partial-shell' in body['pages']
                    assert '/iframe-partial-compose' in body['pages']
                    break
                except Exception:
                    time.sleep(0.1)
            else:
                raise AssertionError('fixture lab manifest did not expose scoped pages')
        finally:
            proc.terminate()
            proc.wait(timeout=5)



def test_fixture_lab_serves_iframe_shell_page() -> None:
    with tempfile.TemporaryDirectory() as _tmp:
        proc = subprocess.Popen([sys.executable, str(ROOT / 'scripts' / 'fixture-lab.py'), '--host', '127.0.0.1', '--port', '8770'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            deadline = time.time() + 10
            while time.time() < deadline:
                try:
                    with urllib.request.urlopen('http://127.0.0.1:8770/iframe-shell', timeout=1) as response:
                        body = response.read().decode('utf-8')
                    assert 'title="Billing details"' in body
                    assert 'name="billing-frame"' in body
                    assert 'src="/iframe-compose"' in body
                    break
                except Exception:
                    time.sleep(0.1)
            else:
                raise AssertionError('fixture lab iframe shell did not start')
        finally:
            proc.terminate()
            proc.wait(timeout=5)



def test_index_fixtures_script_surfaces_output_scope_and_split_scope(tmp_path: Path) -> None:
    fixture = tmp_path / 'iframe-split.json'
    fixture.write_text(json.dumps({'message': {'payload': {'adapter': 'fixturelab', 'title': 'Split scope fixture', 'url': 'https://example.test/iframe-split', 'prompt': 'Need billing follow-up', 'latest_output': 'Top-level billing summary is current', 'selection': '', 'candidates': {'inputs': [{'selector_hint': '[data-glasstty-role="prompt"]', 'label_text': 'Draft note', 'accessible_name': 'Draft note', 'control_kind': 'textarea', 'form_name': 'Embedded split composer', 'frame_selector': 'iframe#billing-split-frame', 'frame_name': 'billing-split-frame', 'frame_title': 'Billing draft frame', 'frame_path': 'iframe#billing-split-frame', 'frame_depth': 1, 'frame_path_selectors': ['iframe#billing-split-frame']}], 'outputs': [{'selector_hint': '[data-glasstty-role="latest-output"]', 'text_sample': 'Top-level billing summary is current', 'control_kind': 'article'}]}, 'metadata': {'top_submit_label': 'Queue follow-up', 'top_submit_action': 'https://example.test/iframe-split/save', 'top_submit_frame_path': 'iframe#billing-split-frame', 'top_output_label': 'Top-level billing summary is current', 'top_output_frame_path': None, 'top_output_frame_depth': None, 'split_scope_detected': True, 'submit_candidates': [{'selector_hint': '[data-glasstty-role="submit"]', 'accessible_name': 'Queue follow-up', 'form_name': 'Embedded split composer', 'submit_action': 'https://example.test/iframe-split/save', 'frame_selector': 'iframe#billing-split-frame', 'frame_path': 'iframe#billing-split-frame', 'frame_path_selectors': ['iframe#billing-split-frame']}], 'semantic_outline': {'form_names': ['Embedded split composer'], 'iframe_names': ['billing-split-frame'], 'iframe_titles': ['Billing draft frame'], 'frame_paths': ['iframe#billing-split-frame'], 'control_kinds': ['textarea'], 'link_hosts': ['example.test']}}}}}), encoding='utf-8')
    output = subprocess.check_output([sys.executable, str(ROOT / 'scripts' / 'index-fixtures.py'), str(tmp_path)], text=True)
    data = json.loads(output)
    item = data['fixtures'][0]
    assert str(item['top_input_locator_root_strategy']).startswith('frame_path_selectors')
    assert item['top_output_locator_root_strategy'] == 'page'
    assert item['top_output_frame_path'] is None
    assert item['split_scope_detected'] is True


def test_fixture_lab_serves_split_iframe_shell_page() -> None:
    with tempfile.TemporaryDirectory() as _tmp:
        proc = subprocess.Popen([sys.executable, str(ROOT / 'scripts' / 'fixture-lab.py'), '--host', '127.0.0.1', '--port', '8771'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            deadline = time.time() + 10
            while time.time() < deadline:
                try:
                    with urllib.request.urlopen('http://127.0.0.1:8771/iframe-split-shell', timeout=1) as response:
                        body = response.read().decode('utf-8')
                    assert 'Top-level billing summary is current' in body
                    assert 'name="billing-split-frame"' in body
                    assert 'src="/iframe-split-compose"' in body
                    break
                except Exception:
                    time.sleep(0.1)
            else:
                raise AssertionError('fixture lab iframe split shell did not start')
        finally:
            proc.terminate()
            proc.wait(timeout=5)


def test_index_fixtures_script_surfaces_dialog_and_iframe_inventory(tmp_path: Path) -> None:
    fixture = tmp_path / 'scoped.json'
    fixture.write_text(json.dumps({'message': {'payload': {'adapter': 'offscreen-html', 'title': 'Scoped fixture', 'url': 'https://example.test/scoped', 'prompt': 'hello', 'latest_output': 'saved', 'selection': '', 'candidates': {'inputs': [{'selector_hint': 'textarea#dialog-prompt', 'label_text': 'Message', 'accessible_name': 'Message', 'dialog_name': 'Profile settings', 'control_kind': 'textbox'}], 'outputs': []}, 'metadata': {'top_submit_label': 'Save', 'semantic_outline': {'dialog_names': ['Profile settings'], 'iframe_names': ['billing-frame'], 'iframe_titles': ['Billing details'], 'control_kinds': ['textbox'], 'link_hosts': ['example.test']}}}}}), encoding='utf-8')
    output = subprocess.check_output([sys.executable, str(ROOT / 'scripts' / 'index-fixtures.py'), str(tmp_path)], text=True)
    data = json.loads(output)
    item = data['fixtures'][0]
    assert item['top_dialog_name'] == 'Profile settings'
    assert item['dialog_names'] == ['Profile settings']
    assert item['iframe_names'] == ['billing-frame']
    assert item['iframe_titles'] == ['Billing details']




def test_fixture_lab_serves_partial_iframe_shell_page() -> None:
    with tempfile.TemporaryDirectory() as _tmp:
        proc = subprocess.Popen([sys.executable, str(ROOT / 'scripts' / 'fixture-lab.py'), '--host', '127.0.0.1', '--port', '8774'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            deadline = time.time() + 10
            while time.time() < deadline:
                try:
                    with urllib.request.urlopen('http://127.0.0.1:8774/iframe-partial-shell', timeout=1) as response:
                        body = response.read().decode('utf-8')
                    assert 'name="accessible-frame"' in body
                    assert 'title="Partner billing widget"' in body
                    assert 'sandbox="allow-scripts"' in body
                    break
                except Exception:
                    time.sleep(0.1)
            else:
                raise AssertionError('fixture lab partial iframe shell did not start')
        finally:
            proc.terminate()
            proc.wait(timeout=5)


def test_fixture_lab_serves_nested_iframe_shell_page() -> None:
    with tempfile.TemporaryDirectory() as _tmp:
        proc = subprocess.Popen([sys.executable, str(ROOT / 'scripts' / 'fixture-lab.py'), '--host', '127.0.0.1', '--port', '8772'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            deadline = time.time() + 10
            while time.time() < deadline:
                try:
                    with urllib.request.urlopen('http://127.0.0.1:8772/iframe-nested-shell', timeout=1) as response:
                        body = response.read().decode('utf-8')
                    assert 'title="Settings shell"' in body
                    assert 'name="settings-frame"' in body
                    assert 'src="/iframe-nested-middle"' in body
                    break
                except Exception:
                    time.sleep(0.1)
            else:
                raise AssertionError('fixture lab nested iframe shell did not start')
        finally:
            proc.terminate()
            proc.wait(timeout=5)



def test_index_fixtures_script_surfaces_partial_frame_capture_status(tmp_path: Path) -> None:
    fixture = tmp_path / 'partial-frame.json'
    fixture.write_text(json.dumps({'message': {'payload': {'adapter': 'fixturelab', 'title': 'Partial frame capture', 'url': 'https://example.test/partial', 'prompt': 'hello', 'latest_output': 'saved', 'selection': '', 'candidates': {'inputs': [{'selector_hint': 'textarea', 'label_text': 'Billing note', 'accessible_name': 'Billing note', 'frame_path': 'iframe#accessible-frame', 'frame_path_selectors': ['iframe#accessible-frame'], 'control_kind': 'textarea'}], 'outputs': [{'selector_hint': 'article', 'text_sample': 'saved', 'frame_path': 'iframe#accessible-frame', 'frame_path_selectors': ['iframe#accessible-frame'], 'control_kind': 'article'}]}, 'metadata': {'accessible_iframe_count': 1, 'blocked_iframe_count': 1, 'blocked_iframe_names': ['partner-frame'], 'blocked_iframe_titles': ['Partner billing widget'], 'blocked_frame_paths': ['iframe#partner-frame'], 'traversed_document_count': 2, 'total_iframe_count': 2, 'frame_capture_ratio': 0.5, 'frame_capture_status': 'partial', 'frame_capture_warning': 'frame capture is partial: 1/2 iframes were accessible and 1 were blocked', 'semantic_outline': {'iframe_names': ['accessible-frame', 'partner-frame'], 'iframe_titles': ['Accessible billing frame', 'Partner billing widget'], 'frame_paths': ['iframe#accessible-frame'], 'control_kinds': ['textarea'], 'link_hosts': ['example.test']}}}}}), encoding='utf-8')
    output = subprocess.check_output([sys.executable, str(ROOT / 'scripts' / 'index-fixtures.py'), str(tmp_path)], text=True)
    data = json.loads(output)
    item = data['fixtures'][0]
    assert item['frame_capture_status'] == 'partial'
    assert item['frame_capture_ratio'] == 0.5
    assert item['blocked_iframe_titles'] == ['Partner billing widget']
    assert item['blocked_frame_paths'] == ['iframe#partner-frame']
    assert '1/2 iframes' in item['frame_capture_warning']


def test_index_fixtures_script_surfaces_frame_paths_and_iframe_depth(tmp_path: Path) -> None:
    fixture = tmp_path / 'nested-frame.json'
    fixture.write_text(json.dumps({'message': {'payload': {'adapter': 'fixturelab', 'title': 'Nested frame', 'url': 'https://example.test/nested', 'prompt': '5555', 'latest_output': 'saved', 'selection': '', 'candidates': {'inputs': [{'selector_hint': 'input#card', 'label_text': 'Card number', 'accessible_name': 'Card number', 'form_name': 'Nested billing details', 'frame_path': 'iframe#settings-frame >> iframe#card-frame', 'frame_depth': 2, 'frame_path_selectors': ['iframe#settings-frame', 'iframe#card-frame'], 'control_kind': 'input:text'}], 'outputs': []}, 'metadata': {'accessible_iframe_count': 2, 'blocked_iframe_count': 0, 'traversed_document_count': 3, 'max_frame_depth': 2, 'top_submit_label': 'Save nested card', 'top_submit_frame_path': 'iframe#settings-frame >> iframe#card-frame', 'submit_candidates': [{'selector_hint': 'button[type="submit"]', 'accessible_name': 'Save nested card', 'form_name': 'Nested billing details', 'frame_path': 'iframe#settings-frame >> iframe#card-frame', 'frame_path_selectors': ['iframe#settings-frame', 'iframe#card-frame']}], 'semantic_outline': {'frame_paths': ['iframe#settings-frame', 'iframe#settings-frame >> iframe#card-frame'], 'iframe_names': ['settings-frame', 'card-frame'], 'iframe_titles': ['Settings shell', 'Card editor frame'], 'form_names': ['Nested billing details'], 'control_kinds': ['input:text'], 'link_hosts': ['example.test']}}}}}), encoding='utf-8')
    output = subprocess.check_output([sys.executable, str(ROOT / 'scripts' / 'index-fixtures.py'), str(tmp_path)], text=True)
    data = json.loads(output)
    item = data['fixtures'][0]
    assert item['top_input_frame_path'] == 'iframe#settings-frame >> iframe#card-frame'
    assert item['top_input_frame_depth'] == 2
    assert item['frame_paths'] == ['iframe#settings-frame', 'iframe#settings-frame >> iframe#card-frame']
    assert item['accessible_iframe_count'] == 2
    assert item['max_frame_depth'] == 2
    assert item['top_submit_locator_root_strategy'] == 'frame_path_selectors+form_name'
