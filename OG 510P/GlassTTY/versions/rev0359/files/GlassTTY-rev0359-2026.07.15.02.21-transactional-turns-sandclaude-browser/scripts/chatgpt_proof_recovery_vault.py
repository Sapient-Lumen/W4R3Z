#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from chatgpt_proof_ingest import (
    DEFAULT_CHECK_SUMMARY,
    DEFAULT_EXPORT_SUMMARY,
    DEFAULT_FINAL_SUMMARY,
    DEFAULT_OUT as DEFAULT_CAPTURE_OUT,
    DEFAULT_REDACTED_OUT,
    DEFAULT_SUMMARY as DEFAULT_INGEST_SUMMARY,
    ROOT,
    display_path,
    ingest_capture,
    read_json,
    redact_large_data_urls,
    sha256_file,
    validate_capture,
    write_json,
)

SCHEMA_VERSION = 1
DEFAULT_SUMMARY = ROOT / 'validation' / 'latest' / 'chatgpt-proof-recovery-vault-summary.json'
DEFAULT_EXTRACTED_OUT = ROOT / 'validation' / 'latest' / 'chatgpt-first-proof-capture.from-recovery-vault.json'
DEFAULT_REDACTED_OUT = ROOT / 'validation' / 'latest' / 'chatgpt-first-proof-capture.from-recovery-vault.redacted.json'
DEFAULT_PACK_DIR = ROOT / 'validation' / 'latest' / 'chatgpt-proof-recovery-vault-evidence-pack'
RECOVERY_STORAGE_KEY = 'glasstty.chatgpt.firstProof.recoveryVault.v1'

JsonDict = dict[str, Any]


def utcnow() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def fnv1a32_text(value: str) -> str:
    h = 2166136261
    for ch in value:
        h ^= ord(ch)
        h = (h * 16777619) & 0xFFFFFFFF
    return f'fnv1a32:{h:08x}'


def canonical_document_json(document: JsonDict) -> str:
    # Mirrors the side-panel's JSON.stringify(document) closely enough for the
    # vault integrity check: no whitespace, preserved object insertion order.
    return json.dumps(document, ensure_ascii=False, separators=(',', ':'))


def classify_payload(payload: Any) -> str:
    if not isinstance(payload, dict):
        return 'invalid-json-root'
    storage_key = payload.get('storage_key')
    storage_backend = payload.get('storage_backend')
    if storage_key == RECOVERY_STORAGE_KEY or storage_backend == 'chrome.storage.local':
        if isinstance(payload.get('document'), dict):
            return 'recovery-vault-full-document'
        return 'recovery-vault-preview-only'
    if isinstance(payload.get('actions'), list) or payload.get('surface_key') == 'chatgpt':
        return 'proof-capture-json'
    if isinstance(payload.get('redacted_preview'), dict):
        return 'recovery-vault-preview-only'
    return 'unknown-json-root'


def extract_document(payload: JsonDict, kind: str) -> JsonDict | None:
    if kind == 'proof-capture-json':
        return payload
    if kind == 'recovery-vault-full-document' and isinstance(payload.get('document'), dict):
        return payload['document']  # type: ignore[return-value]
    return None


def vault_integrity(payload: JsonDict, document: JsonDict | None) -> JsonDict:
    result: JsonDict = {
        'storage_key': payload.get('storage_key'),
        'storage_backend': payload.get('storage_backend'),
        'saved_at': payload.get('saved_at'),
        'save_reason': payload.get('save_reason'),
        'attempt_id': payload.get('attempt_id'),
        'envelope_count': payload.get('envelope_count'),
        'document_bytes_claimed': payload.get('document_bytes'),
        'document_hash_claimed': payload.get('document_hash'),
        'saved_full_document': payload.get('saved_full_document'),
        'has_screenshot_claimed': payload.get('has_screenshot'),
        'warnings': payload.get('warnings') if isinstance(payload.get('warnings'), list) else [],
    }
    if document is None:
        result.update({
            'document_present': False,
            'document_bytes_actual': None,
            'document_hash_actual': None,
            'document_hash_matches_claim': False,
            'document_bytes_match_claim': False,
        })
        return result
    raw = canonical_document_json(document)
    actual_hash = fnv1a32_text(raw)
    actual_bytes = len(raw)
    claimed_hash = payload.get('document_hash')
    claimed_bytes = payload.get('document_bytes')
    result.update({
        'document_present': True,
        'document_bytes_actual': actual_bytes,
        'document_hash_actual': actual_hash,
        'document_hash_matches_claim': bool(isinstance(claimed_hash, str) and claimed_hash == actual_hash),
        'document_bytes_match_claim': bool(isinstance(claimed_bytes, int) and claimed_bytes == actual_bytes),
    })
    return result


