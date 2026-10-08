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
SCHEMA_PATH = ROOT / 'schemas' / 'cooperation_benchmark_card_review_queue.schema.json'
inventory_builder = load_module('cooperation_benchmark_card_inventory_builder', INVENTORY_BUILDER)
heads_builder = load_module('cooperation_benchmark_card_heads_builder', HEADS_BUILDER)

TITLE = '# Cooperation Benchmark Card Review Queue'
SUBTITLE = (
    'Generated actionable queue over compact cooperation-card inventory, lineage heads, '
    'and retained freeze receipts.'
)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def freeze_output_paths(card_path: str) -> tuple[str, str]:
    path = Path(card_path)
    return (path.with_suffix('.md').as_posix(), path.with_suffix('.freeze_receipt.json').as_posix())




def compare_output_path(new_card_path: str) -> str:
    return Path(new_card_path).with_suffix('.delta_receipt.json').as_posix()


def compare_command(old_card_path: str, new_card_path: str) -> str:
    return (
        './grpy ./scripts/tools/cooperation_benchmark_card.py compare '
        f"{old_card_path} {new_card_path} --receipt-output {compare_output_path(new_card_path)}"
    )

def freeze_command(card_path: str) -> str:
    md_path, receipt_path = freeze_output_paths(card_path)
    return (
        './grpy ./scripts/tools/cooperation_benchmark_card.py freeze '
        f"{card_path} --require-current-operational-head --render-output {md_path} --receipt-output {receipt_path}"
    )


