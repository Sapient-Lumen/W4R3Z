#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SUMMARY = ROOT / 'validation' / 'latest' / 'chatgpt-proof-transfer-audit.json'
SCHEMA_VERSION = 1
JsonDict = dict[str, Any]


def utcnow() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def display_path(path: Path | None, *, root: Path = ROOT) -> str | None:
    if path is None:
        return None
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except Exception:
        return str(path)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def compact(value: Any) -> str:
    return ' '.join(value.split()).strip() if isinstance(value, str) else ''


def payload_of(row: JsonDict | None) -> JsonDict:
    if isinstance(row, dict) and isinstance(row.get('payload'), dict):
        return row['payload']  # type: ignore[return-value]
    return {}


def row_type(row: JsonDict) -> str:
    for key in ('type', 'request_type', 'response_type'):
        value = row.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ''


def actions(source: JsonDict) -> list[JsonDict]:
    rows = source.get('actions')
    if isinstance(rows, list):
        return [row for row in rows if isinstance(row, dict)]
    return []


def raw_envelopes(source: JsonDict) -> list[JsonDict]:
    rows = source.get('raw_envelopes')
    if isinstance(rows, list):
        return [row for row in rows if isinstance(row, dict)]
    return []


def classify_root(source: Any) -> str:
    if not isinstance(source, dict):
        return 'non-object-json-root'
    if isinstance(source.get('document'), dict) and source.get('storage_key') == 'glasstty.chatgpt.firstProof.recoveryVault.v1':
        return 'recovery-vault-full-document'
    if source.get('storage_key') == 'glasstty.chatgpt.firstProof.recoveryVault.v1':
        return 'recovery-vault-preview-only'
    if source.get('surface_key') == 'chatgpt' and (isinstance(source.get('actions'), list) or isinstance(source.get('raw_envelopes'), list)):
        return 'proof-capture-json'
    return 'unknown-json-root'


def png_dimensions(data: bytes) -> JsonDict:
    if len(data) < 24 or not data.startswith(b'\x89PNG\r\n\x1a\n'):
        return {'width': None, 'height': None, 'error': 'not-png'}
    return {'width': int.from_bytes(data[16:20], 'big'), 'height': int.from_bytes(data[20:24], 'big')}


def screenshot_info(data_url: Any) -> JsonDict:
    prefix = 'data:image/png;base64,'
    if not isinstance(data_url, str) or not data_url.startswith(prefix):
        return {'present': False, 'valid_png_data_url': False}
    try:
        data = base64.b64decode(data_url.split(',', 1)[1], validate=True)
    except Exception as exc:
        return {'present': True, 'valid_png_data_url': False, 'decode_error': str(exc)}
    dims = png_dimensions(data)
    valid = dims.get('error') is None
    return {
        'present': True,
        'valid_png_data_url': valid,
        'byte_length': len(data),
        'sha256': sha256_bytes(data),
        'dimensions': dims,
        'placeholder_sized': dims.get('width') == 1 and dims.get('height') == 1,
    }


def sequence_index(row: JsonDict) -> int | None:
    value = row.get('sequence_index')
    return value if isinstance(value, int) else None


