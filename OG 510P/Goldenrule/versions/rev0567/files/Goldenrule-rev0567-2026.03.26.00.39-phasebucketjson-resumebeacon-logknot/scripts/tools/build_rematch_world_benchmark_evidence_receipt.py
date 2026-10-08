#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PACKET = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_evidence_packet.json'
PACKET_SCHEMA_PATH = ROOT / 'schemas' / 'rematch_world_benchmark_evidence_packet.schema.json'
RECEIPT_SCHEMA_PATH = ROOT / 'schemas' / 'rematch_world_benchmark_evidence_receipt.schema.json'
EXPECTED_SECTIONS = [
    'world_semantics_contract',
    'matching_state_contract',
    'occupancy_accounting_contract',
    'turnover_tempo_contract',
    'paired_ranking_views_contract',
]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def _sha256_bytes(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def _sha256_json(node: Any) -> str:
    return _sha256_bytes(json.dumps(node, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8'))


def _relativize(path: Path) -> str:
    resolved = path.resolve()
    return resolved.relative_to(ROOT).as_posix() if resolved.is_relative_to(ROOT) else str(path)


def _parse_source_arg(raw: str) -> tuple[str, Path]:
    if '=' not in raw:
        raise ValueError(f'expected LABEL=PATH, got {raw!r}')
    label, path_str = raw.split('=', 1)
    label = label.strip()
    if not label:
        raise ValueError(f'empty label in {raw!r}')
    path = Path(path_str)
    if not path.is_absolute():
        path = (ROOT / path).resolve()
    return label, path


def _parse_coverage_arg(raw: str) -> tuple[str, list[str]]:
    if '=' not in raw:
        raise ValueError(f'expected LABEL=section1,section2, got {raw!r}')
    label, section_blob = raw.split('=', 1)
    sections = [part.strip() for part in section_blob.split(',') if part.strip()]
    if not label.strip() or not sections:
        raise ValueError(f'invalid coverage spec {raw!r}')
    unknown = sorted(set(sections) - set(EXPECTED_SECTIONS))
    if unknown:
        raise ValueError(f'unknown covered sections for {label!r}: {unknown}')
    return label.strip(), sections


def build_receipt(packet: dict[str, Any], packet_path: Path, source_rows: list[dict[str, Any]]) -> dict[str, Any]:
    coverage_sections = sorted({section for row in source_rows for section in row['covered_sections']})
    missing_sections = sorted(set(EXPECTED_SECTIONS) - set(coverage_sections))
    packet_bytes = len(packet_path.read_bytes())
    return {
        'coverage_sections': coverage_sections,
        'missing_sections': missing_sections,
        'packet_bytes': packet_bytes,
        'packet_path': _relativize(packet_path),
        'packet_sha256': _sha256_json(packet),
        'receipt_intent': 'retain one compact provenance receipt tying the distilled evidence packet to scratch-only source files before those wider scratch traces are dropped',
        'receipt_version': '2026-03-17.rematch_world_benchmark_evidence_receipt.v1',
        'scratch_source_count': len(source_rows),
        'scratch_sources': source_rows,
        'scratch_total_bytes': sum(int(row['byte_count']) for row in source_rows),
        'source_run_label': packet['source_run_label'],
        'strict_coverage_passed': not missing_sections,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Build a compact evidence receipt that hashes scratch-only sources behind a rematch-world evidence packet.')
    parser.add_argument('packet', nargs='?', default=str(DEFAULT_PACKET), help='Path to the rematch-world evidence packet JSON.')
    parser.add_argument('--scratch-source', action='append', default=[], help='Scratch source as LABEL=PATH. May be repeated.')
    parser.add_argument('--coverage', action='append', default=[], help='Coverage declaration as LABEL=section1,section2. May be repeated.')
    parser.add_argument('--output', help='Write the receipt JSON to this path instead of stdout.')
    parser.add_argument('--strict-coverage', action='store_true', help='Exit nonzero unless all expected benchmark sections are covered.')
    parser.add_argument('--summary-json', action='store_true', help='Emit a compact summary instead of the full receipt.')
    args = parser.parse_args()

    if not args.scratch_source:
        raise SystemExit('rematch-world-benchmark-evidence-receipt: provide at least one --scratch-source LABEL=PATH')

    packet_path = Path(args.packet)
    if not packet_path.is_absolute():
        packet_path = (ROOT / packet_path).resolve()
    packet = load_json(packet_path)
    packet_schema = load_json(PACKET_SCHEMA_PATH)
    receipt_schema = load_json(RECEIPT_SCHEMA_PATH)
    jsonschema.Draft202012Validator.check_schema(packet_schema)
    jsonschema.Draft202012Validator.check_schema(receipt_schema)
    jsonschema.validate(packet, packet_schema)

    coverage_by_label: dict[str, list[str]] = {}
    for raw in args.coverage:
        label, sections = _parse_coverage_arg(raw)
        coverage_by_label[label] = sections

    source_rows: list[dict[str, Any]] = []
    for raw in args.scratch_source:
        label, path = _parse_source_arg(raw)
        if not path.exists() or not path.is_file():
            raise SystemExit(f'rematch-world-benchmark-evidence-receipt: missing scratch source {path}')
        if label not in coverage_by_label:
            raise SystemExit(f'rematch-world-benchmark-evidence-receipt: missing --coverage for label {label!r}')
        blob = path.read_bytes()
        source_rows.append(
            {
                'byte_count': len(blob),
                'covered_sections': sorted(set(coverage_by_label[label])),
                'label': label,
                'scratch_path': _relativize(path),
                'sha256': _sha256_bytes(blob),
            }
        )

    receipt = build_receipt(packet, packet_path, source_rows)
    jsonschema.validate(receipt, receipt_schema)

    if args.strict_coverage and not receipt['strict_coverage_passed']:
        print(json.dumps(receipt, indent=2, sort_keys=True))
        return 1

    if args.summary_json:
        summary = {
            'coverage_sections': receipt['coverage_sections'],
            'missing_sections': receipt['missing_sections'],
            'packet_bytes': receipt['packet_bytes'],
            'scratch_source_count': receipt['scratch_source_count'],
            'scratch_total_bytes': receipt['scratch_total_bytes'],
            'strict_coverage_passed': receipt['strict_coverage_passed'],
        }
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0

    rendered = json.dumps(receipt, indent=2, sort_keys=True) + '\n'
    if args.output:
        output_path = Path(args.output)
        if not output_path.is_absolute():
            output_path = (ROOT / output_path).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered, encoding='utf-8')
        print(
            'rematch-world-benchmark-evidence-receipt: '
            f'wrote {_relativize(output_path)} ({receipt["scratch_source_count"]} sources, '
            f'{receipt["scratch_total_bytes"]} scratch bytes, '
            f'strict_coverage_passed={str(receipt["strict_coverage_passed"]).lower()})'
        )
        return 0

    print(rendered, end='')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
