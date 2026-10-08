#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import sys
from collections import deque
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
SCHEMA_PATH = ROOT / 'schemas' / 'cooperation_benchmark_card_heads_register.schema.json'
inventory_builder = load_module('cooperation_benchmark_card_inventory_builder', INVENTORY_BUILDER)

TITLE = '# Cooperation Benchmark Card Heads Register'

WARNING_REASON_CODES = {
    'multiple roots; lineage head inference is less stable': 'multiple-roots',
    'multiple tips or branching successors; no single lineage tip by topology alone': 'branch-ambiguous',
    'no claim-ready operational head': 'no-claim-ready-operational-head',
    'multiple claim-ready operational heads': 'multiple-operational-heads',
    'latest claim-ready head is not frozen yet': 'latest-operational-head-needs-freeze',
    'latest claim-ready head has only drifted freeze receipts': 'latest-operational-head-freeze-drift',
    'multiple frozen claim-ready citation heads': 'multiple-citation-heads',
}


def warning_reason_codes(warnings: list[str]) -> list[str]:
    out: list[str] = []
    for warning in warnings:
        code = WARNING_REASON_CODES.get(warning)
        if code and code not in out:
            out.append(code)
    return out


SUBTITLE = (
    'Generated from the compact cooperation-card inventory to show lineage-scoped operational heads, '
    'citation heads, and branch / freeze warnings.'
)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def component_cards(cards: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
    by_id = {card['id']: card for card in cards}
    neighbors: dict[str, set[str]] = {card['id']: set() for card in cards}
    for card in cards:
        for other in card['predecessor_card_ids'] + card['successor_card_ids']:
            if other in by_id:
                neighbors[card['id']].add(other)
                neighbors[other].add(card['id'])
    seen: set[str] = set()
    components: list[list[dict[str, Any]]] = []
    for card_id in sorted(by_id):
        if card_id in seen:
            continue
        queue = deque([card_id])
        seen.add(card_id)
        ids: list[str] = []
        while queue:
            cur = queue.popleft()
            ids.append(cur)
            for nxt in sorted(neighbors[cur]):
                if nxt not in seen:
                    seen.add(nxt)
                    queue.append(nxt)
        components.append([by_id[i] for i in sorted(ids)])
    return components


def build_lineage(cards: list[dict[str, Any]]) -> dict[str, Any]:
    cards = sorted(cards, key=lambda c: c['id'])
    roots = sorted(card['id'] for card in cards if not card['predecessor_card_ids'])
    tips = sorted(card['id'] for card in cards if not card['successor_card_ids'])
    operational_heads = sorted(card['id'] for card in cards if card['claim_ready'] and card['latest_known'])
    citation_heads = sorted(card['id'] for card in cards if card['claim_ready'] and card['latest_known'] and card['frozen'])
    drifted_operational_heads = sorted(card['id'] for card in cards if card['claim_ready'] and card['latest_known'] and card.get('freeze_drift'))
    branch_ambiguous = len(tips) > 1 or any(len(card['successor_card_ids']) > 1 for card in cards)
    warnings: list[str] = []
    if len(roots) != 1:
        warnings.append('multiple roots; lineage head inference is less stable')
    if branch_ambiguous:
        warnings.append('multiple tips or branching successors; no single lineage tip by topology alone')
    if len(operational_heads) == 0:
        warnings.append('no claim-ready operational head')
    elif len(operational_heads) > 1:
        warnings.append('multiple claim-ready operational heads')
    if len(citation_heads) == 0 and len(operational_heads) >= 1:
        if drifted_operational_heads:
            warnings.append('latest claim-ready head has only drifted freeze receipts')
        else:
            warnings.append('latest claim-ready head is not frozen yet')
    elif len(citation_heads) > 1:
        warnings.append('multiple frozen claim-ready citation heads')
    lineage_id = roots[0] if roots else cards[0]['id']
    return {
        'lineage_id': lineage_id,
        'benchmark_names': sorted({card['benchmark_name'] for card in cards}),
        'card_ids': [card['id'] for card in cards],
        'card_paths': [card['path'] for card in cards],
        'root_card_ids': roots or [cards[0]['id']],
        'tip_card_ids': tips or [cards[-1]['id']],
        'operational_head_card_ids': operational_heads,
        'citation_head_card_ids': citation_heads,
        'drifted_operational_head_card_ids': drifted_operational_heads,
        'unique_operational_head_id': operational_heads[0] if len(operational_heads) == 1 else None,
        'unique_citation_head_id': citation_heads[0] if len(citation_heads) == 1 else None,
        'branch_ambiguous': branch_ambiguous,
        'warning_reason_codes': warning_reason_codes(sorted(set(warnings))),
        'warnings': sorted(set(warnings)),
    }


def collect() -> dict[str, Any]:
    inventory = inventory_builder.collect()
    cards = inventory['cards']
    lineages = [build_lineage(component) for component in component_cards(cards)]
    lineages.sort(key=lambda row: row['lineage_id'])
    data = {
        'register_kind': 'cooperation_benchmark_card_heads_register',
        'inventory_kind': inventory['card_inventory_kind'],
        'counts': {
            'lineage_count': len(lineages),
            'unique_operational_head_count': sum(1 for row in lineages if row['unique_operational_head_id']),
            'unique_citation_head_count': sum(1 for row in lineages if row['unique_citation_head_id']),
            'branch_ambiguous_lineage_count': sum(1 for row in lineages if row['branch_ambiguous']),
            'ambiguous_operational_head_lineage_count': sum(1 for row in lineages if len(row['operational_head_card_ids']) != 1),
            'lineages_needing_freeze_count': sum(
                1 for row in lineages if row['unique_operational_head_id'] and not row['unique_citation_head_id']
            ),
            'lineages_with_freeze_drift_count': sum(1 for row in lineages if row['drifted_operational_head_card_ids']),
        },
        'lineages': lineages,
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
        f"- lineage_count: {counts['lineage_count']}",
        f"- unique_operational_head_count: {counts['unique_operational_head_count']}",
        f"- unique_citation_head_count: {counts['unique_citation_head_count']}",
        f"- branch_ambiguous_lineage_count: {counts['branch_ambiguous_lineage_count']}",
        f"- ambiguous_operational_head_lineage_count: {counts['ambiguous_operational_head_lineage_count']}",
        f"- lineages_needing_freeze_count: {counts['lineages_needing_freeze_count']}",
        f"- lineages_with_freeze_drift_count: {counts['lineages_with_freeze_drift_count']}",
        '',
        '## Lineages',
        '',
        '| lineage_id | cards | tips | operational_head | citation_head | warning_codes | warnings |',
        '|---|---:|---|---|---|---|---|',
    ]
    for row in data['lineages']:
        tips = ', '.join(row['tip_card_ids']) or '—'
        operational = row['unique_operational_head_id'] or ('; '.join(row['operational_head_card_ids']) if row['operational_head_card_ids'] else '—')
        citation = row['unique_citation_head_id'] or ('; '.join(row['citation_head_card_ids']) if row['citation_head_card_ids'] else '—')
        warnings = '; '.join(row['warnings']) or '—'
        lines.append(
            f"| `{row['lineage_id']}` | {len(row['card_ids'])} | {tips} | {operational} | {citation} | {', '.join(row['warning_reason_codes']) or '—'} | {warnings} |"
        )
    lines.extend(['', '## Per-lineage details', ''])
    for row in data['lineages']:
        lines.append(f"### `{row['lineage_id']}`")
        lines.append('')
        lines.append(f"- benchmark_names: {', '.join('`' + name + '`' for name in row['benchmark_names'])}")
        lines.append(f"- card_ids: {', '.join('`' + card_id + '`' for card_id in row['card_ids'])}")
        lines.append(f"- root_card_ids: {', '.join('`' + card_id + '`' for card_id in row['root_card_ids'])}")
        lines.append(f"- tip_card_ids: {', '.join('`' + card_id + '`' for card_id in row['tip_card_ids'])}")
        if row['unique_operational_head_id']:
            lines.append(f"- unique_operational_head_id: `{row['unique_operational_head_id']}`")
        else:
            lines.append('- unique_operational_head_id: none')
        if row['unique_citation_head_id']:
            lines.append(f"- unique_citation_head_id: `{row['unique_citation_head_id']}`")
        else:
            lines.append('- unique_citation_head_id: none')
        if row['drifted_operational_head_card_ids']:
            lines.append(
                f"- drifted_operational_head_card_ids: {', '.join('`' + card_id + '`' for card_id in row['drifted_operational_head_card_ids'])}"
            )
        if row['warning_reason_codes']:
            lines.append(f"- warning_reason_codes: {', '.join('`' + code + '`' for code in row['warning_reason_codes'])}")
        if row['warnings']:
            lines.append('- warnings:')
            for warning in row['warnings']:
                lines.append(f'  - {warning}')
        else:
            lines.append('- warnings: none')
        lines.append('')
    return '\n'.join(lines)


def main() -> int:
    write = '--write' in sys.argv
    data = collect()
    out_json = ROOT / 'artifacts' / 'reports' / 'cooperation_benchmark_card_heads.json'
    out_md = ROOT / 'docs' / 'COOPERATION_BENCHMARK_CARD_HEADS.md'
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(data, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    expected_md = render(data) + '\n'
    if write or not out_md.exists():
        out_md.write_text(expected_md, encoding='utf-8')
        print(f'cooperation-benchmark-card-heads: wrote {out_md}')
        print(f'cooperation-benchmark-card-heads: wrote {out_json}')
        return 0
    current_md = out_md.read_text(encoding='utf-8')
    if current_md != expected_md:
        print('cooperation-benchmark-card-heads: drift detected; run with --write', file=sys.stderr)
        return 1
    print(f"cooperation-benchmark-card-heads: ok ({data['counts']['lineage_count']} lineages)")
    print(f'cooperation-benchmark-card-heads: wrote {out_json}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
