#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / 'schemas' / 'cooperation_benchmark_card.schema.json'
EXAMPLE_JSON = ROOT / 'examples' / 'snapshots' / 'cooperation_benchmark_card_example.json'
EXAMPLE_MD = ROOT / 'examples' / 'snapshots' / 'cooperation_benchmark_card_example.md'
TOOL = ROOT / 'scripts' / 'tools' / 'cooperation_benchmark_card.py'


def fail(msg: str) -> int:
    print(f'cooperation-benchmark-card-tooling: {msg}', file=sys.stderr)
    return 1


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=False)


def load_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def main() -> int:
    schema = load_json(SCHEMA_PATH)
    example = load_json(EXAMPLE_JSON)
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(example, schema)

    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        scaffold_path = tmpdir / 'scaffold.json'
        rendered_path = tmpdir / 'rendered.md'
        scaffold = run(
            'python3', str(TOOL), 'scaffold',
            '--id', 'scaffold-example',
            '--benchmark-name', 'Scaffold Example Benchmark',
            '--output', str(scaffold_path),
        )
        if scaffold.returncode != 0:
            return fail(f'scaffold command failed: {scaffold.stderr.strip()}')
        scaffold_obj = load_json(scaffold_path)
        jsonschema.validate(scaffold_obj, schema)
        if 'not applicable' not in scaffold_obj['notes'].lower():
            return fail('scaffold notes should mention explicit not applicable handling')

        rendered = run('python3', str(TOOL), 'render', str(EXAMPLE_JSON), '--output', str(rendered_path))
        if rendered.returncode != 0:
            return fail(f'render command failed: {rendered.stderr.strip()}')
        expected = EXAMPLE_MD.read_text(encoding='utf-8')
        actual = rendered_path.read_text(encoding='utf-8')
        if actual != expected:
            return fail('rendered example markdown drift detected; regenerate snapshot via the tooling script')
        if '## Lane contract' not in actual or '## Adjudication' not in actual:
            return fail('rendered markdown missing expected section headings')

    print('cooperation-benchmark-card-tooling: ok')
    print(f'cooperation-benchmark-card-tooling: validated {TOOL.relative_to(ROOT)} against schema and rendered snapshot')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
