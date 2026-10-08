#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, List

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures" / "cargo-report-pack-kit"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def schema_id_from_filename(name: str) -> str:
    return name.removesuffix('.schema.json')


def control_surface_names() -> set[str]:
    names = set()
    for name in [
        'cargo-report-taxonomy.json',
        'cargo-report-scenario-index.json',
        'cargo-report-review-gates.json',
        'cargo-report-hygiene-checks.json',
    ]:
        names.add(name.removesuffix('.json'))
    return names


def schema_names() -> set[str]:
    return {schema_id_from_filename(p.name) for p in FIXTURES.glob('*.schema.json')}


def example_schema_map(hygiene: dict) -> Dict[Path, Path]:
    mapping: Dict[Path, Path] = {}
    overrides = {
        Path(k): FIXTURES / v for k, v in hygiene.get('example_schema_overrides', {}).items()
    }
    for example in FIXTURES.glob('*/*.example.json'):
        rel = example.relative_to(FIXTURES)
        if rel in overrides:
            mapping[example] = overrides[rel]
            continue
        schema_name = example.name.replace('.example.json', '.schema.json')
        schema_path = FIXTURES / schema_name
        if not schema_path.exists():
            raise AssertionError(f'No schema found for example {rel}')
        mapping[example] = schema_path
    return mapping


def check_revision_stamps(hygiene: dict) -> List[str]:
    errors = []
    expected = hygiene['revision']
    for filename in [
        'cargo-report-taxonomy.json',
        'cargo-report-scenario-index.json',
        'cargo-report-review-gates.json',
        'cargo-report-hygiene-checks.json',
    ]:
        data = load_json(FIXTURES / filename)
        if data.get('revision') != expected:
            errors.append(f'{filename} revision {data.get("revision")} != {expected}')
    return errors


def check_scenario_directories(hygiene: dict, scenario_index: dict) -> List[str]:
    errors = []
    required = hygiene.get('required_scenario_files', [])
    seen_dirs = set()
    for scenario in scenario_index['scenarios']:
        scenario_dir = FIXTURES / scenario['directory']
        seen_dirs.add(scenario_dir.name)
        if not scenario_dir.is_dir():
            errors.append(f'missing scenario directory: {scenario["directory"]}')
            continue
        for req in required:
            if not (scenario_dir / req).exists():
                errors.append(f'missing {req} in scenario {scenario["directory"]}')
    for child in FIXTURES.iterdir():
        if child.is_dir() and child.name not in seen_dirs:
            errors.append(f'unindexed scenario directory: {child.name}')
    return errors


def check_taxonomy_usage(taxonomy: dict, scenario_index: dict) -> List[str]:
    errors = []
    classes = taxonomy['classes']
    for scenario in scenario_index['scenarios']:
        covers = scenario.get('covers', {})
        for class_name, values in covers.items():
            if class_name not in classes:
                errors.append(f'scenario {scenario["scenario_id"]} uses unknown class {class_name}')
                continue
            allowed = set(classes[class_name])
            for value in values:
                if value not in allowed:
                    errors.append(
                        f'scenario {scenario["scenario_id"]} uses unregistered {class_name} value {value}'
                    )
    return errors


def check_gate_artifact_refs(review_gates: dict, hygiene: dict) -> List[str]:
    errors = []
    known = schema_names() | set(hygiene.get('control_surfaces', []))
    for gate in review_gates['gates']:
        for artifact in gate.get('required_artifacts', []):
            if artifact not in known:
                errors.append(f'gate {gate["gate_id"]} references unknown artifact {artifact}')
    return errors


def check_examples_validate(hygiene: dict) -> List[str]:
    errors = []
    for example_path, schema_path in example_schema_map(hygiene).items():
        example = load_json(example_path)
        schema = load_json(schema_path)
        validator = Draft202012Validator(schema)
        for error in validator.iter_errors(example):
            loc = '/'.join(str(part) for part in error.absolute_path) or '<root>'
            errors.append(
                f'{example_path.relative_to(FIXTURES)} invalid against {schema_path.name} at {loc}: {error.message}'
            )
    return errors



def check_head_guard_coverage(scenario_index: dict, example_map: Dict[Path, Path]) -> List[str]:
    errors = []
    covered = set()
    for scenario in scenario_index['scenarios']:
        for value in scenario.get('covers', {}).get('head_guard_status', []):
            covered.add(value)
    for needed in ['matched-head', 'reissue-required']:
        if needed not in covered:
            errors.append(f'missing scenario coverage for head_guard_status {needed}')

    for example_path in example_map:
        if example_path.name == 'cargo-report-review-request.example.json':
            data = load_json(example_path)
            for field in ['expected_head_ref', 'head_lineage_ref', 'head_guard_status']:
                if field not in data:
                    errors.append(f'{example_path.relative_to(FIXTURES)} missing {field}')
        if example_path.name == 'cargo-report-decision-witness.example.json':
            data = load_json(example_path)
            for field in ['reviewed_head_ref', 'head_guard_status']:
                if field not in data:
                    errors.append(f'{example_path.relative_to(FIXTURES)} missing {field}')
    return errors

def check_review_separation_coverage(scenario_index: dict, example_map: Dict[Path, Path]) -> List[str]:
    errors = []
    covered = set()
    for scenario in scenario_index['scenarios']:
        for value in scenario.get('covers', {}).get('review_separation_class', []):
            covered.add(value)
    for needed in ['independent-checker', 'self-review']:
        if needed not in covered:
            errors.append(f'missing scenario coverage for review_separation_class {needed}')

    for example_path in example_map:
        data = load_json(example_path)
        if example_path.name == 'cargo-report-review-request.example.json':
            if 'review_separation_ref' not in data:
                errors.append(f'{example_path.relative_to(FIXTURES)} missing review_separation_ref')
        if example_path.name == 'cargo-report-decision-witness.example.json':
            if 'review_separation_ref' not in data:
                errors.append(f'{example_path.relative_to(FIXTURES)} missing review_separation_ref')
        if example_path.name == 'cargo-report-review-separation-receipt.example.json':
            for field in ['proposer', 'reviewer', 'executor', 'review_separation_class', 'compensating_control_class']:
                if field not in data:
                    errors.append(f'{example_path.relative_to(FIXTURES)} missing {field}')
    return errors

def main() -> int:
    hygiene = load_json(FIXTURES / 'cargo-report-hygiene-checks.json')
    taxonomy = load_json(FIXTURES / 'cargo-report-taxonomy.json')
    scenario_index = load_json(FIXTURES / 'cargo-report-scenario-index.json')
    review_gates = load_json(FIXTURES / 'cargo-report-review-gates.json')

    errors: List[str] = []
    errors.extend(check_revision_stamps(hygiene))
    errors.extend(check_scenario_directories(hygiene, scenario_index))
    errors.extend(check_taxonomy_usage(taxonomy, scenario_index))
    errors.extend(check_gate_artifact_refs(review_gates, hygiene))
    mapping = example_schema_map(hygiene)
    errors.extend(check_examples_validate(hygiene))
    errors.extend(check_head_guard_coverage(scenario_index, mapping))
    errors.extend(check_review_separation_coverage(scenario_index, mapping))

    if errors:
        print('Cargo Report Kit contract check FAILED', file=sys.stderr)
        for err in errors:
            print(f'- {err}', file=sys.stderr)
        return 1

    print('Cargo Report Kit contract check passed')
    print(f'Validated {len(list(FIXTURES.glob("*/*.example.json")))} example files, {len(scenario_index["scenarios"])} scenarios, and {len(review_gates["gates"])} review gates, including review-head guard coverage and review-separation coverage.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
