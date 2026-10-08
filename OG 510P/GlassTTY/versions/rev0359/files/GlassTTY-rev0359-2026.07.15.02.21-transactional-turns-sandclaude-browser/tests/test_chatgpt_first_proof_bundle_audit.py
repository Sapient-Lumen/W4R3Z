from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from test_chatgpt_first_proof_evaluator import ATTEMPT_ID, _reviewable_payload, _seed_kit

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('chatgpt_first_proof_bundle_audit', ROOT / 'scripts' / 'chatgpt_first_proof_bundle_audit.py')
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)

build_bundle_audit = MODULE.build_bundle_audit
audit_file = MODULE.audit_file
summary_markdown = MODULE.summary_markdown


def test_bundle_audit_builds_local_evidence_graph_for_reviewable_payload(tmp_path: Path) -> None:
    _seed_kit(tmp_path)
    payload = _reviewable_payload()

    audit = build_bundle_audit(payload, root=tmp_path)

    assert audit['schema_version'] == 1
    assert audit['evaluator_schema_version'] == 20
    assert audit['check_registry_audit']['ok'] is True
    assert audit['counts']['attempt_count'] == 1
    assert audit['counts']['action_record_count'] == 4
    assert audit['graph']['node_count'] == 4
    assert audit['graph']['edge_count'] == 3
    assert audit['evaluator_summary']['ok'] is True
    assert audit['evaluator_summary']['winning_attempt_id'] == ATTEMPT_ID
    assert audit['support_claim_effect'].startswith('none;')
    attempt = audit['attempts'][0]
    assert attempt['action_types_in_sequence_order'] == ['prompt.write', 'prompt.submit', 'transcript.latest', 'fixture.capture']
    assert attempt['duplicate_sequence_indices'] == []
    assert attempt['missing_sequence_index_paths'] == []
    assert attempt['conversation_route_paths'] == ['/c/example']


def test_bundle_audit_surfaces_duplicate_sequence_indices_without_public_claim(tmp_path: Path) -> None:
    _seed_kit(tmp_path)
    payload = _reviewable_payload()
    payload['actions'][2]['sequence_index'] = 1

    audit = build_bundle_audit(payload, root=tmp_path)

    assert audit['evaluator_summary']['ok'] is False
    assert 'explicit_sequence_indices_monotonic' in audit['evaluator_summary']['missing_required_checks']
    assert audit['attempts'][0]['duplicate_sequence_indices'] == [1]
    assert audit['support_claim_effect'].startswith('none;')


def test_bundle_audit_file_writes_json_and_summary(tmp_path: Path) -> None:
    _seed_kit(tmp_path)
    input_path = tmp_path / 'bundle.json'
    input_path.write_text(json.dumps(_reviewable_payload(), indent=2) + '\n', encoding='utf-8')
    output_dir = tmp_path / 'audit-output'

    audit = audit_file(input_path, root=tmp_path, output_dir=output_dir)

    assert (output_dir / 'chatgpt-first-proof-bundle-audit.json').exists()
    assert (output_dir / 'SUMMARY.md').exists()
    assert audit['input_sha256']
    text = summary_markdown(audit)
    assert 'ChatGPT first-proof bundle audit' in text
    assert 'evaluator_verdict' in text
