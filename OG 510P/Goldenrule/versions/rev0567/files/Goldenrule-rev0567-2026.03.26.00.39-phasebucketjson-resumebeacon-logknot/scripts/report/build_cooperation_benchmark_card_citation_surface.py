#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import jsonschema


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'unable to load module {name} from {path}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ROOT = Path(__file__).resolve().parents[2]
INVENTORY_BUILDER = ROOT / 'scripts' / 'report' / 'build_cooperation_benchmark_card_inventory.py'
HEADS_BUILDER = ROOT / 'scripts' / 'report' / 'build_cooperation_benchmark_card_heads.py'
FREEZE_SCHEMA_PATH = ROOT / 'schemas' / 'cooperation_benchmark_card_freeze_receipt.schema.json'
SCHEMA_PATH = ROOT / 'schemas' / 'cooperation_benchmark_card_citation_surface.schema.json'
inventory_builder = load_module('cooperation_benchmark_card_inventory_builder', INVENTORY_BUILDER)
heads_builder = load_module('cooperation_benchmark_card_heads_builder', HEADS_BUILDER)

TITLE = '# Cooperation Benchmark Card Citation Surface'
SUBTITLE = (
    'Generated fail-closed citation surface over compact cooperation-card lineages. '
    'Only unique citation heads with exactly one verified freeze receipt and a fully verified retained delta basis appear here.'
)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def lineage_basis_reason_codes(
    citation_head_id: str,
    cards_by_id: dict[str, dict[str, Any]],
    verified_delta_by_new_card_id: dict[str, list[dict[str, Any]]],
    all_delta_by_new_card_id: dict[str, list[dict[str, Any]]],
) -> list[str]:
    reasons: list[str] = []
    seen: set[str] = set()
    current_id = citation_head_id
    while True:
        if current_id in seen:
            reasons.append('lineage-basis-cycle')
            break
        seen.add(current_id)
        current = cards_by_id[current_id]
        predecessors = current['predecessor_card_ids']
        if not predecessors:
            break
        if len(predecessors) != 1:
            reasons.append('ambiguous-lineage-basis')
            break
        verified = verified_delta_by_new_card_id.get(current_id, [])
        all_receipts = all_delta_by_new_card_id.get(current_id, [])
        if len(verified) == 1:
            current_id = predecessors[0]
            continue
        if len(verified) > 1:
            reasons.append('multiple-verified-delta-receipts')
            break
        if all_receipts:
            reasons.append('citation-basis-drift')
        else:
            reasons.append('missing-lineage-delta-receipt')
        break
    return sorted(set(reasons))


def collect() -> dict[str, Any]:
    inventory = inventory_builder.collect()
    heads = heads_builder.collect()
    freeze_schema = load_json(FREEZE_SCHEMA_PATH)
    surface_schema = load_json(SCHEMA_PATH)
    for schema in [freeze_schema, surface_schema]:
        jsonschema.Draft202012Validator.check_schema(schema)

    cards_by_id = {row['id']: row for row in inventory['cards']}
    verified_receipts_by_card_id: dict[str, list[dict[str, Any]]] = {}
    verified_delta_by_new_card_id: dict[str, list[dict[str, Any]]] = {}
    all_delta_by_new_card_id: dict[str, list[dict[str, Any]]] = {}
    for receipt in inventory['freeze_receipts']:
        if not receipt.get('matches_current_surface'):
            continue
        payload = load_json(ROOT / receipt['path'])
        jsonschema.validate(payload, freeze_schema)
        verified_receipts_by_card_id.setdefault(receipt['card_id'], []).append(payload)
    for receipt in inventory['delta_receipts']:
        all_delta_by_new_card_id.setdefault(receipt['new_card_id'], []).append(receipt)
        if receipt.get('matches_current_surface'):
            verified_delta_by_new_card_id.setdefault(receipt['new_card_id'], []).append(receipt)

    entries: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []

    for lineage in heads['lineages']:
        reason_codes = list(lineage.get('warning_reason_codes', []))
        citation_head_id = lineage.get('unique_citation_head_id')
        if citation_head_id is None or reason_codes:
            unresolved.append(
                {
                    'lineage_id': lineage['lineage_id'],
                    'reason_codes': reason_codes or ['no-unique-citation-head'],
                    'operational_head_card_ids': lineage['operational_head_card_ids'],
                    'citation_head_card_ids': lineage['citation_head_card_ids'],
                    'card_paths': lineage['card_paths'],
                }
            )
            continue
        basis_reasons = lineage_basis_reason_codes(citation_head_id, cards_by_id, verified_delta_by_new_card_id, all_delta_by_new_card_id)
        if basis_reasons:
            unresolved.append(
                {
                    'lineage_id': lineage['lineage_id'],
                    'reason_codes': basis_reasons,
                    'operational_head_card_ids': lineage['operational_head_card_ids'],
                    'citation_head_card_ids': lineage['citation_head_card_ids'],
                    'card_paths': lineage['card_paths'],
                }
            )
            continue
        receipts = verified_receipts_by_card_id.get(citation_head_id, [])
        if len(receipts) != 1:
            unresolved.append(
                {
                    'lineage_id': lineage['lineage_id'],
                    'reason_codes': sorted(set(reason_codes + ['multiple-verified-freeze-receipts'] if len(receipts) > 1 else reason_codes + ['missing-verified-freeze-receipt'])),
                    'operational_head_card_ids': lineage['operational_head_card_ids'],
                    'citation_head_card_ids': lineage['citation_head_card_ids'],
                    'card_paths': lineage['card_paths'],
                }
            )
            continue
        receipt = receipts[0]
        card = cards_by_id[citation_head_id]
        entries.append(
            {
                'lineage_id': lineage['lineage_id'],
                'benchmark_name': receipt['benchmark_name'],
                'card_id': citation_head_id,
                'card_path': card['path'],
                'rendered_markdown_path': receipt['rendered_markdown_path'],
                'freeze_receipt_path': next(
                    receipt_row['path']
                    for receipt_row in inventory['freeze_receipts']
                    if receipt_row['card_id'] == citation_head_id and receipt_row.get('matches_current_surface')
                ),
                'card_sha256': receipt['card_sha256'],
                'rendered_markdown_sha256': receipt['rendered_markdown_sha256'],
                'card_schema_path': receipt['card_schema_path'],
                'card_schema_sha256': receipt['card_schema_sha256'],
                'freeze_tool_path': receipt['freeze_tool_path'],
                'freeze_tool_sha256': receipt['freeze_tool_sha256'],
            }
        )

    entries.sort(key=lambda row: row['lineage_id'])
    unresolved.sort(key=lambda row: row['lineage_id'])
    data = {
        'surface_kind': 'cooperation_benchmark_card_citation_surface',
        'inventory_kind': inventory['card_inventory_kind'],
        'heads_register_kind': heads['register_kind'],
        'counts': {
            'lineage_count': len(heads['lineages']),
            'citation_lineage_count': len(entries),
            'unresolved_lineage_count': len(unresolved),
            'citation_entry_count': len(entries),
        },
        'entries': entries,
        'unresolved_lineages': unresolved,
    }
    jsonschema.validate(data, surface_schema)
    return data


