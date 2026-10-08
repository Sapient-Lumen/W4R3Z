from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from test_second_adapter_report import _seed_lock, _seed_matrix, _seed_records

ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location('chatgpt_posture_matrix', ROOT / 'scripts' / 'chatgpt_posture_matrix.py')
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)

build_chatgpt_posture_matrix = MODULE.build_chatgpt_posture_matrix
capture_chatgpt_posture_matrix = MODULE.capture_chatgpt_posture_matrix
write_root_chatgpt_posture_matrix = MODULE.write_root_chatgpt_posture_matrix
summarize_capture_history = MODULE.summarize_capture_history


def _augment_lock(root: Path) -> None:
    lock_path = root / 'SUPPORT-SOURCE-LOCK.json'
    payload = json.loads(lock_path.read_text(encoding='utf-8'))
    payload['sources'].extend([
        {'source_key': 'chatgpt-home-page', 'title': 'The ChatGPT home page', 'url': 'https://help.openai.com/en/articles/9125172-the-chatgpt-home-page', 'tier': 'first-party-product-surface', 'surface_keys': ['chatgpt'], 'required_for_publication': True, 'reviewed_at': '2026-03-21'},
        {'source_key': 'chatgpt-capabilities-overview', 'title': 'ChatGPT Capabilities Overview', 'url': 'https://help.openai.com/en/articles/9260256-chatgpt-capabilities-overview', 'tier': 'first-party-product-surface', 'surface_keys': ['chatgpt'], 'required_for_publication': False, 'reviewed_at': '2026-03-21'},
        {'source_key': 'chatgpt-projects', 'title': 'Projects in ChatGPT', 'url': 'https://help.openai.com/en/articles/10169521-projects-in-chatgpt', 'tier': 'first-party-product-surface', 'surface_keys': ['chatgpt'], 'required_for_publication': False, 'reviewed_at': '2026-03-21'},
        {'source_key': 'chatgpt-canvas-feature', 'title': 'What is the canvas feature in ChatGPT and how do I use it?', 'url': 'https://help.openai.com/en/articles/9930697-what-is-the-canvas-feature-in-chatgpt-and-how-do-i-use-it', 'tier': 'first-party-product-surface', 'surface_keys': ['chatgpt'], 'required_for_publication': False, 'reviewed_at': '2026-03-21'},
        {'source_key': 'chatgpt-search', 'title': 'ChatGPT search', 'url': 'https://help.openai.com/en/articles/9237897-chatgpt-search', 'tier': 'first-party-product-surface', 'surface_keys': ['chatgpt'], 'required_for_publication': False, 'reviewed_at': '2026-03-21'},
        {'source_key': 'chatgpt-gpts-builder', 'title': 'Creating and editing GPTs', 'url': 'https://help.openai.com/en/articles/8554397-creating-a-gpt', 'tier': 'first-party-product-surface', 'surface_keys': ['chatgpt'], 'required_for_publication': False, 'reviewed_at': '2026-03-21'},
    ])
    lock_path.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')


def test_chatgpt_posture_matrix_builds_route_first_classifier(tmp_path: Path) -> None:
    _seed_matrix(tmp_path)
    _seed_lock(tmp_path)
    _seed_records(tmp_path)
    _augment_lock(tmp_path)
    payload = build_chatgpt_posture_matrix(root=tmp_path)
    assert payload['surface_key'] == 'chatgpt'
    assert 'guest-home-single-thread' in payload['baseline_allowed_postures']
    assert 'project-workspace-shell' in payload['branch_postures']
    assert 'search-capable-home-lane' in payload['caution_postures']
    gpts = [item for item in payload['postures'] if item['posture_key'] == 'gpts-builder-web-workspace'][0]
    assert gpts['route_hint'] == 'https://chatgpt.com/gpts'


def test_capture_and_write_root_chatgpt_posture_matrix(tmp_path: Path) -> None:
    _seed_matrix(tmp_path)
    _seed_lock(tmp_path)
    _seed_records(tmp_path)
    _augment_lock(tmp_path)
    output_dir = tmp_path / 'validation' / 'latest' / 'chatgpt-posture-matrix'
    history_path = tmp_path / 'validation' / 'chatgpt-posture-matrix-captures.json'
    payload = capture_chatgpt_posture_matrix(root=tmp_path, output_dir=output_dir, history_path=history_path)
    assert (output_dir / 'chatgpt-posture-matrix.json').exists()
    assert (output_dir / 'SUMMARY.md').exists()
    assert payload['history_update']['capture_count_after_write'] == 1
    history = summarize_capture_history(history_path)
    assert history['capture_count'] == 1
    root_payload = write_root_chatgpt_posture_matrix(root=tmp_path)
    assert (tmp_path / 'CHATGPT-POSTURE-MATRIX.json').exists()
    assert root_payload['counts']['branch_count'] == 3
