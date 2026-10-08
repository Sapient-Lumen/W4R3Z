#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path
import jsonschema
ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / 'schemas' / 'cooperation_benchmark_card.schema.json'
EXAMPLE_PATH = ROOT / 'examples' / 'snapshots' / 'cooperation_benchmark_card_example.json'
def fail(msg: str) -> int:
    print(f'cooperation-benchmark-card: {msg}', file=sys.stderr)
    return 1

def load_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))

def main() -> int:
    schema = load_json(SCHEMA_PATH)
    example = load_json(EXAMPLE_PATH)
    if schema.get('title') != 'Cooperation Benchmark Card':
        return fail('schema title mismatch')
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(example, schema)
    if example.get('schema_version') != 1:
        return fail('expected schema_version == 1')
    if example.get('result_kind') != 'comparative':
        return fail('expected comparative example')
    lane = example.get('lane_contract', {})
    if 'not applicable' not in lane.get('human_lane_type_proxy_provenance_and_real_human_escalation_status', '').lower():
        return fail('expected worked example to demonstrate explicit not applicable handling')
    print('cooperation-benchmark-card: ok')
    print(f'cooperation-benchmark-card: validated {EXAMPLE_PATH.relative_to(ROOT)} against {SCHEMA_PATH.relative_to(ROOT)}')
    return 0
if __name__ == '__main__':
    raise SystemExit(main())
