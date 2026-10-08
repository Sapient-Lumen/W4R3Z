from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from test_chatgpt_first_proof_evaluator import _reviewable_payload

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('chatgpt_first_proof_schema_validation', ROOT / 'scripts' / 'chatgpt_first_proof_schema_validation.py')
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)

validate_payload = MODULE.validate_payload
validate_file = MODULE.validate_file
summary_markdown = MODULE.summary_markdown


def _schema() -> dict:
    return json.loads((ROOT / 'schemas' / 'chatgpt-first-proof-bundle.schema.json').read_text(encoding='utf-8'))


def _schema_payload() -> dict:
    payload = _reviewable_payload()
    payload['bundle_schema'] = 'chatgpt-first-proof-bundle/v1'
    payload['probe_prompt'] = {
        'text': 'Reply with exactly this text and nothing else: GLASSTTY-CHECKPOINT',
        'expected_exact_reply': 'GLASSTTY-CHECKPOINT',
    }
    payload['route_witness'] = {
        'adapter': 'chatgpt',
        'url': 'https://chatgpt.com/',
        'route_posture': 'plain-chat',
        'tab_id': 314159,
    }
    return payload


def test_schema_validation_accepts_reviewable_bundle_shape() -> None:
    report = validate_payload(_schema_payload(), _schema())

    assert report['ok'] is True
    assert report['validator_available'] is True
    assert report['error_count'] == 0
    assert report['errors'] == []


def test_schema_validation_rejects_missing_privacy_review() -> None:
    payload = _schema_payload()
    payload.pop('privacy_redaction_review')

    report = validate_payload(payload, _schema())

    assert report['ok'] is False
    assert any(error['path'] == '$' and 'privacy_redaction_review' in error['message'] for error in report['errors'])


def test_schema_validation_file_writes_report_and_summary(tmp_path: Path) -> None:
    input_path = tmp_path / 'bundle-manifest.json'
    schema_path = ROOT / 'schemas' / 'chatgpt-first-proof-bundle.schema.json'
    output_dir = tmp_path / 'schema-validation'
    input_path.write_text(json.dumps(_schema_payload(), indent=2) + '\n', encoding='utf-8')

    report = validate_file(input_path, schema_path=schema_path, output_dir=output_dir)

    assert report['ok'] is True
    assert report['input_sha256']
    assert report['schema_sha256']
    assert (output_dir / 'bundle-schema-validation.json').exists()
    assert (output_dir / 'SUMMARY.md').exists()
    assert 'ChatGPT first-proof bundle schema validation' in summary_markdown(report)
