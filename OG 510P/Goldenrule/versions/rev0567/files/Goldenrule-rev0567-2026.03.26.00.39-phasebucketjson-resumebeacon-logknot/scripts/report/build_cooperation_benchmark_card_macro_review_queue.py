#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import jsonschema


ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / 'schemas' / 'cooperation_benchmark_card_macro_review_queue.schema.json'

TITLE = '# Cooperation Benchmark Card Macro Review Queue'
SUBTITLE = (
    'Generated lineage-grouped review surface for compact cooperation benchmark cards. '
    'This keeps all currently actionable review items for one lineage together so inheritors '
    'do not have to reconstruct repair work from a flat queue.'
)

KIND_PRIORITY = {
    'delta_drift': 0,
    'freeze_drift': 1,
    'freeze_needed': 2,
    'topology_review': 3,
    'readiness_lint': 4,
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def ordered_unique(values: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value not in seen:
            seen.add(value)
            out.append(value)
    return out


def item_sort_key(row: dict[str, Any]) -> tuple[int, str]:
    return (KIND_PRIORITY.get(row['item_kind'], 99), row['item_id'])


def collect() -> dict[str, Any]:
    inventory = load_json(ROOT / 'artifacts' / 'reports' / 'cooperation_benchmark_card_inventory.json')
    heads = load_json(ROOT / 'artifacts' / 'reports' / 'cooperation_benchmark_card_heads.json')
    review_queue = load_json(ROOT / 'artifacts' / 'reports' / 'cooperation_benchmark_card_review_queue.json')
    citation_surface = load_json(ROOT / 'artifacts' / 'reports' / 'cooperation_benchmark_card_citation_surface.json')
    schema = load_json(SCHEMA_PATH)
    jsonschema.Draft202012Validator.check_schema(schema)

    lineages_by_id = {row['lineage_id']: row for row in heads['lineages']}
    citation_ready_lineage_ids = {row['lineage_id'] for row in citation_surface['entries']}
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in review_queue['items']:
        lineage_id = row['lineage_id'] or row['card_id'] or row['item_id']
        grouped.setdefault(lineage_id, []).append(row)

    groups: list[dict[str, Any]] = []
    for lineage_id, rows in sorted(grouped.items()):
        rows = sorted(rows, key=item_sort_key)
        lineage = lineages_by_id.get(lineage_id)
        benchmark_names = lineage['benchmark_names'] if lineage else ['unknown-benchmark']
        operational_head = lineage['unique_operational_head_id'] if lineage else None
        citation_head = lineage['unique_citation_head_id'] if lineage else None
        review_commands = ordered_unique([row['review_command'] for row in rows])
        apply_commands = ordered_unique([row['apply_command'] for row in rows if row.get('apply_command')])
        groups.append(
            {
                'lineage_id': lineage_id,
                'benchmark_names': benchmark_names,
                'operational_head_card_id': operational_head,
                'citation_head_card_id': citation_head,
                'citation_ready': lineage_id in citation_ready_lineage_ids,
                'item_count': len(rows),
                'item_ids': [row['item_id'] for row in rows],
                'item_kinds': ordered_unique([row['item_kind'] for row in rows]),
                'reason_codes': sorted({code for row in rows for code in row['reason_codes']}),
                'primary_review_command': review_commands[0],
                'review_commands': review_commands,
                'apply_commands': apply_commands,
                'context_paths': sorted({path for row in rows for path in row['context_paths']}),
            }
        )

    data = {
        'queue_kind': 'cooperation_benchmark_card_macro_review_queue',
        'inventory_kind': inventory['card_inventory_kind'],
        'heads_register_kind': heads['register_kind'],
        'review_queue_kind': review_queue['queue_kind'],
        'citation_surface_kind': citation_surface['surface_kind'],
        'counts': {
            'lineage_count': len(heads['lineages']),
            'queued_lineage_count': len(groups),
            'total_item_count': review_queue['counts']['total_items'],
            'total_apply_command_count': sum(len(row['apply_commands']) for row in groups),
        },
        'groups': groups,
    }
    jsonschema.validate(data, schema)
    return data


def render(data: dict[str, Any]) -> str:
    counts = data['counts']
    lines = [
        TITLE,
        '',
        SUBTITLE,
        '',
        f"- lineage_count: {counts['lineage_count']}",
        f"- queued_lineage_count: {counts['queued_lineage_count']}",
        f"- total_item_count: {counts['total_item_count']}",
        f"- total_apply_command_count: {counts['total_apply_command_count']}",
        '',
    ]
    if not data['groups']:
        lines.extend(['No lineages currently have grouped compact-card review work.', ''])
        return '\n'.join(lines)

    lines.extend([
        '## Group summary',
        '',
        '| lineage_id | citation_ready | item_count | item_kinds | reason_codes | primary_review_command |',
        '|---|---:|---:|---|---|---|',
    ])
    for row in data['groups']:
        lines.append(
            f"| `{row['lineage_id']}` | {str(row['citation_ready']).lower()} | {row['item_count']} | "
            f"{', '.join('`' + value + '`' for value in row['item_kinds'])} | "
            f"{', '.join('`' + value + '`' for value in row['reason_codes'])} | `{row['primary_review_command']}` |"
        )
    lines.extend(['', '## Per-lineage groups', ''])
    for row in data['groups']:
        lines.append(f"### `{row['lineage_id']}`")
        lines.append('')
        lines.append(f"- benchmark_names: {', '.join('`' + value + '`' for value in row['benchmark_names'])}")
        lines.append(f"- operational_head_card_id: {('`' + row['operational_head_card_id'] + '`') if row['operational_head_card_id'] else 'none'}")
        lines.append(f"- citation_head_card_id: {('`' + row['citation_head_card_id'] + '`') if row['citation_head_card_id'] else 'none'}")
        lines.append(f"- citation_ready: {str(row['citation_ready']).lower()}")
        lines.append(f"- item_count: {row['item_count']}")
        lines.append(f"- item_ids: {', '.join('`' + value + '`' for value in row['item_ids'])}")
        lines.append(f"- item_kinds: {', '.join('`' + value + '`' for value in row['item_kinds'])}")
        lines.append(f"- reason_codes: {', '.join('`' + value + '`' for value in row['reason_codes'])}")
        lines.append(f"- primary_review_command: `{row['primary_review_command']}`")
        lines.append('- review_commands:')
        for command in row['review_commands']:
            lines.append(f"  - `{command}`")
        if row['apply_commands']:
            lines.append('- apply_commands:')
            for command in row['apply_commands']:
                lines.append(f"  - `{command}`")
        else:
            lines.append('- apply_commands: none')
        lines.append('- context_paths:')
        for path in row['context_paths']:
            lines.append(f"  - `{path}`")
        lines.append('')
    return '\n'.join(lines)


def main() -> int:
    write = '--write' in sys.argv
    data = collect()
    out_json = ROOT / 'artifacts' / 'reports' / 'cooperation_benchmark_card_macro_review_queue.json'
    out_md = ROOT / 'docs' / 'COOPERATION_BENCHMARK_CARD_MACRO_REVIEW_QUEUE.md'
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(data, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    expected_md = render(data) + '\n'
    if write or not out_md.exists():
        out_md.write_text(expected_md, encoding='utf-8')
        print(f'cooperation-benchmark-card-macro-review-queue: wrote {out_md}')
        print(f'cooperation-benchmark-card-macro-review-queue: wrote {out_json}')
        return 0
    current_md = out_md.read_text(encoding='utf-8')
    if current_md != expected_md:
        print('cooperation-benchmark-card-macro-review-queue: drift detected; run with --write', file=sys.stderr)
        return 1
    print(f"cooperation-benchmark-card-macro-review-queue: ok ({data['counts']['queued_lineage_count']} grouped lineages)")
    print(f'cooperation-benchmark-card-macro-review-queue: wrote {out_json}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
