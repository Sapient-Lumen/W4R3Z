#!/usr/bin/env python3
"""Validate compact machine-readable archive surfaces against explicit JSON Schemas."""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

from jsonschema import Draft202012Validator

SCHEMA_TARGETS = [
    ('RELEASE_MANIFEST.json', 'schemas/release_manifest.schema.json'),
    ('REVISION_RECEIPT.json', 'schemas/revision_receipt.schema.json'),
    ('ARCHIVE_INDEX.json', 'schemas/archive_index.schema.json'),
    ('CONTEXT_PACK.json', 'schemas/context_pack.schema.json'),
    ('publishing/control_surfaces.json', 'schemas/control_surfaces.schema.json'),
    ('release_queue/QUEUE_INDEX.json', 'schemas/queue_index.schema.json'),
    ('release_queue/LATEST_DECISION.json', 'schemas/latest_decision.schema.json'),
    ('release_queue/DECISION_INDEX.json', 'schemas/decision_index.schema.json'),
    ('published/citation_heads.json', 'schemas/citation_heads.schema.json'),
    ('published/PUBLIC_SURFACE.json', 'schemas/public_surface.schema.json'),
    ('publishing/archive_invariants.json', 'schemas/archive_invariants.schema.json'),
    ('TRANSFER_SOURCES.json', 'schemas/transfer_sources.schema.json'),
    ('ASSURANCE_ARTIFACTS.json', 'schemas/assurance_artifacts.schema.json'),
    ('publishing/archive_budget_policy.json', 'schemas/archive_budget_policy.schema.json'),
]


def load_json(path: pathlib.Path):
    return json.loads(path.read_text(encoding='utf-8'))


def check(root: pathlib.Path) -> dict:
    checks = []
    for target_rel, schema_rel in SCHEMA_TARGETS:
        target = root / target_rel
        schema_path = root / schema_rel
        try:
            schema = load_json(schema_path)
            instance = load_json(target)
            validator = Draft202012Validator(schema)
            errors = sorted(validator.iter_errors(instance), key=lambda e: list(e.absolute_path))
            checks.append({
                'target': target_rel,
                'schema': schema_rel,
                'status': 'pass' if not errors else 'fail',
                'error_count': len(errors),
                'errors': [
                    {
                        'path': '/'.join(str(p) for p in err.absolute_path),
                        'message': err.message,
                    }
                    for err in errors[:20]
                ],
            })
        except FileNotFoundError as exc:
            checks.append({'target': target_rel, 'schema': schema_rel, 'status': 'fail', 'error_count': 1, 'errors': [{'path': '', 'message': str(exc)}]})
        except Exception as exc:
            checks.append({'target': target_rel, 'schema': schema_rel, 'status': 'fail', 'error_count': 1, 'errors': [{'path': '', 'message': str(exc)}]})

    failures = [c for c in checks if c['status'] == 'fail']
    return {
        'status': 'pass' if not failures else 'fail',
        'checked_targets': len(checks),
        'checks': checks,
        'summary': {
            'checks_passed': len(checks) - len(failures),
            'checks_failed': len(failures),
        },
        'fail_closed_rule': 'If schema validation fails, default to no publication and repair malformed machine-readable surfaces before trusting them.'
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', default='.')
    parser.add_argument('--write-report', default='')
    args = parser.parse_args()

    root = pathlib.Path(args.root).resolve()
    report = check(root)
    text = json.dumps(report, indent=2) + "\n"
    if args.write_report:
        out = (root / args.write_report).resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding='utf-8')
    sys.stdout.write(text)
    return 0 if report['status'] == 'pass' else 1


if __name__ == '__main__':
    raise SystemExit(main())
