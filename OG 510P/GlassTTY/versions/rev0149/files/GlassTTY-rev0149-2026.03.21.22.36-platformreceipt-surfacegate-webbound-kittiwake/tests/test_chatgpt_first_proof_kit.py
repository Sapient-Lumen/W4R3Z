from __future__ import annotations

import importlib.util
from pathlib import Path

from test_second_adapter_report import _seed_lock, _seed_matrix, _seed_records

ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location('chatgpt_first_proof_kit', ROOT / 'scripts' / 'chatgpt_first_proof_kit.py')
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)

build_chatgpt_first_proof_kit = MODULE.build_chatgpt_first_proof_kit
capture_chatgpt_first_proof_kit = MODULE.capture_chatgpt_first_proof_kit
write_root_chatgpt_first_proof_kit = MODULE.write_root_chatgpt_first_proof_kit
write_candidate_bundle_manifest = MODULE.write_candidate_bundle_manifest
summarize_capture_history = MODULE.summarize_capture_history


def test_chatgpt_first_proof_kit_builds_from_second_adapter_brief_inputs(tmp_path: Path) -> None:
    _seed_matrix(tmp_path)
    _seed_lock(tmp_path)
    _seed_records(tmp_path)
    payload = build_chatgpt_first_proof_kit(root=tmp_path)
    assert payload['selected_surface']['surface_key'] == 'chatgpt'
    assert payload['selected_surface']['primary_route_hint'] == 'https://chatgpt.com/overview'
    assert payload['probe_prompt']['expected_exact_reply'] == 'GLASSTTY-CHECKPOINT'
    assert payload['selector_contract']['composer_candidates'][0]['family'] == 'accessible-textbox'
    assert payload['candidate_bundle_path'].endswith('chatgpt-routefirst-chromium-live-candidate.json')


def test_capture_write_root_and_write_candidate_bundle(tmp_path: Path) -> None:
    _seed_matrix(tmp_path)
    _seed_lock(tmp_path)
    _seed_records(tmp_path)
    output_dir = tmp_path / 'validation' / 'latest' / 'chatgpt-first-proof-kit'
    history_path = tmp_path / 'validation' / 'chatgpt-first-proof-kit-captures.json'
    payload = capture_chatgpt_first_proof_kit(root=tmp_path, output_dir=output_dir, history_path=history_path)
    assert (output_dir / 'chatgpt-first-proof-kit.json').exists()
    assert (output_dir / 'SUMMARY.md').exists()
    assert payload['history_update']['capture_count_after_write'] == 1
    history = summarize_capture_history(history_path)
    assert history['capture_count'] == 1
    root_payload = write_root_chatgpt_first_proof_kit(root=tmp_path)
    assert (tmp_path / 'CHATGPT-FIRST-PROOF-KIT.json').exists()
    assert root_payload['selected_surface']['surface_key'] == 'chatgpt'
    bundle_payload = write_candidate_bundle_manifest(root=tmp_path)
    bundle_path = tmp_path / 'docs' / 'support-bundles' / 'candidate' / 'chatgpt-routefirst-chromium-live-candidate.json'
    assert bundle_path.exists()
    assert bundle_payload['bundle_status'] == 'candidate'
    assert 'CHATGPT-FIRST-PROOF-KIT.json' in [item['path'] for item in bundle_payload['artifact_refs']]