def render(data: dict[str, Any]) -> str:
    counts = data['counts']
    lines = [
        TITLE,
        '',
        SUBTITLE,
        '',
        f"- lineage_count: {counts['lineage_count']}",
        f"- citation_lineage_count: {counts['citation_lineage_count']}",
        f"- unresolved_lineage_count: {counts['unresolved_lineage_count']}",
        f"- citation_entry_count: {counts['citation_entry_count']}",
        '',
    ]
    if data['entries']:
        lines.extend([
            '## Citation entries',
            '',
            '| lineage_id | card_id | benchmark_name | freeze_receipt_path | rendered_markdown_path |',
            '|---|---|---|---|---|',
        ])
        for row in data['entries']:
            lines.append(
                f"| `{row['lineage_id']}` | `{row['card_id']}` | {row['benchmark_name']} | `{row['freeze_receipt_path']}` | `{row['rendered_markdown_path']}` |"
            )
        lines.append('')
    else:
        lines.extend(['No compact-card citation entries are currently admissible.', ''])

    if data['unresolved_lineages']:
        lines.extend([
            '## Unresolved lineages',
            '',
            '| lineage_id | reason_codes | operational_heads | citation_heads |',
            '|---|---|---|---|',
        ])
        for row in data['unresolved_lineages']:
            lines.append(
                f"| `{row['lineage_id']}` | {', '.join('`' + code + '`' for code in row['reason_codes'])} | "
                f"{', '.join('`' + item + '`' for item in row['operational_head_card_ids']) or '—'} | "
                f"{', '.join('`' + item + '`' for item in row['citation_head_card_ids']) or '—'} |"
            )
        lines.append('')
    return '\n'.join(lines)


def main() -> int:
    write = '--write' in sys.argv
    data = collect()
    out_json = ROOT / 'artifacts' / 'reports' / 'cooperation_benchmark_card_citation_surface.json'
    out_md = ROOT / 'docs' / 'COOPERATION_BENCHMARK_CARD_CITATION_SURFACE.md'
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(data, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    expected_md = render(data) + '\n'
    if write or not out_md.exists():
        out_md.write_text(expected_md, encoding='utf-8')
        print(f'cooperation-benchmark-card-citation-surface: wrote {out_md}')
        print(f'cooperation-benchmark-card-citation-surface: wrote {out_json}')
        return 0
    current_md = out_md.read_text(encoding='utf-8')
    if current_md != expected_md:
        print('cooperation-benchmark-card-citation-surface: drift detected; run with --write', file=sys.stderr)
        return 1
    print(f"cooperation-benchmark-card-citation-surface: ok ({data['counts']['citation_entry_count']} entries)")
    print(f'cooperation-benchmark-card-citation-surface: wrote {out_json}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
