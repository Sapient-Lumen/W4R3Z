from __future__ import annotations

import json
from argparse import Namespace
from pathlib import Path

from glassttyd.cli import build_parser, cmd_doctor
from glassttyd.cli import (
    _first_flight_baseline_blocker,
    _first_flight_ok,
    _unknown_composer_controls_by_phase,
    cmd_first_flight,
)
from glassttyd.mock_tab import MockChatGPTTab, MockReply


def test_cli_has_surface_contract_commands_and_no_deleted_fixture_shims() -> None:
    choices = build_parser()._subparsers._group_actions[0].choices

    assert 'surface-audit' in choices
    assert 'surface-contract-build' in choices
    assert 'surface-contract-check' in choices
    assert 'proof-rehearse' in choices
    assert 'proof-preflight' in choices
    assert 'proof-export-pack' in choices
    assert 'proof-check-pack' in choices
    assert 'proof-finalize-pack' in choices
    assert 'proof-ingest' in choices
    assert 'proof-privacy-review' in choices
    assert 'proof-publish-bundle' in choices
    assert 'proof-publish-verify' in choices
    assert 'proof-status' in choices
    assert 'doctor' in choices
    assert 'seed-fixture-corpus' not in choices
    assert 'plan-fixture' not in choices
    assert 'native-message-budget' not in choices


def test_cli_doctor_reports_chatgpt_only_contract(capsys) -> None:
    status = cmd_doctor(Namespace(pretty=False))
    output = capsys.readouterr().out

    assert status == 0
    assert '"chatgpt_only": true' in output
    assert '"strict_send_selector": "#composer-submit-button"' in output


def test_first_flight_unions_unknown_controls_across_idle_and_drafted_phases() -> None:
    voice = {
        'key': 'aria:start voice',
        'selector_hint': 'button [aria-label*="Start Voice"]',
        'aria_label': 'Start Voice',
        'classification': 'unknown',
        'visible': True,
        'region': 'composer',
    }
    idle = {'controls': {'voice': voice}}
    drafted = {'controls': {}}

    unknowns = _unknown_composer_controls_by_phase([('idle', idle), ('drafted', drafted)])

    assert len(unknowns) == 1
    assert unknowns[0]['key'] == 'aria:start voice'
    assert unknowns[0]['observed_in'] == ['idle']


def test_first_flight_exit_status_requires_clean_steps_and_no_unknowns() -> None:
    clean = {'steps': [{'step': 'bridge reachable', 'ok': True}]}
    failed = {'steps': [{'step': 'composer fully classified', 'ok': False}]}

    assert _first_flight_ok(clean, [])
    assert not _first_flight_ok(clean, ['unclassified control'])
    assert not _first_flight_ok(failed, [])


def test_first_flight_keeps_draft_health_separate_from_anonymous_attachment_loss() -> None:
    snapshot = {
        'capabilities': {'submit_prompt': True, 'attach_files': False},
        'authentication': {'posture': 'anonymous'},
    }

    blocker = _first_flight_baseline_blocker(snapshot, {'verdict': 'surface-drift-degraded'})

    assert snapshot['capabilities']['submit_prompt'] is True
    assert blocker == 'not promoted while ChatGPT is logged out; attachment capability is unavailable'


def test_first_flight_promotes_only_a_complete_healthy_surface() -> None:
    snapshot = {
        'capabilities': {'submit_prompt': True, 'attach_files': True},
        'authentication': {'posture': 'authenticated'},
    }

    assert _first_flight_baseline_blocker(snapshot, {'verdict': 'surface-ok'}) is None
    assert _first_flight_baseline_blocker(snapshot, {'verdict': 'surface-drift-critical'}) == (
        'verdict=surface-drift-critical is not healthy enough to become a baseline'
    )

    unknown = {**snapshot, 'authentication': {'posture': 'unknown'}}
    assert _first_flight_baseline_blocker(unknown, {'verdict': 'surface-ok'}) == (
        'not promoted because ChatGPT authentication could not be verified'
    )


def _first_flight_args(tmp_path: Path, sock: Path, probe: Path | None = None):
    argv = [
        'first-flight', '--socket', str(sock), '--store', str(tmp_path / 'surface'),
        '--out', str(tmp_path / 'flight.json'), '--poll-interval', '0.01',
        '--start-grace', '0.2', '--max-wait', '2', '--settle-polls', '1',
        '--chip-wait', '0.01',
    ]
    if probe is not None:
        argv.extend(['--learn-attachment', str(probe)])
    return build_parser().parse_args(argv)


