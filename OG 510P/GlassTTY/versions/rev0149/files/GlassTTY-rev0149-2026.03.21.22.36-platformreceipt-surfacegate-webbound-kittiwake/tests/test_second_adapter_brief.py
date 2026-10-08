from __future__ import annotations

import importlib.util
from pathlib import Path

from test_second_adapter_report import _seed_lock, _seed_matrix, _seed_records

ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location('second_adapter_brief', ROOT / 'scripts' / 'second_adapter_brief.py')
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)

build_second_adapter_brief = MODULE.build_second_adapter_brief
capture_second_adapter_brief = MODULE.capture_second_adapter_brief
write_root_second_adapter_brief = MODULE.write_root_second_adapter_brief
summarize_capture_history = MODULE.summarize_capture_history


def test_second_adapter_brief_defaults_to_recommended_surface_and_primary_route(tmp_path: Path) -> None:
    _seed_matrix(tmp_path)
    _seed_lock(tmp_path)
    _seed_records(tmp_path)
    data = build_second_adapter_brief(root=tmp_path)
    assert data['selected_surface']['surface_key'] == 'chatgpt'
    assert data['selected_surface']['primary_route_hint'] == 'https://chatgpt.com/overview'
    assert len(data['phases']) == 4
    assert data['phases'][0]['phase_key'] == 'route-anchor-baseline'


def test_capture_and_write_root_second_adapter_brief(tmp_path: Path) -> None:
    _seed_matrix(tmp_path)
    _seed_lock(tmp_path)
    _seed_records(tmp_path)
    output_dir = tmp_path / 'validation' / 'latest' / 'second-adapter-brief'
    history_path = tmp_path / 'validation' / 'second-adapter-brief-captures.json'
    payload = capture_second_adapter_brief(root=tmp_path, output_dir=output_dir, history_path=history_path)
    assert (output_dir / 'second-adapter-brief.json').exists()
    assert (output_dir / 'SUMMARY.md').exists()
    assert payload['history_update']['capture_count_after_write'] == 1
    history = summarize_capture_history(history_path)
    assert history['capture_count'] == 1
    root_payload = write_root_second_adapter_brief(root=tmp_path)
    assert (tmp_path / 'SECOND-ADAPTER-BRIEF.json').exists()
    assert root_payload['selected_surface']['surface_key'] == 'chatgpt'
