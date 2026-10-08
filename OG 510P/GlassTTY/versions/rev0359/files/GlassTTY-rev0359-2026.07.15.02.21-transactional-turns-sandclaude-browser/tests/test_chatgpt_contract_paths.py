from __future__ import annotations

import json
from pathlib import Path

from chatgpt_contract_paths import active_contract_path, active_fixture_path


def test_active_contract_path_picks_highest_revision(tmp_path: Path) -> None:
    latest = tmp_path / 'validation' / 'latest'
    latest.mkdir(parents=True)
    (latest / 'chatgpt-live-surface-contract-rev0001-2026.01.01.json').write_text('{}')
    (latest / 'chatgpt-live-surface-contract-rev0335-2026.06.13.json').write_text('{}')
    (latest / 'chatgpt-live-surface-contract-rev0334-2026.06.13.json').write_text('{}')

    assert active_contract_path(tmp_path).name == 'chatgpt-live-surface-contract-rev0335-2026.06.13.json'


def test_active_fixture_path_picks_highest_revision(tmp_path: Path) -> None:
    latest = tmp_path / 'validation' / 'latest'
    latest.mkdir(parents=True)
    (latest / 'chatgpt-live-surface-contract-fixture-rev0334.json').write_text('{}')
    (latest / 'chatgpt-live-surface-contract-fixture-rev0335.json').write_text('{}')

    assert active_fixture_path(tmp_path).name == 'chatgpt-live-surface-contract-fixture-rev0335.json'
