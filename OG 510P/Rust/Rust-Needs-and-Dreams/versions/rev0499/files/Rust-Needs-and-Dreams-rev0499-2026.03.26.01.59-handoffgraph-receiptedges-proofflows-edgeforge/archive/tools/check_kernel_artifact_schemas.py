#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / 'schemas' / 'top-band-v0'
HYG = SCHEMA_DIR / 'schema-pack-hygiene-checks.json'
REQUIRED_FILES = [ROOT / 'schemas' / 'README.md', SCHEMA_DIR / 'README.md', HYG]

def schema_filename_for_family(family: str) -> str:
    return family.split('/')[0] + '.schema.json'

def main() -> int:
    errors: list[str] = []
    for path in REQUIRED_FILES:
        if not path.exists():
            errors.append(f'missing required schema asset: {path.relative_to(ROOT)}')
    if errors:
        print('Kernel artifact schema check FAILED', file=sys.stderr)
        for err in errors: print(f'- {err}', file=sys.stderr)
        return 1
    try:
        hyg = json.loads(HYG.read_text(encoding='utf-8'))
    except Exception as exc:
        print('Kernel artifact schema check FAILED', file=sys.stderr)
        print(f'- failed to parse {HYG.relative_to(ROOT)}: {exc}', file=sys.stderr)
        return 1
    if hyg.get('schema_family') != 'kernel-artifact-schema-hygiene/v0':
        errors.append('schema-pack hygiene schema_family must be kernel-artifact-schema-hygiene/v0')
    families = hyg.get('required_schema_families', [])
    if not isinstance(families, list) or not families:
        errors.append('required_schema_families must be a non-empty list')
        families = []
    family_to_specimens = hyg.get('family_to_specimens', {})
    if not isinstance(family_to_specimens, dict):
        errors.append('family_to_specimens must be an object')
        family_to_specimens = {}
    validators = {}
    for family in families:
        if not isinstance(family, str) or not family.strip():
            errors.append('schema family entries must be non-empty strings'); continue
        schema_path = SCHEMA_DIR / schema_filename_for_family(family)
        if not schema_path.exists():
            errors.append(f'missing schema file for family {family}: {schema_path.relative_to(ROOT)}'); continue
        try:
            schema = json.loads(schema_path.read_text(encoding='utf-8'))
            Draft202012Validator.check_schema(schema)
            validators[family] = Draft202012Validator(schema)
        except Exception as exc:
            errors.append(f'failed to load/validate schema {schema_path.relative_to(ROOT)}: {exc}')
    for family in families:
        specimen_paths = family_to_specimens.get(family)
        if not isinstance(specimen_paths, list) or not specimen_paths:
            errors.append(f'missing specimen bindings for schema family {family}'); continue
        validator = validators.get(family)
        for rel in specimen_paths:
            if not isinstance(rel, str) or not rel.strip():
                errors.append(f'{family} has non-string specimen binding'); continue
            specimen = ROOT / rel
            if not specimen.exists():
                errors.append(f'{family} specimen file does not exist: {rel}'); continue
            try:
                payload = json.loads(specimen.read_text(encoding='utf-8'))
            except Exception as exc:
                errors.append(f'failed to parse specimen {rel}: {exc}'); continue
            if payload.get('schema_family') != family:
                errors.append(f'{rel} declares schema_family {payload.get("schema_family")!r}, expected {family!r}')
            if validator is not None:
                errs=list(validator.iter_errors(payload))
                if errs:
                    errors.append(f'{rel} failed schema validation: {errs[0].message}')
    if errors:
        print('Kernel artifact schema check FAILED', file=sys.stderr)
        for err in errors: print(f'- {err}', file=sys.stderr)
        return 1
    print('Kernel artifact schema check passed')
    print(f'Validated {len(families)} schema families and their bound specimen payloads.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