def freeze_drift_items(
    inventory: dict[str, Any],
    lineage_by_card_id: dict[str, str],
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    cards_by_id = {row['id']: row for row in inventory['cards']}
    for receipt in inventory['freeze_receipts']:
        reasons = receipt.get('drift_reason_codes', [])
        if not reasons:
            continue
        card = cards_by_id.get(receipt['card_id'])
        card_path = receipt['card_path']
        context_paths = [card_path, receipt['rendered_markdown_path'], receipt['path']]
        apply_command = None
        if card and card['claim_ready']:
            apply_command = freeze_command(card_path)
        out.append(
            {
                'item_id': f"freeze-drift-{receipt['card_id']}",
                'item_kind': 'freeze_drift',
                'reason_codes': reasons,
                'summary': 'Retained freeze receipt no longer matches its bound card and/or rendered markdown surface.',
                'review_command': f"./grpy ./scripts/tools/cooperation_benchmark_card.py render {card_path}",
                'apply_command': apply_command,
                'lineage_id': lineage_by_card_id.get(receipt['card_id']),
                'card_id': receipt['card_id'],
                'card_path': card_path,
                'context_paths': sorted(dict.fromkeys(context_paths)),
            }
        )
    return out




def delta_drift_items(
    inventory: dict[str, Any],
    lineage_by_card_id: dict[str, str],
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    cards_by_id = {row['id']: row for row in inventory['cards']}
    for receipt in inventory['delta_receipts']:
        reasons = receipt.get('drift_reason_codes', [])
        if not reasons:
            continue
        old_card = cards_by_id.get(receipt['old_card_id'])
        new_card = cards_by_id.get(receipt['new_card_id'])
        context_paths = [receipt['old_card_path'], receipt['new_card_path'], receipt['path']]
        apply_command = None
        if old_card and new_card and old_card['claim_ready'] and new_card['claim_ready']:
            apply_command = compare_command(receipt['old_card_path'], receipt['new_card_path'])
        out.append(
            {
                'item_id': f"delta-drift-{receipt['new_card_id']}",
                'item_kind': 'delta_drift',
                'reason_codes': reasons,
                'summary': 'Retained delta receipt no longer matches its bound predecessor and/or successor card surface.',
                'review_command': f"./grpy ./scripts/tools/cooperation_benchmark_card.py render {receipt['new_card_path']}",
                'apply_command': apply_command,
                'lineage_id': lineage_by_card_id.get(receipt['new_card_id']) or lineage_by_card_id.get(receipt['old_card_id']),
                'card_id': receipt['new_card_id'],
                'card_path': receipt['new_card_path'],
                'context_paths': sorted(dict.fromkeys(context_paths)),
            }
        )
    return out

def collect() -> dict[str, Any]:
    inventory = inventory_builder.collect()
    heads = heads_builder.collect()
    cards_by_id = {row['id']: row for row in inventory['cards']}
    lineage_by_card_id = {
        card_id: row['lineage_id']
        for row in heads['lineages']
        for card_id in row['card_ids']
    }
    items: list[dict[str, Any]] = []

    for card in inventory['cards']:
        if card['claim_ready']:
            continue
        items.append(
            {
                'item_id': f"readiness-lint-{card['id']}",
                'item_kind': 'readiness_lint',
                'reason_codes': ['claim-not-ready'],
                'summary': f"Card is schema-valid but still fails claim-readiness lint ({card['readiness_issue_count']} issue(s)).",
                'review_command': f"./grpy ./scripts/tools/cooperation_benchmark_card.py lint {card['path']}",
                'apply_command': None,
                'lineage_id': lineage_by_card_id.get(card['id'], card['id']),
                'card_id': card['id'],
                'card_path': card['path'],
                'context_paths': [card['path']],
            }
        )

    for row in heads['lineages']:
        if any(code in row.get('warning_reason_codes', []) for code in {'latest-operational-head-needs-freeze', 'latest-operational-head-freeze-drift'}):
            card_id = row['unique_operational_head_id']
            card = cards_by_id.get(card_id) if card_id else None
            if card is not None:
                summary = (
                    'Latest claim-ready operational head has only drifted freeze receipts and needs a fresh guarded freeze '
                    'before the lineage regains a unique citation head.'
                    if 'latest-operational-head-freeze-drift' in row.get('warning_reason_codes', [])
                    else 'Latest claim-ready operational head is not frozen yet, so the lineage lacks a unique citation head.'
                )
                items.append(
                    {
                        'item_id': f"freeze-needed-{row['lineage_id']}",
                        'item_kind': 'freeze_needed',
                        'reason_codes': [
                            code for code in row['warning_reason_codes']
                            if code in {'latest-operational-head-needs-freeze', 'latest-operational-head-freeze-drift'}
                        ],
                        'summary': summary,
                        'review_command': f"./grpy ./scripts/tools/cooperation_benchmark_card.py render {card['path']}",
                        'apply_command': freeze_command(card['path']),
                        'lineage_id': row['lineage_id'],
                        'card_id': card['id'],
                        'card_path': card['path'],
                        'context_paths': sorted(dict.fromkeys(row['card_paths'] + [card['path']])),
                    }
                )

        topology_codes = [
            code for code in row.get('warning_reason_codes', [])
            if code in {
                'multiple-roots',
                'branch-ambiguous',
                'no-claim-ready-operational-head',
                'multiple-operational-heads',
                'multiple-citation-heads',
            }
        ]
        if topology_codes:
            items.append(
                {
                    'item_id': f"topology-review-{row['lineage_id']}",
                    'item_kind': 'topology_review',
                    'reason_codes': topology_codes,
                    'summary': 'Lineage topology or head state blocks a straightforward citation / inheritance answer and needs review.',
                    'review_command': './grpy ./scripts/report/build_cooperation_benchmark_card_heads.py',
                    'apply_command': None,
                    'lineage_id': row['lineage_id'],
                    'card_id': row['unique_operational_head_id'],
                    'card_path': cards_by_id.get(row['unique_operational_head_id'], {}).get('path') if row['unique_operational_head_id'] else None,
                    'context_paths': row['card_paths'],
                }
            )

    items.extend(freeze_drift_items(inventory, lineage_by_card_id))
    items.extend(delta_drift_items(inventory, lineage_by_card_id))
    items.sort(key=lambda row: row['item_id'])
    data = {
        'queue_kind': 'cooperation_benchmark_card_review_queue',
        'inventory_kind': inventory['card_inventory_kind'],
        'heads_register_kind': heads['register_kind'],
        'counts': {
            'total_items': len(items),
            'freeze_needed_item_count': sum(1 for row in items if row['item_kind'] == 'freeze_needed'),
            'topology_review_item_count': sum(1 for row in items if row['item_kind'] == 'topology_review'),
            'readiness_lint_item_count': sum(1 for row in items if row['item_kind'] == 'readiness_lint'),
            'freeze_drift_item_count': sum(1 for row in items if row['item_kind'] == 'freeze_drift'),
            'delta_drift_item_count': sum(1 for row in items if row['item_kind'] == 'delta_drift'),
        },
        'items': items,
    }
    schema = load_json(SCHEMA_PATH)
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(data, schema)
    return data


def render(data: dict[str, Any]) -> str:
    counts = data['counts']
    lines = [
        TITLE,
        '',
        SUBTITLE,
        '',
        f"- total_items: {counts['total_items']}",
        f"- freeze_needed_item_count: {counts['freeze_needed_item_count']}",
        f"- topology_review_item_count: {counts['topology_review_item_count']}",
        f"- readiness_lint_item_count: {counts['readiness_lint_item_count']}",
        f"- freeze_drift_item_count: {counts['freeze_drift_item_count']}",
        f"- delta_drift_item_count: {counts['delta_drift_item_count']}",
        '',
    ]
    if not data['items']:
        lines.extend([
            'No actionable compact-card review items are currently queued.',
            '',
        ])
        return '\n'.join(lines)

    lines.extend([
        '## Queue items',
        '',
        '| item_id | item_kind | lineage_id | card_id | reason_codes | review_command | apply_command |',
        '|---|---|---|---|---|---|---|',
    ])
    for row in data['items']:
        lines.append(
            f"| `{row['item_id']}` | `{row['item_kind']}` | {('`' + row['lineage_id'] + '`') if row['lineage_id'] else '—'} | "
            f"{('`' + row['card_id'] + '`') if row['card_id'] else '—'} | {', '.join('`' + code + '`' for code in row['reason_codes'])} | "
            f"`{row['review_command']}` | {('`' + row['apply_command'] + '`') if row['apply_command'] else '—'} |"
        )
    lines.extend(['', '## Details', ''])
    for row in data['items']:
        lines.append(f"### `{row['item_id']}`")
        lines.append('')
        lines.append(f"- summary: {row['summary']}")
        lines.append(f"- reason_codes: {', '.join('`' + code + '`' for code in row['reason_codes'])}")
        lines.append(f"- review_command: `{row['review_command']}`")
        if row['apply_command']:
            lines.append(f"- apply_command: `{row['apply_command']}`")
        else:
            lines.append('- apply_command: none')
        if row['context_paths']:
            lines.append(f"- context_paths: {', '.join('`' + item + '`' for item in row['context_paths'])}")
        lines.append('')
    return '\n'.join(lines)


def main() -> int:
    write = '--write' in sys.argv
    data = collect()
    out_json = ROOT / 'artifacts' / 'reports' / 'cooperation_benchmark_card_review_queue.json'
    out_md = ROOT / 'docs' / 'COOPERATION_BENCHMARK_CARD_REVIEW_QUEUE.md'
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(data, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    expected_md = render(data) + '\n'
    if write or not out_md.exists():
        out_md.write_text(expected_md, encoding='utf-8')
        print(f'cooperation-benchmark-card-review-queue: wrote {out_md}')
        print(f'cooperation-benchmark-card-review-queue: wrote {out_json}')
        return 0
    current_md = out_md.read_text(encoding='utf-8')
    if current_md != expected_md:
        print('cooperation-benchmark-card-review-queue: drift detected; run with --write', file=sys.stderr)
        return 1
    print(f"cooperation-benchmark-card-review-queue: ok ({data['counts']['total_items']} items)")
    print(f'cooperation-benchmark-card-review-queue: wrote {out_json}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
