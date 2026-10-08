#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = ROOT / 'validation' / 'live-proof-evidence' / 'chatgpt' / 'chatgpt-proof-evidence-pack' / 'bundle-manifest.json'
DEFAULT_SCHEMA = ROOT / 'schemas' / 'chatgpt-first-proof-bundle.schema.json'
DEFAULT_OUTPUT_DIR = ROOT / 'validation' / 'latest' / 'chatgpt-first-proof-schema-validation'
VALIDATION_SCHEMA_VERSION = 1


def utcnow() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')


def _error_path(parts: Any) -> str:
    parts_list = list(parts)
    if not parts_list:
        return '$'
    out = '$'
    for part in parts_list:
        if isinstance(part, int):
            out += f'[{part}]'
        else:
            out += f'.{part}'
    return out


def validate_payload(payload: Any, schema: dict[str, Any]) -> dict[str, Any]:
    try:
        from jsonschema import Draft202012Validator
    except Exception as exc:  # pragma: no cover - depends on environment
        return {
            'ok': False,
            'validator_available': False,
            'validator_error': str(exc),
            'error_count': 1,
            'errors': [{'path': '$', 'schema_path': '$', 'message': 'jsonschema package is not available', 'validator': 'import'}],
        }

    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(payload), key=lambda err: (list(err.path), list(err.schema_path), err.message))
    rows = [
        {
            'path': _error_path(error.path),
            'schema_path': _error_path(error.schema_path),
            'message': error.message,
            'validator': error.validator,
        }
        for error in errors
    ]
    return {
        'ok': not rows,
        'validator_available': True,
        'validator': 'jsonschema.Draft202012Validator',
        'error_count': len(rows),
        'errors': rows,
    }


def validate_file(input_path: Path = DEFAULT_INPUT, *, schema_path: Path = DEFAULT_SCHEMA, output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, Any]:
    input_path = input_path.resolve()
    schema_path = schema_path.resolve()
    payload = read_json(input_path)
    schema = read_json(schema_path)
    result = validate_payload(payload, schema if isinstance(schema, dict) else {})
    report = {
        'schema_version': VALIDATION_SCHEMA_VERSION,
        'validation_key': 'chatgpt-first-proof-bundle-schema-validation',
        'generated_at': utcnow(),
        'project': 'GlassTTY',
        'surface_key': 'chatgpt',
        'input_path': str(input_path),
        'input_sha256': sha256_file(input_path),
        'schema_path': str(schema_path),
        'schema_sha256': sha256_file(schema_path),
        'schema_id': schema.get('$id') if isinstance(schema, dict) else None,
        'ok': result.get('ok'),
        'validator_available': result.get('validator_available'),
        'validator': result.get('validator'),
        'error_count': result.get('error_count'),
        'errors': result.get('errors'),
        'support_claim_effect': 'none; schema validation is local structural evidence and never widens support claims',
        'operator_notes': [
            'This structural check is necessary but not sufficient for proof acceptance.',
            'Run the artifact ledger before schema validation when material capture slots may be missing.',
            'Run the bundle audit and schema v20 evaluator after this structural check passes.',
        ],
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    write_json(output_dir / 'bundle-schema-validation.json', report)
    (output_dir / 'SUMMARY.md').write_text(summary_markdown(report), encoding='utf-8')
    return report


def summary_markdown(report: dict[str, Any]) -> str:
    lines = [
        '# ChatGPT first-proof bundle schema validation',
        '',
        f"- generated_at: `{report.get('generated_at')}`",
        f"- input: `{report.get('input_path')}`",
        f"- input_sha256: `{report.get('input_sha256')}`",
        f"- schema: `{report.get('schema_path')}`",
        f"- schema_sha256: `{report.get('schema_sha256')}`",
        f"- ok: `{report.get('ok')}`",
        f"- error_count: `{report.get('error_count')}`",
        '',
        '## Errors',
        '',
    ]
    errors = report.get('errors') or []
    if not errors:
        lines.append('- none')
    else:
        for error in errors:
            lines.append(f"- `{error.get('path')}`: {error.get('message')} ({error.get('validator')})")
    lines.extend(['', '## Operator notes', ''])
    for note in report.get('operator_notes') or []:
        lines.append(f'- {note}')
    return '\n'.join(lines) + '\n'


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Validate a ChatGPT first-proof bundle against its canonical JSON Schema.')
    sub = parser.add_subparsers(dest='command')
    validate_cmd = sub.add_parser('validate', help='Validate bundle-manifest.json against the schema')
    validate_cmd.add_argument('--input', type=Path, default=DEFAULT_INPUT)
    validate_cmd.add_argument('--schema', type=Path, default=DEFAULT_SCHEMA)
    validate_cmd.add_argument('--output-dir', type=Path, default=DEFAULT_OUTPUT_DIR)
    validate_cmd.add_argument('--pretty', action='store_true')
    validate_cmd.add_argument('--require-ok', action='store_true', help='Exit nonzero unless the schema validation passes')
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command in (None, 'validate'):
        report = validate_file(
            getattr(args, 'input', DEFAULT_INPUT),
            schema_path=getattr(args, 'schema', DEFAULT_SCHEMA),
            output_dir=getattr(args, 'output_dir', DEFAULT_OUTPUT_DIR),
        )
        print(json.dumps(report, indent=2 if getattr(args, 'pretty', False) else None))
        if getattr(args, 'require_ok', False) and not report.get('ok'):
            return 1
        return 0
    parser.error(f'unknown command {args.command}')
    return 2


if __name__ == '__main__':
    raise SystemExit(main())
