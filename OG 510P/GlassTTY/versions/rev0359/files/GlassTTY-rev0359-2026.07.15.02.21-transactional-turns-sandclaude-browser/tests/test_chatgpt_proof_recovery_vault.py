from __future__ import annotations

import json
from pathlib import Path

from chatgpt_proof_recovery_vault import (
    RECOVERY_STORAGE_KEY,
    analyze_recovery_vault,
    canonical_document_json,
    classify_payload,
    fnv1a32_text,
)
from test_chatgpt_proof_ingest import _live_candidate_payload


def _vault_record(document: dict) -> dict:
    raw = canonical_document_json(document)
    return {
        'schema_version': 1,
        'storage_key': RECOVERY_STORAGE_KEY,
        'storage_backend': 'chrome.storage.local',
        'saved_at': '2026-06-13T10:00:00.000Z',
        'save_reason': 'manual',
        'attempt_id': document.get('attempt_id', 'test-attempt'),
        'envelope_count': len(document.get('raw_envelopes', [])),
        'document_bytes': len(raw),
        'document_hash': fnv1a32_text(raw),
        'has_screenshot': True,
        'saved_full_document': True,
        'document': document,
        'redacted_preview': {'attempt_id': document.get('attempt_id', 'test-attempt')},
        'warnings': [],
    }


def test_classify_payload_distinguishes_vault_and_capture() -> None:
    document = _live_candidate_payload()
    assert classify_payload(document) == 'proof-capture-json'
    assert classify_payload(_vault_record(document)) == 'recovery-vault-full-document'
    assert classify_payload({'storage_key': RECOVERY_STORAGE_KEY, 'redacted_preview': {}}) == 'recovery-vault-preview-only'


def test_recovery_vault_extracts_full_document_and_can_ingest(tmp_path: Path) -> None:
    document = _live_candidate_payload()
    vault = _vault_record(document)
    input_path = tmp_path / 'vault.json'
    input_path.write_text(json.dumps(vault), encoding='utf-8')
    extracted = tmp_path / 'extracted.json'
    redacted = tmp_path / 'redacted.json'
    summary = tmp_path / 'summary.json'
    ingest_out = tmp_path / 'normalized.json'
    ingest_summary = tmp_path / 'ingest-summary.json'

    report = analyze_recovery_vault(
        input_path,
        out=extracted,
        redacted_out=redacted,
        summary_out=summary,
        require_full_document=True,
        require_integrity_match=True,
        require_live_candidate=True,
        ingest=True,
        ingest_out=ingest_out,
        ingest_summary_out=ingest_summary,
        ingest_redacted_out=tmp_path / 'ingest-redacted.json',
    )

    assert report['ok'] is True
    assert report['verdict'] == 'recovery-vault-full-document-ok'
    assert report['recovery_vault']['document_hash_matches_claim'] is True
    assert report['recovery_vault']['document_bytes_match_claim'] is True
    assert report['capture_validation']['live_candidate'] is True
    assert report['ingest']['verdict'] == 'proof-json-ingested-live-candidate'
    assert extracted.exists()
    assert redacted.exists()
    assert summary.exists()
    assert ingest_out.exists()


def test_preview_only_vault_is_blocked(tmp_path: Path) -> None:
    input_path = tmp_path / 'preview-only.json'
    input_path.write_text(json.dumps({
        'schema_version': 1,
        'storage_key': RECOVERY_STORAGE_KEY,
        'storage_backend': 'chrome.storage.local',
        'saved_full_document': False,
        'redacted_preview': {'attempt_id': 'lost'},
    }), encoding='utf-8')

    report = analyze_recovery_vault(input_path, summary_out=tmp_path / 'summary.json')

    assert report['ok'] is False
    assert report['verdict'] == 'recovery-vault-preview-only-blocked'
    assert any('preview' in blocker for blocker in report['blockers'])


def test_integrity_mismatch_blocks_when_required(tmp_path: Path) -> None:
    document = _live_candidate_payload()
    vault = _vault_record(document)
    vault['document_hash'] = 'fnv1a32:00000000'
    input_path = tmp_path / 'bad-vault.json'
    input_path.write_text(json.dumps(vault), encoding='utf-8')

    report = analyze_recovery_vault(
        input_path,
        summary_out=tmp_path / 'summary.json',
        require_integrity_match=True,
    )

    assert report['ok'] is False
    assert any('hash' in blocker for blocker in report['blockers'])
