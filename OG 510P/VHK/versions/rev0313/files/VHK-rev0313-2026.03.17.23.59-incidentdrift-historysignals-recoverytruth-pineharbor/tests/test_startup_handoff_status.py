from __future__ import annotations

from pathlib import Path

from vhk.project.startup_handoff_status import summarize_startup_handoff_status


def test_startup_handoff_reports_manual_for_environment_only_lane(tmp_path: Path) -> None:
    payload = summarize_startup_handoff_status(
        service_mode='environment-only',
        expected_units=[],
        units=[],
        autostart_desktop=tmp_path / 'missing.desktop',
        systemctl_available=True,
    )
    assert payload['verdict'] == 'manual_or_external_owner'
    assert 'manual or delegated' in payload['summary']


def test_startup_handoff_reports_primary_user_unit_owner(tmp_path: Path) -> None:
    payload = summarize_startup_handoff_status(
        service_mode='socket-activated-busd',
        expected_units=['vhk-busd-proj.socket', 'vhk-busd-proj.service'],
        units=[
            {
                'unit': 'vhk-busd-proj.socket',
                'unit_file_state': 'enabled',
                'load_state': 'loaded',
            },
            {
                'unit': 'vhk-busd-proj.service',
                'unit_file_state': 'static',
                'load_state': 'loaded',
            },
        ],
        autostart_desktop=tmp_path / 'missing.desktop',
        systemctl_available=True,
    )
    assert payload['verdict'] == 'primary_user_unit_owner'
    assert payload['counts']['enabled_unit_count'] == 1


def test_startup_handoff_reports_duplicate_risk_when_unit_and_autostart_exist(tmp_path: Path) -> None:
    autostart = tmp_path / 'vhk-busd-proj.desktop'
    autostart.write_text(
        '\n'.join(
            [
                '[Desktop Entry]',
                'Type=Application',
                'Name=VHK session services',
                'Exec=/usr/bin/env sh -lc true',
                'TryExec=sh',
                '',
            ]
        )
    )
    payload = summarize_startup_handoff_status(
        service_mode='socket-activated-busd',
        expected_units=['vhk-busd-proj.socket'],
        units=[{'unit': 'vhk-busd-proj.socket', 'unit_file_state': 'enabled', 'load_state': 'loaded'}],
        autostart_desktop=autostart,
        systemctl_available=True,
    )
    assert payload['verdict'] == 'duplicate_start_risk'
    assert payload['autostart']['effective'] is True


def test_startup_handoff_reports_hidden_autostart_without_owner(tmp_path: Path) -> None:
    autostart = tmp_path / 'vhk-busd-proj.desktop'
    autostart.write_text(
        '\n'.join(
            [
                '[Desktop Entry]',
                'Type=Application',
                'Name=VHK session services',
                'Hidden=true',
                'TryExec=sh',
                '',
            ]
        )
    )
    payload = summarize_startup_handoff_status(
        service_mode='socket-activated-busd',
        expected_units=['vhk-busd-proj.socket'],
        units=[{'unit': 'vhk-busd-proj.socket', 'unit_file_state': 'disabled', 'load_state': 'loaded'}],
        autostart_desktop=autostart,
        systemctl_available=True,
    )
    assert payload['verdict'] == 'autostart_hidden_no_owner'
    assert payload['autostart']['state'] == 'hidden'