def audit_transfer(
    input_path: Path,
    *,
    summary_out: Path | None = DEFAULT_SUMMARY,
    require_proof_capture: bool = True,
    require_ready_to_download: bool = False,
    require_full_screenshot: bool = False,
) -> JsonDict:
    blockers: list[str] = []
    warnings: list[str] = []
    recommendations: list[str] = []
    observed: JsonDict = {}
    raw_bytes = b''
    parsed: Any = None

    if not input_path.exists():
        blockers.append('input proof JSON does not exist')
    else:
        raw_bytes = input_path.read_bytes()
        observed['input_byte_length'] = len(raw_bytes)
        observed['input_sha256'] = sha256_bytes(raw_bytes)
        try:
            parsed = json.loads(raw_bytes.decode('utf-8'))
        except Exception as exc:
            blockers.append(f'input is not valid UTF-8 JSON: {exc}')

    root_kind = classify_root(parsed)
    observed['root_kind'] = root_kind
    source = parsed if isinstance(parsed, dict) else {}

    if require_proof_capture and root_kind != 'proof-capture-json':
        blockers.append(f'input is {root_kind}, not proof-capture-json')
        if root_kind.startswith('recovery-vault'):
            recommendations.append('Run proof-recovery-vault --input <file> --require-full-document --ingest instead of proof-transfer-audit directly.')

    action_rows = actions(source)
    envelope_rows = raw_envelopes(source)
    observed['actions_count'] = len(action_rows)
    observed['raw_envelopes_count'] = len(envelope_rows)
    observed['action_types'] = [row_type(row) for row in action_rows]
    observed['raw_envelope_types'] = [row_type(row) for row in envelope_rows]
    observed['attempt_id'] = source.get('attempt_id') if isinstance(source.get('attempt_id'), str) else None

    if not action_rows:
        blockers.append('proof capture has no actions array')
    if not envelope_rows:
        blockers.append('proof capture has no raw_envelopes array')
    if action_rows and envelope_rows and len(action_rows) != len(envelope_rows):
        blockers.append('actions and raw_envelopes counts differ')
    if action_rows and envelope_rows:
        mismatches = []
        for index, (action, envelope) in enumerate(zip(action_rows, envelope_rows)):
            if row_type(action) != row_type(envelope):
                mismatches.append({'index': index, 'action_type': row_type(action), 'raw_envelope_type': row_type(envelope)})
        if mismatches:
            blockers.append('actions and raw_envelopes type order differ')
            observed['type_mismatches'] = mismatches[:10]

    indices = [sequence_index(row) for row in action_rows]
    observed['sequence_indices'] = indices
    if any(index is None for index in indices):
        blockers.append('one or more actions lack integer sequence_index')
    elif indices and indices != list(range(len(indices))):
        blockers.append('action sequence_index values are not contiguous from zero in document order')

    root_attempt = source.get('attempt_id')
    if not isinstance(root_attempt, str) or not root_attempt.strip():
        blockers.append('root attempt_id is missing')
    else:
        inconsistent = []
        for index, row in enumerate(action_rows):
            row_attempt = row.get('attempt_id')
            payload_attempt = payload_of(row).get('attempt_id')
            if isinstance(row_attempt, str) and row_attempt != root_attempt:
                inconsistent.append({'index': index, 'field': 'attempt_id', 'value': row_attempt})
            if isinstance(payload_attempt, str) and payload_attempt != root_attempt:
                inconsistent.append({'index': index, 'field': 'payload.attempt_id', 'value': payload_attempt})
        if inconsistent:
            blockers.append('one or more action attempt_id values differ from root attempt_id')
            observed['attempt_id_mismatches'] = inconsistent[:10]

    final_ready = [row for row in action_rows if row_type(row) == 'proof.operator_readiness' and payload_of(row).get('verdict') == 'proof-attempt-ready-to-download']
    observed['ready_to_download_envelope_count'] = len(final_ready)
    if require_ready_to_download and not final_ready:
        blockers.append('missing ready-to-download proof.operator_readiness envelope')
    if final_ready and action_rows and action_rows[-1] is not final_ready[-1]:
        blockers.append('final proof.operator_readiness ready-to-download envelope is not the last action')

    screenshot = screenshot_info(source.get('visible_tab_screenshot_data_url'))
    observed['screenshot'] = screenshot
    if require_full_screenshot:
        if not screenshot.get('present'):
            blockers.append('root visible_tab_screenshot_data_url is missing')
        elif not screenshot.get('valid_png_data_url'):
            blockers.append('root visible_tab_screenshot_data_url is not a valid PNG data URL')
        elif screenshot.get('placeholder_sized'):
            blockers.append('root visible_tab_screenshot_data_url is placeholder-sized')

    transfer = source.get('operator_transfer') if isinstance(source.get('operator_transfer'), dict) else {}
    observed['recommended_json_filename'] = transfer.get('recommended_json_filename')
    if isinstance(transfer.get('recommended_json_filename'), str) and input_path.name != transfer.get('recommended_json_filename'):
        warnings.append('input filename differs from operator_transfer.recommended_json_filename')

    ok = not blockers
    report: JsonDict = {
        'schema_version': SCHEMA_VERSION,
        'tool': 'glasstty-chatgpt-proof-transfer-audit',
        'checked_at': utcnow(),
        'input_path': display_path(input_path),
        'ok': ok,
        'verdict': 'proof-transfer-audit-ok' if ok else 'proof-transfer-audit-blocked',
        'blockers': blockers,
        'warnings': warnings,
        'recommendations': recommendations,
        'observed': observed,
        'summary_path': display_path(summary_out) if summary_out else None,
    }
    if summary_out is not None:
        write_json(summary_out, report)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Audit downloaded ChatGPT side-panel proof JSON transfer integrity before attempt audit/ingest.')
    parser.add_argument('--input', required=True)
    parser.add_argument('--summary-out', default=str(DEFAULT_SUMMARY))
    parser.add_argument('--no-require-proof-capture', action='store_true')
    parser.add_argument('--require-ready-to-download', action='store_true')
    parser.add_argument('--require-full-screenshot', action='store_true')
    parser.add_argument('--pretty', action='store_true')
    args = parser.parse_args(argv)
    report = audit_transfer(
        Path(args.input),
        summary_out=Path(args.summary_out),
        require_proof_capture=not args.no_require_proof_capture,
        require_ready_to_download=args.require_ready_to_download,
        require_full_screenshot=args.require_full_screenshot,
    )
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=bool(args.pretty)))
    return 0 if report.get('ok') else 2


if __name__ == '__main__':
    raise SystemExit(main())
