from __future__ import annotations

import importlib.util
import shutil
from pathlib import Path

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


def _seed_minimal_root(tmp_path: Path) -> None:
    shutil.copy(ROOT / 'CHATGPT-SURFACE-PATTERN-ATLAS.json', tmp_path / 'CHATGPT-SURFACE-PATTERN-ATLAS.json')
    shutil.copy(ROOT / 'CHATGPT-PROOF-EVIDENCE-ATLAS.json', tmp_path / 'CHATGPT-PROOF-EVIDENCE-ATLAS.json')
    schemas = tmp_path / 'schemas'
    schemas.mkdir()
    shutil.copy(ROOT / 'schemas' / 'chatgpt-first-proof-bundle.schema.json', schemas / 'chatgpt-first-proof-bundle.schema.json')
    pack = tmp_path / 'validation' / 'live-proof-evidence' / 'chatgpt' / 'chatgpt-proof-evidence-pack'
    pack.mkdir(parents=True)
    (pack / 'README.md').write_text('placeholder\n', encoding='utf-8')


def test_chatgpt_first_proof_kit_is_chatgpt_only_and_self_contained(tmp_path: Path) -> None:
    _seed_minimal_root(tmp_path)
    payload = build_chatgpt_first_proof_kit(root=tmp_path)
    assert payload['state']['provider_scope'] == 'chatgpt-only'
    assert payload['selected_surface']['surface_key'] == 'chatgpt'
    assert payload['selected_surface']['role'] == 'primary-and-only-provider'
    assert payload['selected_surface']['primary_route_hint'] == 'https://chatgpt.com/'
    assert payload['selected_surface']['required_host'] == 'chatgpt.com'
    assert payload['probe_prompt']['expected_exact_reply'] == 'GLASSTTY-CHECKPOINT'
    assert payload['selector_contract']['composer_candidates'][0]['family'] == 'accessible-textbox'
    assert payload['artifact_plan']['pack_dir'].endswith('chatgpt-proof-evidence-pack')
    assert len(payload['artifact_plan']['required_slots']) == 30
    slot_files = {slot['filename'] for slot in payload['artifact_plan']['required_slots']}
    assert 'bundle-manifest.json' in slot_files
    assert 'privacy-redaction-review.md' in slot_files
    assert 'settled-generation-sequence-witness.json' in slot_files
    assert 'same-conversation-route-witness.json' in slot_files
    assert 'exact-readback-witness.json' in slot_files
    assert 'schemas/chatgpt-first-proof-bundle.schema.json' == payload['artifact_plan']['bundle_schema']
    assert payload['evaluator_contract']['schema_version'] == 20
    assert 'write_and_submit_readbacks_exact_probe' in payload['evaluator_contract']['required_checks']
    assert 'no_cross_surface_conflicts' in payload['evaluator_contract']['required_checks']
    assert payload['commands']['audit_captured_proof_bundle'].startswith('python scripts/chatgpt-first-proof-bundle-audit.py audit')
    assert payload['commands']['extension_build'] == 'npm --prefix extension run build'


def test_capture_write_root_and_write_candidate_bundle(tmp_path: Path) -> None:
    _seed_minimal_root(tmp_path)
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
    bundle_path = tmp_path / 'validation' / 'latest' / 'chatgpt-routefirst-chromium-live-candidate.json'
    assert bundle_path.exists()
    assert bundle_payload['bundle_status'] == 'candidate'
    assert bundle_payload['provider_scope'] == 'chatgpt-only'
    paths = [item['path'] for item in bundle_payload['artifact_refs']]
    assert len(paths) == len(set(paths))
    assert 'CHATGPT-FIRST-PROOF-KIT.json' in paths
    assert 'CHATGPT-SURFACE-PATTERN-ATLAS.json' in paths
    assert 'CHATGPT-PROOF-EVIDENCE-ATLAS.json' in paths
    assert 'schemas/chatgpt-first-proof-bundle.schema.json' in paths
    assert 'validation/live-proof-evidence/chatgpt/chatgpt-proof-evidence-pack/README.md' in paths