def test_first_flight_proves_attachment_cleanup_before_exact_canary(tmp_path: Path, capsys) -> None:
    sock = tmp_path / 'daemon.sock'
    probe = tmp_path / 'probe.txt'
    probe.write_text('first-flight probe\n', encoding='utf-8')
    args = _first_flight_args(tmp_path, sock, probe)
    args.canary = True

    def exact_canary(_prompt: str, _turn_index: int) -> MockReply:
        return MockReply(parts=['GLASSTTY-FIRST-FLIGHT-OK'])

    with MockChatGPTTab(sock, responder=exact_canary) as tab:
        status = cmd_first_flight(args)

    report = json.loads((tmp_path / 'flight.json').read_text(encoding='utf-8'))
    capsys.readouterr()
    assert status == 0
    assert report['attachment_cleanup']['ok'] is True
    assert report['canary_exact_match'] is True
    assert tab.attached == []
    assert [turn['role'] for turn in tab.transcript] == ['user']


def test_first_flight_blocks_canary_when_attachment_cleanup_is_uncertain(tmp_path: Path, capsys) -> None:
    sock = tmp_path / 'daemon.sock'
    probe = tmp_path / 'probe.txt'
    probe.write_text('first-flight probe\n', encoding='utf-8')
    args = _first_flight_args(tmp_path, sock, probe)
    args.canary = True

    with MockChatGPTTab(sock, drift='sticky-attachment-chip') as tab:
        status = cmd_first_flight(args)

    report = json.loads((tmp_path / 'flight.json').read_text(encoding='utf-8'))
    capsys.readouterr()
    assert status == 1
    assert report['attachment_cleanup']['ok'] is False
    assert report['canary']['blocked'] == 'attachment cleanup was not verified'
    assert tab.transcript == []


def test_first_flight_rejects_a_substring_only_canary_reply(tmp_path: Path, capsys) -> None:
    sock = tmp_path / 'daemon.sock'
    args = _first_flight_args(tmp_path, sock)
    args.canary = True

    # The default mock echoes the prompt, so the marker is present but the reply
    # is not exact. The old substring check incorrectly accepted this.
    with MockChatGPTTab(sock):
        status = cmd_first_flight(args)

    report = json.loads((tmp_path / 'flight.json').read_text(encoding='utf-8'))
    capsys.readouterr()
    assert status == 1
    assert report['canary_exact_match'] is False


def test_first_flight_never_overwrites_an_existing_composer(tmp_path: Path, capsys) -> None:
    sock = tmp_path / 'daemon.sock'
    args = _first_flight_args(tmp_path, sock)
    args.canary = True

    with MockChatGPTTab(sock) as tab:
        tab.composer = 'operator draft: preserve exactly'
        status = cmd_first_flight(args)
        composer_after = tab.composer

    report = json.loads((tmp_path / 'flight.json').read_text(encoding='utf-8'))
    capsys.readouterr()
    assert status == 1
    assert composer_after == 'operator draft: preserve exactly'
    assert report['drafted']['skipped'] is True
    assert report['canary']['blocked'] == 'surface preflight was not clean'


def test_first_flight_never_clears_an_existing_attachment(tmp_path: Path, capsys) -> None:
    sock = tmp_path / 'daemon.sock'
    args = _first_flight_args(tmp_path, sock)
    args.canary = True

    with MockChatGPTTab(sock) as tab:
        tab.attached = [{'name': 'operator-file.txt', 'bytes': 10}]
        status = cmd_first_flight(args)
        attachments_after = list(tab.attached)

    report = json.loads((tmp_path / 'flight.json').read_text(encoding='utf-8'))
    capsys.readouterr()
    assert status == 1
    assert attachments_after == [{'name': 'operator-file.txt', 'bytes': 10}]
    assert report['idle']['composer']['attachment_chip_count'] == 1
    assert report['drafted']['skipped'] is True


def test_cli_proof_autopilot_dry_run_smoke(tmp_path, monkeypatch):
    import chatgpt_proof_autopilot as autopilot_module
    from glassttyd import cli

    monkeypatch.setattr(autopilot_module, 'DEFAULT_OPERATOR_STATE', tmp_path / 'operator-state.json')
    parser = cli.build_parser()
    out = tmp_path / 'autopilot.json'
    args = parser.parse_args(['proof-autopilot', '--summary-out', str(out)])
    assert args.command == 'proof-autopilot'
    result = args.func(args)
    assert result == 0
    assert out.exists()