def analyze_recovery_vault(
    input_path: Path,
    *,
    out: Path | None = None,
    redacted_out: Path | None = None,
    summary_out: Path = DEFAULT_SUMMARY,
    require_full_document: bool = False,
    require_integrity_match: bool = False,
    require_live_candidate: bool = False,
    ingest: bool = False,
    ingest_out: Path = DEFAULT_CAPTURE_OUT,
    ingest_redacted_out: Path | None = DEFAULT_REDACTED_OUT,
    ingest_summary_out: Path = DEFAULT_INGEST_SUMMARY,
    finalize: bool = False,
    pack_dir: Path = DEFAULT_PACK_DIR,
    final_summary_path: Path = DEFAULT_FINAL_SUMMARY,
    export_summary_path: Path = DEFAULT_EXPORT_SUMMARY,
    check_summary_path: Path = DEFAULT_CHECK_SUMMARY,
    clean: bool = False,
) -> JsonDict:
    payload = read_json(input_path)
    kind = classify_payload(payload)
    blockers: list[str] = []
    warnings: list[str] = []
    recommendations: list[str] = []

    if not isinstance(payload, dict):
        blockers.append('input root is not a JSON object')
        payload = {}
    document = extract_document(payload, kind)
    integrity = vault_integrity(payload, document) if kind.startswith('recovery-vault') else {
        'document_present': document is not None,
        'document_hash_matches_claim': None,
        'document_bytes_match_claim': None,
    }

    if kind == 'unknown-json-root':
        blockers.append('input is not a side-panel proof JSON or recovery-vault record')
    if kind == 'recovery-vault-preview-only':
        blockers.append('recovery vault contains only a redacted preview; restore or download the full proof JSON from the side panel')
    if require_full_document and document is None:
        blockers.append('--require-full-document was requested but no full proof document is available')
    if require_integrity_match and kind.startswith('recovery-vault'):
        if not integrity.get('document_hash_matches_claim'):
            blockers.append('vault document hash does not match the recovery-vault claim')
        if not integrity.get('document_bytes_match_claim'):
            blockers.append('vault document byte count does not match the recovery-vault claim')

    validation: JsonDict | None = None
    if document is not None:
        validation = validate_capture(document, source_path=input_path)
        if require_live_candidate and not validation.get('live_candidate'):
            blockers.append('extracted proof document is not a live candidate')
        if out is not None:
            normalized = copy.deepcopy(document)
            normalized.setdefault('recovery_vault_extract', {})
            if isinstance(normalized['recovery_vault_extract'], dict):
                normalized['recovery_vault_extract'].update({
                    'extracted_at': utcnow(),
                    'source_path': display_path(input_path),
                    'source_sha256': sha256_file(input_path),
                    'source_kind': kind,
                    'vault_document_hash_matches_claim': integrity.get('document_hash_matches_claim'),
                    'vault_document_bytes_match_claim': integrity.get('document_bytes_match_claim'),
                })
            write_json(out, normalized)
            if redacted_out is not None:
                write_json(redacted_out, redact_large_data_urls(normalized))
    else:
        recommendations.append('Use the side panel Restore recovery vault or Download proof JSON control; preview-only vault records cannot be finalized.')

    ingest_report: JsonDict | None = None
    if ingest:
        if blockers and require_live_candidate:
            ingest_report = {
                'ok': False,
                'verdict': 'proof-ingest-skipped-recovery-vault-blocked',
                'reason': 'recovery-vault analysis did not pass requested gates',
            }
        elif document is None:
            ingest_report = {
                'ok': False,
                'verdict': 'proof-ingest-skipped-no-full-document',
                'reason': 'no full proof document can be ingested from this recovery-vault input',
            }
        else:
            staging = out or DEFAULT_EXTRACTED_OUT
            if not staging.exists():
                write_json(staging, document)
            ingest_report = ingest_capture(
                staging,
                out=ingest_out,
                redacted_out=ingest_redacted_out,
                summary_out=ingest_summary_out,
                require_live_candidate=require_live_candidate,
                finalize=finalize,
                pack_dir=pack_dir,
                final_summary_path=final_summary_path,
                export_summary_path=export_summary_path,
                check_summary_path=check_summary_path,
                clean=clean,
            )

    if not blockers:
        if kind == 'recovery-vault-full-document':
            recommendations.append('Recovery vault contains a full proof document. Prefer proof-ingest on the extracted/normalized JSON next.')
        elif kind == 'proof-capture-json':
            recommendations.append('Input is already a proof capture JSON. Use proof-ingest --require-live-candidate when it is a live side-panel download.')
    if require_integrity_match and kind == 'proof-capture-json':
        warnings.append('--require-integrity-match applies only to recovery-vault records, not plain proof JSON downloads')

    ok = not blockers
    if kind == 'recovery-vault-full-document' and ok:
        verdict = 'recovery-vault-full-document-ok'
    elif kind == 'proof-capture-json' and ok:
        verdict = 'proof-capture-json-ok'
    elif kind == 'recovery-vault-preview-only':
        verdict = 'recovery-vault-preview-only-blocked'
    else:
        verdict = 'recovery-vault-analysis-blocked'

    report: JsonDict = {
        'schema_version': SCHEMA_VERSION,
        'tool': 'glasstty-chatgpt-proof-recovery-vault',
        'generated_at': utcnow(),
        'ok': ok,
        'verdict': verdict,
        'input_path': display_path(input_path),
        'input_sha256': sha256_file(input_path) if input_path.exists() else None,
        'input_kind': kind,
        'recovery_vault': integrity,
        'extracted_document': {
            'present': document is not None,
            'output_path': display_path(out) if out is not None else None,
            'redacted_output_path': display_path(redacted_out) if redacted_out is not None else None,
        },
        'capture_validation': validation,
        'ingest': ingest_report,
        'blockers': blockers,
        'warnings': warnings,
        'recommendations': recommendations,
    }
    write_json(summary_out, report)
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Inspect, recover, and optionally ingest a ChatGPT side-panel recovery-vault JSON or proof JSON.')
    parser.add_argument('--input', type=Path, required=True, help='Recovery-vault JSON or side-panel proof JSON')
    parser.add_argument('--out', type=Path, default=DEFAULT_EXTRACTED_OUT, help='Extracted proof document output path; pass empty string to disable')
    parser.add_argument('--redacted-out', type=Path, default=DEFAULT_REDACTED_OUT, help='Redacted extracted proof preview; pass empty string to disable')
    parser.add_argument('--summary-out', type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument('--require-full-document', action='store_true')
    parser.add_argument('--require-integrity-match', action='store_true')
    parser.add_argument('--require-live-candidate', action='store_true')
    parser.add_argument('--ingest', action='store_true', help='Run proof-ingest against the extracted document')
    parser.add_argument('--ingest-out', type=Path, default=DEFAULT_CAPTURE_OUT)
    parser.add_argument('--ingest-redacted-out', type=Path, default=DEFAULT_REDACTED_OUT)
    parser.add_argument('--ingest-summary-out', type=Path, default=DEFAULT_INGEST_SUMMARY)
    parser.add_argument('--finalize', action='store_true', help='When --ingest succeeds, run proof-finalize-pack')
    parser.add_argument('--pack-dir', type=Path, default=DEFAULT_PACK_DIR)
    parser.add_argument('--final-summary-out', type=Path, default=DEFAULT_FINAL_SUMMARY)
    parser.add_argument('--export-summary-out', type=Path, default=DEFAULT_EXPORT_SUMMARY)
    parser.add_argument('--check-summary-out', type=Path, default=DEFAULT_CHECK_SUMMARY)
    parser.add_argument('--clean', action='store_true')
    parser.add_argument('--pretty', action='store_true')
    return parser


def _optional_path(value: Path | None) -> Path | None:
    if value is None:
        return None
    if str(value) in {'', 'none', 'None', '-'}:
        return None
    return value


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = analyze_recovery_vault(
        args.input,
        out=_optional_path(args.out),
        redacted_out=_optional_path(args.redacted_out),
        summary_out=args.summary_out,
        require_full_document=args.require_full_document,
        require_integrity_match=args.require_integrity_match,
        require_live_candidate=args.require_live_candidate,
        ingest=args.ingest,
        ingest_out=args.ingest_out,
        ingest_redacted_out=_optional_path(args.ingest_redacted_out),
        ingest_summary_out=args.ingest_summary_out,
        finalize=args.finalize,
        pack_dir=args.pack_dir,
        final_summary_path=args.final_summary_out,
        export_summary_path=args.export_summary_out,
        check_summary_path=args.check_summary_out,
        clean=args.clean,
    )
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=bool(args.pretty)))
    return 0 if report.get('ok') else 2


if __name__ == '__main__':
    raise SystemExit(main())
